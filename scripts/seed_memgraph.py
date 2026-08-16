"""
Canonical 5-Linkage & Set-Theory Seeding Script for Memgraph (06-delta.md Compliant).

Seeds the exact 5-Linkage Canonical Topology:
  [Risk] --(MITIGATES)--> [ControlObjective] --(SATISFIES)--> [Obligation]
  [ControlObjective] --(OPERATIONALIZED_BY)--> [ControlActivity]
  [ControlObjective] --(CROSSWALKS_TO_OBJ)--> [FrameworkControlObjective]
  [ControlActivity] --(CROSSWALKS_TO_ACT)--> [FrameworkControlActivity]
And Escape Hatch Gap Topologies:
  [StatutoryRequirement] --(GAP_IDENTIFIED)--> [GapNode] --(AFFECTS)--> [ControlActivity]
"""

import sys
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from neo4j import GraphDatabase

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_memgraph")

BOLT_URL = "bolt://localhost:7687"


def seed_memgraph_canonical():
    logger.info("Connecting to Memgraph at %s...", BOLT_URL)
    driver = GraphDatabase.driver(BOLT_URL, auth=("", ""))

    with driver.session() as session:
        # Reset graph store
        session.run("MATCH (n) DETACH DELETE n;")

        # 1. Statutory & Framework Control Objectives
        framework_nodes = [
            ("NIST-SP-800-53-AC-1", "NIST SP 800-53 Rev 5", "Policy and Procedures", "FrameworkControlObjective"),
            ("NIST-SP-800-53-AC-2", "NIST SP 800-53 Rev 5", "Account Management", "FrameworkControlObjective"),
            ("NIST-SP-800-53-AU-2", "NIST SP 800-53 Rev 5", "Event Logging", "FrameworkControlObjective"),
            ("ISO-27001-A.5.15", "ISO/IEC 27001:2022", "Access Control Rules", "Obligation"),
            ("ISO-27001-A.8.15", "ISO/IEC 27001:2022", "Logging and Monitoring", "Obligation"),
            ("EU-AI-ACT-ART-9", "EU AI Act 2024", "AI Risk Management System", "Obligation"),
        ]

        for fid, fname, title, label in framework_nodes:
            query = f"""
            MERGE (n:{label} {{node_id: $fid}})
            SET n.framework_name = $fname, n.title = $title, n.status = 'HUMAN_ATTESTED'
            """
            session.run(query, fid=fid, fname=fname, title=title)

        # 2. Risks
        risks = [
            ("RISK-001", "Unauthorized Access & Credential Abuse", "HIGH"),
            ("RISK-002", "Unmonitored Audit Event Tampering", "CRITICAL"),
            ("RISK-003", "AI System Bias & Ungoverned Training", "HIGH"),
        ]

        for rid, name, sev in risks:
            session.run(
                """
                MERGE (r:Risk {node_id: $rid})
                SET r.title = $name, r.risk_severity = $sev
                """,
                rid=rid,
                name=name,
                sev=sev,
            )

        # 3. Control Objectives (Internal GRC Layer)
        control_objectives = [
            ("CO-IAM-01", "Identity & Access Control Standard", "Access Control"),
            ("CO-LOG-01", "Centralized Security Audit Logging", "Audit & Logging"),
            ("CO-AIR-01", "AI Lifecycle Risk Assessment & Monitoring", "AI Governance"),
        ]

        for co_id, title, domain in control_objectives:
            session.run(
                """
                MERGE (co:ControlObjective {node_id: $co_id})
                SET co.title = $title, co.domain_facet = $domain
                """,
                co_id=co_id,
                title=title,
                domain=domain,
            )

        # 4. Control Activities (Operational Internal Enterprise Policies)
        control_activities = [
            ("CA-MFA-001", "Enforce Multi-Factor Authentication for Admin Portals", "Access Control"),
            ("CA-SIEM-002", "Ingest Application & OS Logs into Centralized SIEM", "Audit Logging"),
            ("CA-AIRM-003", "Quarterly Bias & Safety Evaluation of Deployed LLMs", "AI Governance"),
        ]

        for ca_id, title, domain in control_activities:
            session.run(
                """
                MERGE (ca:ControlActivity {node_id: $ca_id})
                SET ca.title = $title, ca.domain_facet = $domain
                """,
                ca_id=ca_id,
                title=title,
                domain=domain,
            )

        # 5. Canonical 5-Linkage Topology Relationships
        # (Risk) -[MITIGATES]-> (ControlObjective)
        session.run("MATCH (r:Risk {node_id: 'RISK-001'}), (co:ControlObjective {node_id: 'CO-IAM-01'}) MERGE (r)-[:MITIGATES]->(co);")
        session.run("MATCH (r:Risk {node_id: 'RISK-002'}), (co:ControlObjective {node_id: 'CO-LOG-01'}) MERGE (r)-[:MITIGATES]->(co);")
        session.run("MATCH (r:Risk {node_id: 'RISK-003'}), (co:ControlObjective {node_id: 'CO-AIR-01'}) MERGE (r)-[:MITIGATES]->(co);")

        # (ControlObjective) -[SATISFIES]-> (Obligation) with NLI Set-Theory Attributes
        session.run(
            """
            MATCH (co:ControlObjective {node_id: 'CO-IAM-01'}), (ob:Obligation {node_id: 'ISO-27001-A.5.15'})
            MERGE (co)-[s:SATISFIES {
                set_theory_relation: 'EQUIVALENT_TO',
                confidence_score: 0.95,
                condition_confidence: 1.00,
                status: 'PROBABILISTIC_AI'
            }]->(ob);
            """
        )
        session.run(
            """
            MATCH (co:ControlObjective {node_id: 'CO-AIR-01'}), (ob:Obligation {node_id: 'EU-AI-ACT-ART-9'})
            MERGE (co)-[s:SATISFIES {
                set_theory_relation: 'CONTINGENT_SATISFIES',
                condition_clause: 'Applies ONLY IF system_classification == HighRiskAI',
                condition_confidence: 0.92,
                confidence_score: 0.88,
                status: 'PROBABILISTIC_AI'
            }]->(ob);
            """
        )

        # (ControlObjective) -[OPERATIONALIZED_BY]-> (ControlActivity)
        session.run("MATCH (co:ControlObjective {node_id: 'CO-IAM-01'}), (ca:ControlActivity {node_id: 'CA-MFA-001'}) MERGE (co)-[:OPERATIONALIZED_BY]->(ca);")
        session.run("MATCH (co:ControlObjective {node_id: 'CO-LOG-01'}), (ca:ControlActivity {node_id: 'CA-SIEM-002'}) MERGE (co)-[:OPERATIONALIZED_BY]->(ca);")
        session.run("MATCH (co:ControlObjective {node_id: 'CO-AIR-01'}), (ca:ControlActivity {node_id: 'CA-AIRM-003'}) MERGE (co)-[:OPERATIONALIZED_BY]->(ca);")

        # (ControlObjective) -[CROSSWALKS_TO_OBJ]-> (FrameworkControlObjective)
        session.run("MATCH (co:ControlObjective {node_id: 'CO-IAM-01'}), (fc:FrameworkControlObjective {node_id: 'NIST-SP-800-53-AC-2'}) MERGE (co)-[:CROSSWALKS_TO_OBJ]->(fc);")
        session.run("MATCH (co:ControlObjective {node_id: 'CO-LOG-01'}), (fc:FrameworkControlObjective {node_id: 'NIST-SP-800-53-AU-2'}) MERGE (co)-[:CROSSWALKS_TO_OBJ]->(fc);")

        # 6. Escape Hatch Topology & Gap Nodes
        session.run(
            """
            MERGE (g:GapNode {gap_id: 'GAP-2026-001'})
            SET g.gap_type = 'MISSING_INTERMEDIATE_POLICY_OBJECTIVE',
                g.risk_level = 'HIGH',
                g.gap_description = 'Missing explicit control activity for NIST SP 800-53 AC-1 policy dissemination.'
            WITH g
            MATCH (fc:FrameworkControlObjective {node_id: 'NIST-SP-800-53-AC-1'})
            MATCH (ca:ControlActivity {node_id: 'CA-MFA-001'})
            MERGE (fc)-[:GAP_IDENTIFIED]->(g)
            MERGE (g)-[:AFFECTS]->(ca);
            """
        )

        res_nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
        res_edges = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]

        logger.info("==================================================")
        logger.info("CANONICAL 5-LINKAGE MEMGRAPH SEEDING COMPLETE!")
        logger.info("Total Nodes in Memgraph:        %d", res_nodes)
        logger.info("Total Relationships in Memgraph: %d", res_edges)
        logger.info("==================================================")

    driver.close()


if __name__ == "__main__":
    seed_memgraph_canonical()
