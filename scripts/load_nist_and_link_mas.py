"""
Live Script: Ingest NIST SP 800-53 Rev 5 OSCAL YAML and Compute MAS TRM Linkages.

1. Ingests NIST SP 800-53 controls and enhancements into PostgreSQL and Memgraph.
2. Synchronizes MAS TRM obligations into ObligationNode.
3. Computes set-theory semantic crosswalks between MAS TRM and NIST SP 800-53.
4. Stores linkages in PostgreSQL obligation_framework_mappings and Memgraph :CROSSWALKS_TO edges.
5. Prints a detailed audit summary and crosswalk table.
"""

import os
import sys
import logging
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv

# Setup paths and environment
APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from app.core.database import SessionLocal, engine
from app.core.memgraph import get_memgraph_driver
from app.models.rckg_nodes import (
    Base,
    FrameworkControlObjectiveNode,
    FrameworkControlActivityNode,
    ObligationNode,
    ObligationFrameworkMapping,
    SetTheoryRelation,
    MappingStatus,
)
from app.models import SemanticControl
from app.services.parsers.oscal_parser import OscalYamlCatalogParser
from app.services.facet_extractor import DeJureFacetExtractor


def load_nist_oscal_catalog(session, mem_driver, yaml_path: str):
    """Load NIST SP 800-53 from OSCAL YAML into PostgreSQL and Memgraph."""
    logger.info("=== STEP 1: Ingesting NIST SP 800-53 Rev 5 OSCAL YAML ===")
    parser = OscalYamlCatalogParser(yaml_path)
    parsed = parser.parse()

    objectives = parsed["objectives"]
    activities = parsed["activities"]
    edges = parsed["edges"]

    # 1. PostgreSQL Batch Merge
    logger.info("Saving %d Objectives and %d Activities to PostgreSQL...", len(objectives), len(activities))
    obj_db_map = {}
    for obj in objectives:
        existing = session.query(FrameworkControlObjectiveNode).filter_by(framework_obj_id=obj["framework_obj_id"]).first()
        if not existing:
            existing = FrameworkControlObjectiveNode(
                id=uuid4(),
                framework_obj_id=obj["framework_obj_id"],
                framework_name=obj["framework_name"],
                framework_version=obj["framework_version"],
                objective_name=obj["objective_name"],
                objective_text=obj["objective_text"],
            )
            session.add(existing)
        else:
            existing.objective_name = obj["objective_name"]
            existing.objective_text = obj["objective_text"]
        obj_db_map[obj["framework_obj_id"]] = existing

    session.flush()

    for act in activities:
        existing_act = session.query(FrameworkControlActivityNode).filter_by(framework_act_id=act["framework_act_id"]).first()
        if not existing_act:
            existing_act = FrameworkControlActivityNode(
                id=uuid4(),
                framework_act_id=act["framework_act_id"],
                framework_name=act["framework_name"],
                framework_version=act["framework_version"],
                activity_name=act["activity_name"],
                activity_text=act["activity_text"],
            )
            session.add(existing_act)
        else:
            existing_act.activity_name = act["activity_name"]
            existing_act.activity_text = act["activity_text"]

    session.commit()
    logger.info("PostgreSQL commit complete for NIST controls.")

    # 2. Memgraph Batch Injection
    if mem_driver:
        logger.info("Injecting NIST nodes and REFINES edges into Memgraph...")
        with mem_driver.session() as mem_sess:
            # Batch merge objectives
            for obj in objectives:
                mem_sess.run(
                    """
                    MERGE (fco:FrameworkControlObj {framework_obj_id: $id})
                    SET fco.framework_name = $fw_name,
                        fco.framework_version = $fw_version,
                        fco.objective_name = $name,
                        fco.objective_text = $text,
                        fco.node_status = 'RESOLVED'
                    """,
                    {
                        "id": obj["framework_obj_id"],
                        "fw_name": obj["framework_name"],
                        "fw_version": obj["framework_version"],
                        "name": obj["objective_name"],
                        "text": obj["objective_text"][:500],
                    }
                )

            # Batch merge activities
            for act in activities:
                mem_sess.run(
                    """
                    MERGE (fca:FrameworkControlAct {framework_act_id: $id})
                    SET fca.framework_name = $fw_name,
                        fca.framework_version = $fw_version,
                        fca.activity_name = $name,
                        fca.activity_text = $text,
                        fca.node_status = 'RESOLVED'
                    """,
                    {
                        "id": act["framework_act_id"],
                        "fw_name": act["framework_name"],
                        "fw_version": act["framework_version"],
                        "name": act["activity_name"],
                        "text": act["activity_text"][:500],
                    }
                )

            # Batch merge hierarchy edges
            for e in edges:
                mem_sess.run(
                    """
                    MATCH (p:FrameworkControlObj {framework_obj_id: $src})
                    MATCH (c:FrameworkControlAct {framework_act_id: $tgt})
                    MERGE (p)-[r:REFINES]->(c)
                    """,
                    {"src": e["source_id"], "tgt": e["target_id"]}
                )
        logger.info("Memgraph injection complete for NIST controls.")

    return objectives, activities


def sync_mas_trm_obligations(session, mem_driver):
    """Sync MAS TRM clauses from semantic_controls into ObligationNode & Memgraph."""
    logger.info("=== STEP 2: Synchronizing MAS TRM Obligations ===")
    sem_controls = session.query(SemanticControl).all()
    logger.info("Found %d MAS TRM semantic controls in PostgreSQL.", len(sem_controls))

    obligations = []
    for sc in sem_controls:
        obl_id = f"MAS-{sc.control_id}" if not sc.control_id.startswith("MAS-") else sc.control_id
        existing = session.query(ObligationNode).filter_by(obligation_id=obl_id).first()
        if not existing:
            existing = ObligationNode(
                id=uuid4(),
                obligation_id=obl_id,
                framework_name="MAS TRM",
                framework_version="2021",
                statement_text=sc.statement_text or sc.objective_text or "",
                action_verb=sc.action_verb or "enforce",
                subject_noun=sc.subject_noun or "Financial Institution",
                section_reference=sc.section_reference or "General",
                source_document_id=sc.source_document_id,
            )
            session.add(existing)
        obligations.append(existing)

    session.commit()
    logger.info("Synchronized %d MAS TRM ObligationNodes in PostgreSQL.", len(obligations))

    if mem_driver:
        with mem_driver.session() as mem_sess:
            for obl in obligations:
                mem_sess.run(
                    """
                    MERGE (o:Obligation {obligation_id: $id})
                    SET o.framework_name = $fw,
                        o.framework_version = $ver,
                        o.statement_text = $text,
                        o.action_verb = $verb,
                        o.subject_noun = $noun,
                        o.section_reference = $sec
                    """,
                    {
                        "id": obl.obligation_id,
                        "fw": obl.framework_name,
                        "ver": obl.framework_version,
                        "text": (obl.statement_text or "")[:500],
                        "verb": obl.action_verb,
                        "noun": obl.subject_noun,
                        "sec": obl.section_reference,
                    }
                )
        logger.info("Synchronized MAS TRM Obligations into Memgraph.")

    return obligations


def compute_and_store_crosswalks(session, mem_driver, obligations, nist_objectives):
    """Compute semantic set-theory crosswalks between MAS TRM and NIST SP 800-53."""
    logger.info("=== STEP 3: Computing Semantic Crosswalks (MAS TRM <-> NIST 800-53) ===")

    # Pre-extract NIST keywords and tokens for candidate pairing
    nist_nodes = session.query(FrameworkControlObjectiveNode).all()
    logger.info("Loaded %d NIST Framework Control Objectives for candidate pairing.", len(nist_nodes))

    crosswalk_results = []
    created_count = 0

    shared_keywords = {
        "access", "mfa", "authentication", "encryption", "audit", "log", "logging",
        "incident", "vulnerability", "backup", "credential", "session", "privilege",
        "privilege", "security", "patch", "network", "firewall", "wireless", "cloud",
        "vendor", "third-party", "risk", "governance", "monitoring", "training", "dr",
        "disaster", "recovery", "key", "cryptographic", "cryptography", "identity",
    }

    for idx, obl in enumerate(obligations, 1):
        obl_text = (obl.statement_text or "").lower()
        obl_tokens = set(obl_text.split())

        best_match = None
        best_score = 0.0
        best_relation = SetTheoryRelation.SUPERSET_OF

        for nist in nist_nodes:
            nist_text = (nist.objective_text or "" + " " + nist.objective_name).lower()
            nist_tokens = set(nist_text.split())
            if not nist_tokens:
                continue

            # Calculate token overlap & domain affinity
            intersection = obl_tokens & nist_tokens
            overlap = len(intersection) / max(len(obl_tokens | nist_tokens), 1)
            
            # Domain / Topic keyword affinity boost
            matching_keywords = intersection & shared_keywords
            keyword_bonus = len(matching_keywords) * 0.12

            sim_score = min(0.98, round(overlap * 2.8 + keyword_bonus, 2))

            if sim_score > best_score and sim_score >= 0.25:
                best_score = sim_score
                best_match = nist
                
                # Determine Set Theory Relation
                if sim_score >= 0.75:
                    best_relation = SetTheoryRelation.EQUIVALENT_TO
                elif sim_score >= 0.50:
                    best_relation = SetTheoryRelation.SUPERSET_OF
                elif sim_score >= 0.35:
                    best_relation = SetTheoryRelation.SUBSET_OF
                else:
                    best_relation = SetTheoryRelation.INTERSECTS_WITH


        if best_match:
            # Check or create mapping in PostgreSQL
            mapping = session.query(ObligationFrameworkMapping).filter_by(
                obligation_id=obl.id, framework_objective_id=best_match.id
            ).first()
            if not mapping:
                mapping = ObligationFrameworkMapping(
                    id=uuid4(),
                    obligation_id=obl.id,
                    framework_objective_id=best_match.id,
                    set_theory_relation=best_relation,
                    confidence_score=str(best_score),
                    status=MappingStatus.PROBABILISTIC_AI,
                    rationale=f"Semantic match between {obl.obligation_id} and {best_match.framework_obj_id} (sim={best_score})",
                )
                session.add(mapping)
                created_count += 1

            crosswalk_results.append({
                "mas_id": obl.obligation_id,
                "mas_text": obl_text[:75] + ("..." if len(obl_text) > 75 else ""),
                "nist_id": best_match.framework_obj_id,
                "nist_name": best_match.objective_name,
                "relation": best_relation.value,
                "confidence": best_score,
            })

            # Create Memgraph Edge
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
                            r.updated_at = timestamp()
                        """,
                        {
                            "obl_id": obl.obligation_id,
                            "nist_id": best_match.framework_obj_id,
                            "rel": best_relation.value,
                            "conf": str(best_score),
                        }
                    )

    session.commit()
    logger.info("Saved %d Crosswalk Linkages in PostgreSQL and Memgraph.", created_count)
    return crosswalk_results


def main():
    logger.info("================================================================")
    logger.info("  STARTING NIST SP 800-53 INGESTION & MAS TRM CROSSWALK PIPELINE ")
    logger.info("================================================================")

    yaml_path = "data/test-docs/NIST_SP-800-53_rev5_catalog.yaml"
    if not os.path.exists(yaml_path):
        logger.error("OSCAL YAML not found at %s", yaml_path)
        return

    # Ensure tables exist
    Base.metadata.create_all(engine)

    session = SessionLocal()
    mem_driver = get_memgraph_driver()

    try:
        # Step 1: Ingest NIST OSCAL YAML
        nist_objs, nist_acts = load_nist_oscal_catalog(session, mem_driver, yaml_path)

        # Step 2: Synchronize MAS TRM Obligations
        mas_obls = sync_mas_trm_obligations(session, mem_driver)

        # Step 3: Compute & Store Crosswalk Linkages
        crosswalks = compute_and_store_crosswalks(session, mem_driver, mas_obls, nist_objs)

        # Step 4: Display Results Summary
        print("\n" + "=" * 105)
        print(f"  CROSSWALK RESULTS: MAS TRM (2021) <──[CROSSWALKS_TO]──> NIST SP 800-53 (Rev 5)")
        print("=" * 105)
        print(f"Total NIST Objectives Loaded : {len(nist_objs)}")
        print(f"Total NIST Activities Loaded : {len(nist_acts)}")
        print(f"Total MAS Obligations Linked : {len(crosswalks)} / {len(mas_obls)}")
        print("-" * 105)
        print(f"{'MAS Clause ID':<16} | {'NIST Control ID':<16} | {'Set Theory Relation':<18} | {'Conf':<6} | {'NIST Control Name'}")
        print("-" * 105)

        for cw in crosswalks[:25]:
            print(f"{cw['mas_id']:<16} | {cw['nist_id']:<16} | {cw['relation']:<18} | {cw['confidence']:<6.2f} | {cw['nist_name']}")

        if len(crosswalks) > 25:
            print(f"... and {len(crosswalks) - 25} more crosswalk linkages established in Memgraph & PostgreSQL.")
        print("=" * 105 + "\n")

    except Exception as e:
        logger.exception("Ingestion failed: %s", e)
    finally:
        session.close()
        if mem_driver:
            mem_driver.close()


if __name__ == "__main__":
    main()
