from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.database import Database

router = APIRouter()

class UpdateDraftRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

def get_db():
    db = Database()
    db.connect()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_pending_approvals(db: Database = Depends(get_db)):
    """
    Get all elements (Nodes/Relationships) with status='DRAFT'.
    """
    pending = []
    
    # 1. Draft Nodes
    query_nodes = """
    MATCH (n)
    WHERE n.status = 'DRAFT'
    OPTIONAL MATCH (n)-[:MENTIONED_IN]->(r:Requirement)
    RETURN elementId(n) as eid, properties(n) as props, labels(n) as labels, r.title as source_title
    LIMIT 50
    """
    node_results = db.execute_read(query_nodes)
    for row in node_results:
        pending.append({
            "type": "node",
            "id": row['eid'],
            "labels": row['labels'],
            "properties": row['props'],
            "source": row['source_title']
        })

    # 2. Draft Relationships
    query_rels = """
    MATCH (s)-[r]->(t)
    WHERE r.status = 'DRAFT'
    RETURN elementId(r) as eid, properties(r) as props, type(r) as rel_type, 
           elementId(s) as source_id, labels(s) as source_labels, properties(s).title as source_title,
           elementId(t) as target_id, labels(t) as target_labels, properties(t).title as target_title
    LIMIT 50
    """
    rel_results = db.execute_read(query_rels)
    for row in rel_results:
        # Build a descriptive label like "AWS Control -> CCM Control"
        s_lbl = row['source_labels'][0] if row['source_labels'] else "Node"
        t_lbl = row['target_labels'][0] if row['target_labels'] else "Node"
        s_title = row['source_title'] or "Unknown Source"
        t_title = row['target_title'] or "Unknown Target"
        
        pending.append({
            "type": "relationship",
            "id": row['eid'],
            "relationship_type": row['rel_type'],
            "properties": row['props'],
            "description": f"{s_lbl} ({s_title}) --[{row['rel_type']}]--> {t_lbl} ({t_title})",
            "source": "AI Mapping"
        })
        
    return pending

@router.post("/{element_id}/approve")
def approve_draft(element_id: str, db: Database = Depends(get_db)):
    """
    Approve: Set status='APPROVED'. Works for Nodes and Relationships.
    """
    # Try updating Node first
    query_node = """
    MATCH (n) WHERE elementId(n) = $eid
    SET n.status = 'APPROVED'
    RETURN count(n) as c
    """
    res_node = db.execute_write(query_node, {"eid": element_id})
    if res_node[0]['c'] > 0:
        return {"status": "success", "id": element_id, "type": "node"}
        
    # Try updating Relationship
    query_rel = """
    MATCH ()-[r]->() WHERE elementId(r) = $eid
    SET r.status = 'APPROVED'
    RETURN count(r) as c
    """
    res_rel = db.execute_write(query_rel, {"eid": element_id})
    if res_rel[0]['c'] > 0:
        return {"status": "success", "id": element_id, "type": "relationship"}

    raise HTTPException(status_code=404, detail="Element not found")

@router.post("/{element_id}/reject")
def reject_draft(element_id: str, db: Database = Depends(get_db)):
    """
    Reject: Delete element.
    """
    # Try Node
    query_node = """
    MATCH (n) WHERE elementId(n) = $eid
    DETACH DELETE n
    RETURN count(n) as c
    """
    # NOTE: In generic execute_write, catching 'count' from DELETE might need RETURN.
    # We use a trick: Optional Match + Delete? No, straight delete.
    # Actually, we can check existence first or just run both deletes.
    # Safer to run both if we don't know type, but ID is unique across space? 
    # Actually Neo4j Element IDs are unique.
    
    # Try Node Delete
    res_node = db.execute_write(query_node, {"eid": element_id})
    
    # Try Rel Delete
    query_rel = """
    MATCH ()-[r]->() WHERE elementId(r) = $eid
    DELETE r
    """
    res_rel = db.execute_write(query_rel, {"eid": element_id})
    
    return {"status": "success", "id": element_id}

@router.put("/{element_id}")
def update_draft(element_id: str, payload: UpdateDraftRequest, db: Database = Depends(get_db)):
    """
    Update properties or status.
    """
    updates = []
    params = {"eid": element_id}
    
    if payload.name:
        updates.append("n.name = $name")
        params["name"] = payload.name
    if payload.description:
        updates.append("n.description = $desc")
        params["desc"] = payload.description
    if payload.status:
        updates.append("n.status = $status")
        params["status"] = payload.status
        
    if not updates:
        return {"status": "no_change"}
        
    set_clause = "SET " + ", ".join(updates)
    
    query = f"""
    MATCH (n)
    WHERE elementId(n) = $eid
    {set_clause}
    RETURN n
    """
    
    db.execute_write(query, params, action="UPDATE_DRAFT")
    
    return {"status": "success", "updates": updates}
