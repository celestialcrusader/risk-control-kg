"""
Live Script: Execute Production NLI Semantic Evaluation across MAS TRM <-> NIST SP 800-53.

1. Fetches candidate pairs from PostgreSQL & Memgraph.
2. Runs NliBatchCrosswalkEvaluator on each pair to compute calibrated set-theory relation and confidence.
3. Updates PostgreSQL obligation_framework_mappings and Memgraph :CROSSWALKS_TO edges.
4. Outputs the final high-confidence crosswalk report.
"""

import os
import sys
import logging
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from app.core.database import SessionLocal
from app.core.memgraph import get_memgraph_driver
from app.models.rckg_nodes import (
    ObligationNode,
    FrameworkControlObjectiveNode,
    ObligationFrameworkMapping,
    SetTheoryRelation,
    MappingStatus,
)
from app.services.nli_evaluator import NliBatchCrosswalkEvaluator


def main():
    logger.info("=================================================================")
    logger.info("  STARTING PRODUCTION NLI EVALUATION (MAS TRM <-> NIST 800-53)   ")
    logger.info("=================================================================")

    session = SessionLocal()
    mem_driver = get_memgraph_driver()
    evaluator = NliBatchCrosswalkEvaluator()

    try:
        obligations = session.query(ObligationNode).all()
        nist_controls = session.query(FrameworkControlObjectiveNode).all()

        logger.info("Evaluating %d MAS TRM obligations against %d NIST controls...", len(obligations), len(nist_controls))

        evaluated_count = 0
        updated_crosswalks = []

        from concurrent.futures import ThreadPoolExecutor, as_completed

        def evaluate_single_obligation(obl):
            obl_text = (obl.statement_text or "").strip()
            if not obl_text:
                return None

            obl_lower = obl_text.lower()
            obl_tokens = set(obl_lower.split())

            scored_candidates = []
            for nist in nist_controls:
                nist_text = (nist.objective_text or "") + " " + (nist.objective_name or "")
                nist_lower = nist_text.lower()
                nist_tokens = set(nist_lower.split())
                
                shared_domains = 0
                for domain, kws in evaluator.SEMANTIC_KEYWORDS.items():
                    if any(k in obl_lower for k in kws) and any(k in nist_lower for k in kws):
                        shared_domains += 1

                overlap = len(obl_tokens & nist_tokens)
                if shared_domains > 0 or overlap >= 3:
                    score = (shared_domains * 3.0) + overlap
                    scored_candidates.append((score, nist, nist_text))

            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            top_candidates = scored_candidates[:3]

            best_match = None
            best_eval = None

            for score, nist, nist_text in top_candidates:
                res = evaluator.evaluate_pair(obl_text, nist_text)
                if res.relation != "NO_RELATIONSHIP" and res.confidence >= 0.70:
                    if best_eval is None or res.confidence > best_eval.confidence:
                        best_eval = res
                        best_match = nist

            if best_match and best_eval:
                return (obl, best_match, best_eval)
            return None

        # Execute in parallel across 16 threads
        logger.info("Executing concurrent NLI evaluations with 16 parallel workers...")
        evaluated_pairs = []
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(evaluate_single_obligation, obl) for obl in obligations]
            for f in as_completed(futures):
                res = f.result()
                if res:
                    evaluated_pairs.append(res)

        logger.info("Parallel evaluation finished. Updating DB with %d crosswalks...", len(evaluated_pairs))

        for obl, best_match, best_eval in evaluated_pairs:
            rel_enum = SetTheoryRelation[best_eval.relation] if best_eval.relation in SetTheoryRelation.__members__ else SetTheoryRelation.SUPERSET_OF

            mapping = session.query(ObligationFrameworkMapping).filter_by(
                obligation_id=obl.id, framework_objective_id=best_match.id
            ).first()

            if not mapping:
                mapping = ObligationFrameworkMapping(
                    id=uuid4(),
                    obligation_id=obl.id,
                    framework_objective_id=best_match.id,
                    set_theory_relation=rel_enum,
                    confidence_score=str(best_eval.confidence),
                    status=MappingStatus.PROBABILISTIC_AI,
                    rationale=best_eval.rationale,
                )
                session.add(mapping)
            else:
                mapping.set_theory_relation = rel_enum
                mapping.confidence_score = str(best_eval.confidence)
                mapping.rationale = best_eval.rationale

            if mem_driver:
                with mem_driver.session() as mem_sess:
                    mem_sess.run(
                        """
                        MATCH (o:Obligation {obligation_id: $obl_id})
                        MATCH (f:FrameworkControlObj {framework_obj_id: $nist_id})
                        MERGE (o)-[r:CROSSWALKS_TO]->(f)
                        SET r.set_theory_relation = $rel,
                            r.confidence_score = $conf,
                            r.status = 'PROBABILISTIC_AI',
                            r.rationale = $rat,
                            r.updated_at = timestamp()
                        """,
                        {
                            "obl_id": obl.obligation_id,
                            "nist_id": best_match.framework_obj_id,
                            "rel": best_eval.relation,
                            "conf": str(best_eval.confidence),
                            "rat": best_eval.rationale,
                        }
                    )

            updated_crosswalks.append({
                "mas_id": obl.obligation_id,
                "nist_id": best_match.framework_obj_id,
                "nist_name": best_match.objective_name,
                "relation": best_eval.relation,
                "confidence": best_eval.confidence,
                "rationale": best_eval.rationale,
            })


        session.commit()
        logger.info("Successfully committed %d high-confidence NLI crosswalks.", evaluated_count)

        # Print Final Results Table
        print("\n" + "=" * 115)
        print("  PRODUCTION AI NLI CROSSWALK EVALUATION RESULTS (MAS TRM 2021 <──> NIST SP 800-53 Rev 5)")
        print("=" * 115)
        print(f"Total MAS Obligations Evaluated : {len(obligations)}")
        print(f"High-Confidence Linkages Formed : {len(updated_crosswalks)}")
        print("-" * 115)
        print(f"{'MAS Clause ID':<16} | {'NIST Control ID':<16} | {'Set Theory Relation':<18} | {'Conf':<6} | {'NIST Control Name'}")
        print("-" * 115)

        for cw in sorted(updated_crosswalks, key=lambda x: x["confidence"], reverse=True)[:30]:
            print(f"{cw['mas_id']:<16} | {cw['nist_id']:<16} | {cw['relation']:<18} | {cw['confidence']:<6.2f} | {cw['nist_name']}")

        print("=" * 115 + "\n")

    except Exception as e:
        logger.exception("NLI evaluation failed: %s", e)
    finally:
        session.close()
        if mem_driver:
            mem_driver.close()


if __name__ == "__main__":
    main()
