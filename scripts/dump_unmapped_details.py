import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app.core.database import SessionLocal
from app.models.rckg_nodes import ObligationNode, FrameworkControlObjectiveNode

db = SessionLocal()

pairs_to_check = [
    ("MAS-1.4(b).1", "NIST-SA-24"),
    ("MAS-6.5.1", "NIST-CM-8"),
    ("MAS-6.5.3.c", "NIST-CM-3"),
    ("MAS-6.5.3.d", "NIST-SA-11"),
    ("MAS-7.3.1.b", "NIST-SA-22"),
    ("MAS-7.6.1", "NIST-AC-5"),
    ("MAS-7.6.2", "NIST-SI-7"),
    ("MAS-13.5.2.b", "NIST-RA-3"),
    ("MAS-13.6.1.b", "NIST-SI-2"),
    ("MAS-14.1.6.a", "NIST-SI-4"),
    ("MAS-14.3.2", "NIST-IR-4"),
    ("MAS-14.3.3.a", "NIST-SI-4"),
    ("MAS-14.4.2", "NIST-SI-5"),
]

detailed_results = []

for mas_id, nist_id in pairs_to_check:
    mas_node = db.query(ObligationNode).filter_by(obligation_id=mas_id).first()
    nist_node = db.query(FrameworkControlObjectiveNode).filter_by(framework_obj_id=nist_id).first()

    detailed_results.append({
        "mas_id": mas_id,
        "mas_text": mas_node.statement_text.strip() if mas_node and mas_node.statement_text else "N/A",
        "nist_id": nist_id,
        "nist_title": nist_node.objective_name.strip() if nist_node and nist_node.objective_name else "N/A",
        "nist_text": nist_node.objective_text.strip() if nist_node and nist_node.objective_text else "N/A"
    })

out_path = Path(__file__).resolve().parent.parent / "scripts" / "unmapped_detailed_nist.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(detailed_results, f, indent=2)

print(f"Dumped {len(detailed_results)} pairs with full NIST wording to {out_path}")
db.close()
