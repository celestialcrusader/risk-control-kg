import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app.core.database import SessionLocal
from app.models.rckg_nodes import ObligationNode, ObligationFrameworkMapping

db = SessionLocal()
all_obls = db.query(ObligationNode).all()
mapped_obl_ids = set(m[0] for m in db.query(ObligationFrameworkMapping.obligation_id).distinct().all())

mapped = [o for o in all_obls if o.id in mapped_obl_ids]
unmapped = [o for o in all_obls if o.id not in mapped_obl_ids]

out_data = {
    "total_obligations": len(all_obls),
    "mapped_count": len(mapped),
    "unmapped_count": len(unmapped),
    "unmapped_obligations": [
        {
            "id": o.obligation_id,
            "statement_text": (o.statement_text or "").strip(),
            "framework": o.framework_name,
            "action_verb": o.action_verb or "",
        }
        for o in unmapped
    ]
}

out_path = Path(__file__).resolve().parent.parent / "scripts" / "unmapped_obligations.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out_data, f, indent=2)

print(f"Total: {len(all_obls)} | Mapped: {len(mapped)} | Unmapped: {len(unmapped)}")
print(f"Written unmapped obligations to {out_path}")
db.close()
