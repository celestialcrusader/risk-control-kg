import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app.core.database import SessionLocal
from app.models.rckg_nodes import ObligationFrameworkMapping, ObligationNode, FrameworkControlObjectiveNode

db = SessionLocal()
results = (
    db.query(ObligationFrameworkMapping, ObligationNode, FrameworkControlObjectiveNode)
    .join(ObligationNode, ObligationFrameworkMapping.obligation_id == ObligationNode.id)
    .join(FrameworkControlObjectiveNode, ObligationFrameworkMapping.framework_objective_id == FrameworkControlObjectiveNode.id)
    .all()
)

# Pick 25 items across the list
step = max(len(results) // 25, 1)
samples = [results[i] for i in range(0, len(results), step)][:25]

data = []
for idx, (m, o, f) in enumerate(samples, 1):
    data.append({
        'index': idx,
        'mas_id': o.obligation_id,
        'mas_text': o.statement_text.strip() if o.statement_text else '',
        'nist_id': f.framework_obj_id,
        'nist_title': f.objective_name.strip() if f.objective_name else '',
        'nist_text': f.objective_text.strip() if f.objective_text else '',
        'relation': m.set_theory_relation.value,
        'confidence': float(m.confidence_score),
        'rationale': m.rationale
    })

out_path = Path(__file__).resolve().parent.parent / "scripts" / "sample_pairs.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Dumped {len(data)} sample pairs to {out_path}")
db.close()
