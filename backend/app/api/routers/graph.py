from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
import json
from neo4j.time import DateTime, Date, Time

from app.core.database import Database

router = APIRouter()

def serialize_neo4j_values(data: Any) -> Any:
    if isinstance(data, (DateTime, Date, Time)):
        return data.isoformat()
    if isinstance(data, dict):
        return {k: serialize_neo4j_values(v) for k, v in data.items()}
    if isinstance(data, list):
        return [serialize_neo4j_values(item) for item in data]
    return data

def get_db():
    db = Database()
    db.connect()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_graph(limit: int = 1000, label: str = None, db: Database = Depends(get_db)) -> Dict[str, List[Any]]:
    """
    Returns graph data in Cytoscape.js format.
    Optional 'label' query param filters by node label.
    """
    nodes = []
    edges = []
    
    label_filter = f":{label}" if label else ""
    
    # 1. Fetch Nodes
    # Query: MATCH (n) RETURN n.id as id, labels(n) as labels, properties(n) as props
    node_query = f"""
    MATCH (n{label_filter})
    RETURN n.id as id, labels(n) as labels, properties(n) as props
    LIMIT {limit}
    """
    node_results = db.execute_read(node_query)
    
    seen_ids = set()
    
    for row in node_results:
        nid = row.get('id')
        if not nid: 
            # Fallback to internal ID if we could get it, but we didn't select it.
            continue
            
        if nid in seen_ids:
            continue
        seen_ids.add(nid)
            
        labels = row.get('labels', [])
        # Serialize props to handle DateTime
        props = serialize_neo4j_values(row.get('props', {}))
        
        # Format for Cytoscape
        # Use first label as main class
        main_label = labels[0] if labels else "Unknown"
        
        # Use name or title as label
        display_name = props.get('title') or props.get('name') or props.get('description', '')[:20] or nid
        
        nodes.append({
            "data": {
                "id": nid,
                "label": display_name,
                "type": main_label,
                **props
            }
        })
        
    # 2. Fetch Edges
    edge_query = f"""
    MATCH (n{label_filter})-[r]->(m)
    WHERE n.id IS NOT NULL AND m.id IS NOT NULL
    RETURN n.id as source, m.id as target, type(r) as type, elementId(r) as eid, properties(r) as props
    LIMIT {limit}
    """
    
    edge_results = db.execute_read(edge_query)
    
    for row in edge_results:
        source = row['source']
        target = row['target']
        
        # Only include edges if both nodes were fetched (prevents Cytoscape crash)
        if source not in seen_ids or target not in seen_ids:
            continue
        
        edges.append({
            "data": {
                "id": row.get('eid', f"{source}-{target}"),
                "source": source,
                "target": target,
                "label": row['type'],
                **serialize_neo4j_values(row.get('props', {}))
            }
        })

    return {
        "nodes": nodes,
        "edges": edges
    }
