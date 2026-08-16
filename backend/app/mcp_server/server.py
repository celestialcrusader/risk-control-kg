"""
Pure RCKG Enterprise Model Context Protocol (MCP) Server
(STORY-MCP-201, STORY-MCP-202, STORY-MCP-203)

Exposes canonical GRC capabilities, query tools, governance analytics,
dynamic NLI crosswalk evaluations, auditor overrides, and context prompts
to autonomous AI agents (Claude Code, Gemini CLI, Cursor, Windsurf, OpenDevin).
"""
import os
import sys
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from sqlalchemy import desc, cast, Float
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rckg_nodes import (
    ObligationNode,
    FrameworkControlObjectiveNode,
    ObligationFrameworkMapping,
    SemanticRelation,
    AssuranceCoverage,
)
from app.models import AuditLog
from app.services.nli_evaluator import NliBatchCrosswalkEvaluator
from app.services.coverage_verifier import AtomicCoverageVerifier
from app.services.confidence_calibrator import format_structured_rationale

# Initialize FastMCP Server
mcp_server = FastMCP(
    name="Pure-RCKG-Engine",
    instructions=(
        "You are connected to the Pure RCKG (Risk Control Knowledge Graph) Governance Engine. "
        "Use this server to query regulatory obligations (e.g. MAS TRM), active security controls "
        "(NIST SP 800-53 Rev 5), evaluate semantic crosswalks, inspect coverage gaps, and record auditor overrides."
    )
)

WITHDRAWN_NIST_IDS = {
    "NIST-AC-9", "NIST-AC-13", "NIST-AC-15", "NIST-AT-5", "NIST-AU-13", "NIST-AU-15",
    "NIST-CA-4", "NIST-CM-13", "NIST-CP-5", "NIST-IA-13", "NIST-IR-10", "NIST-MA-1",
    "NIST-MP-8", "NIST-PE-7", "NIST-PE-11", "NIST-PE-12", "NIST-PE-19", "NIST-PL-3",
    "NIST-PS-9", "NIST-RA-4", "NIST-SA-6", "NIST-SA-7", "NIST-SA-12", "NIST-SA-13",
    "NIST-SA-14", "NIST-SA-18", "NIST-SA-19", "NIST-SC-6", "NIST-SC-9", "NIST-SI-9"
}

RETAIL_CONSUMER_GAP_IDS = {
    "MAS-14.3.3.a": (
        "Direct customer notification threshold mandate. NIST SP 800-53 Rev 5 governs federal information systems and has no consumer banking mandate.",
        "Implement dedicated customer-facing push/SMS alerting infrastructure."
    ),
    "MAS-14.3.3.b": (
        "Customer notification message content requirements (transaction type, amount, reporting instructions).",
        "Configure consumer banking transaction notification templates."
    ),
    "MAS-14.4.2": (
        "Timely customer cyber threat advisories. Out of scope for federal system controls.",
        "Establish customer cybersecurity bulletin publishing workflow."
    ),
    "MAS-14.4.3": (
        "Customer reporting instructions for unauthorized transactions and fraud detection advisory.",
        "Deploy fraud advisory center and 24/7 retail customer hotline."
    )
}


# =============================================================================
# STORY-MCP-201: Canonical Crosswalk Tools
# =============================================================================

@mcp_server.tool()
def query_obligations(
    framework: str = "MAS-TRM",
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query regulatory obligations (e.g. MAS Technology Risk Management Guidelines).
    Supports keyword search, chapter filtering, and pagination.
    """
    db: Session = SessionLocal()
    try:
        query = db.query(ObligationNode)
        if framework:
            f_clean = framework.replace("-", " ")
            query = query.filter(
                (ObligationNode.framework_name.ilike(f"%{framework}%")) |
                (ObligationNode.framework_name.ilike(f"%{f_clean}%"))
            )
        if search:
            query = query.filter(
                (ObligationNode.statement_text.ilike(f"%{search}%")) |
                (ObligationNode.obligation_id.ilike(f"%{search}%"))
            )
        
        total = query.count()
        records = query.order_by(ObligationNode.obligation_id).offset(offset).limit(limit).all()
        
        items = [
            {
                "obligation_id": r.obligation_id,
                "statement_text": r.statement_text,
                "framework_name": r.framework_name,
                "section_reference": r.section_reference,
            }
            for r in records
        ]
        return {"total": total, "limit": limit, "offset": offset, "items": items}
    finally:
        db.close()


@mcp_server.tool()
def query_controls(
    framework: str = "NIST-SP-800-53",
    family: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query cybersecurity and privacy framework controls (e.g. NIST SP 800-53 Rev 5).
    When active_only=True, filters out the 30 withdrawn/empty controls.
    """
    db: Session = SessionLocal()
    try:
        query = db.query(FrameworkControlObjectiveNode)
        if active_only:
            query = query.filter(
                ~FrameworkControlObjectiveNode.framework_obj_id.in_(WITHDRAWN_NIST_IDS)
            )
        if family:
            query = query.filter(FrameworkControlObjectiveNode.framework_obj_id.ilike(f"NIST-{family}%"))
            
        total = query.count()
        records = query.order_by(FrameworkControlObjectiveNode.framework_obj_id).offset(offset).limit(limit).all()
        
        items = [
            {
                "framework_obj_id": r.framework_obj_id,
                "objective_name": r.objective_name,
                "objective_text": r.objective_text,
                "framework_name": r.framework_name,
            }
            for r in records
        ]
        return {"total": total, "limit": limit, "offset": offset, "items": items}
    finally:
        db.close()


@mcp_server.tool()
def query_crosswalk_mapping(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    semantic_relation: Optional[str] = None,
    assurance_coverage: Optional[str] = None,
    min_confidence: Optional[float] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query the 2D Set-Theoretic Crosswalk between regulatory obligations and security controls.
    Returns matched pairs with semantic_relation, assurance_coverage, confidence_score, and 4-part rationale.
    """
    db: Session = SessionLocal()
    try:
        query = (
            db.query(ObligationFrameworkMapping, ObligationNode, FrameworkControlObjectiveNode)
            .join(ObligationNode, ObligationFrameworkMapping.obligation_id == ObligationNode.id)
            .join(FrameworkControlObjectiveNode, ObligationFrameworkMapping.framework_objective_id == FrameworkControlObjectiveNode.id)
        )
        
        if source_id:
            query = query.filter(ObligationNode.obligation_id == source_id)
        if target_id:
            query = query.filter(FrameworkControlObjectiveNode.framework_obj_id == target_id)
        if semantic_relation:
            query = query.filter(ObligationFrameworkMapping.semantic_relation == semantic_relation)
        if assurance_coverage:
            query = query.filter(ObligationFrameworkMapping.assurance_coverage == assurance_coverage)
        if min_confidence is not None:
            query = query.filter(cast(ObligationFrameworkMapping.confidence_score, Float) >= min_confidence)
            
        total = query.count()
        records = query.order_by(desc(ObligationFrameworkMapping.confidence_score)).offset(offset).limit(limit).all()
        
        items = [
            {
                "mapping_id": str(m.id),
                "source_id": o.obligation_id,
                "source_text": o.statement_text or "",
                "target_id": c.framework_obj_id,
                "target_name": c.objective_name or "",
                "semantic_relation": m.semantic_relation.value if hasattr(m.semantic_relation, "value") else str(m.semantic_relation),
                "assurance_coverage": m.assurance_coverage.value if hasattr(m.assurance_coverage, "value") else str(m.assurance_coverage),
                "confidence_score": float(m.confidence_score or 0.0),
                "rationale": m.rationale or "",
            }
            for m, o, c in records
        ]
        return {"total": total, "limit": limit, "offset": offset, "items": items}
    finally:
        db.close()


# =============================================================================
# STORY-MCP-202: Governance Analytics, Gap Inspection & Realtime Evaluation
# =============================================================================

@mcp_server.tool()
def get_coverage_analytics() -> Dict[str, Any]:
    """
    Get aggregate compliance coverage statistics, rates (Full, Partial, No Coverage),
    and chapter-by-chapter compliance breakdown for MAS TRM obligations.
    """
    db: Session = SessionLocal()
    try:
        total_obls = db.query(ObligationNode).count()
        active_ctrls = db.query(FrameworkControlObjectiveNode).filter(
            ~FrameworkControlObjectiveNode.framework_obj_id.in_(WITHDRAWN_NIST_IDS)
        ).count()
        total_mappings = db.query(ObligationFrameworkMapping).count()
        
        full_cnt = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.assurance_coverage == AssuranceCoverage.FULL_COVERAGE).count()
        part_cnt = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.assurance_coverage == AssuranceCoverage.PARTIAL_COVERAGE).count()
        no_cnt = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.assurance_coverage == AssuranceCoverage.NO_COVERAGE).count()
        
        denom = max(total_mappings, 1)
        return {
            "total_obligations": total_obls,
            "active_controls": active_ctrls,
            "total_linkages": total_mappings,
            "rates": {
                "full_coverage_pct": round((full_cnt / denom) * 100, 1),
                "partial_coverage_pct": round((part_cnt / denom) * 100, 1),
                "no_coverage_pct": round((no_cnt / denom) * 100, 1),
            }
        }
    finally:
        db.close()


@mcp_server.tool()
def get_compliance_gaps(framework: str = "MAS-TRM") -> Dict[str, Any]:
    """
    Inspect defensible two-tier compliance gaps:
    - Category A: Zero candidate controls above semantic retrieval threshold.
    - Category B: Out-of-scope Retail Consumer Mandates (e.g. MAS 14.3.3.a/b, 14.4.2/3).
    """
    db: Session = SessionLocal()
    try:
        query = db.query(ObligationNode)
        if framework:
            f_clean = framework.replace("-", " ")
            query = query.filter(
                (ObligationNode.framework_name.ilike(f"%{framework}%")) |
                (ObligationNode.framework_name.ilike(f"%{f_clean}%"))
            )
        all_obls = query.all()
        mapped_obl_ids = set(row[0] for row in db.query(ObligationFrameworkMapping.obligation_id).distinct().all())
        
        cat_a = []
        cat_b = []
        for obl in all_obls:
            if obl.obligation_id in RETAIL_CONSUMER_GAP_IDS:
                root_cause, remediation = RETAIL_CONSUMER_GAP_IDS[obl.obligation_id]
                cat_b.append({
                    "obligation_id": obl.obligation_id,
                    "statement_text": obl.statement_text or "",
                    "audit_root_cause": root_cause,
                    "suggested_remediation": remediation,
                })
            elif obl.id not in mapped_obl_ids:
                cat_a.append({
                    "obligation_id": obl.obligation_id,
                    "statement_text": obl.statement_text or "",
                    "audit_root_cause": "Zero candidate controls above semantic retrieval threshold.",
                    "suggested_remediation": "Review custom institutional controls or supplementary standards.",
                })
                
        return {
            "total_true_gaps": len(cat_a) + len(cat_b),
            "category_a_unmatched": cat_a,
            "category_b_retail_mandates": cat_b
        }
    finally:
        db.close()


@mcp_server.tool()
def evaluate_compliance_crosswalk(
    source_text: str,
    target_text: str,
    source_id: str = "CUSTOM-SRC",
    target_id: str = "CUSTOM-TGT"
) -> Dict[str, Any]:
    """
    Execute realtime Dual-Judge NLI evaluation between any source regulatory obligation
    and target control requirement. Returns 2D classification, calibrated confidence, and 4-part rationale.
    """
    evaluator = NliBatchCrosswalkEvaluator()
    verifier = AtomicCoverageVerifier()
    
    res = evaluator.evaluate_pair(source_text, target_text)
    
    rel_raw = getattr(res, "semantic_relation", "OVERLAPS")
    cov_raw = getattr(res, "assurance_coverage", "PARTIAL_COVERAGE")
    if hasattr(rel_raw, "value"):
        rel_raw = rel_raw.value
    if hasattr(cov_raw, "value"):
        cov_raw = cov_raw.value
        
    adj_rel_str, adj_cov_str, gate_note = verifier.verify_and_gate(
        source_id, target_id, source_text, target_text, str(rel_raw), str(cov_raw)
    )
    
    adj_rel = SemanticRelation(adj_rel_str)
    adj_cov = AssuranceCoverage(adj_cov_str)
    
    formatted_rat = format_structured_rationale(
        source_id=source_id,
        target_id=target_id,
        source_text=source_text,
        target_text=target_text,
        sem_rel=adj_rel.value,
        ass_cov=adj_cov.value,
        covered_elements=getattr(res, "covered_mechanisms", None),
        missing_elements=getattr(res, "missing_gaps", None),
        conclusion_text=getattr(res, "comparative_justification", None)
    )
    
    return {
        "semantic_relation": adj_rel.value,
        "assurance_coverage": adj_cov.value,
        "confidence_score": float(res.confidence),
        "rationale": formatted_rat
    }


@mcp_server.tool()
def override_crosswalk_mapping(
    mapping_id: str,
    semantic_relation: str,
    assurance_coverage: str,
    auditor_id: str,
    justification: str
) -> Dict[str, Any]:
    """
    Apply a human auditor override to an existing crosswalk mapping and record an immutable audit log.
    """
    db: Session = SessionLocal()
    try:
        mapping = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.id == mapping_id).first()
        if not mapping:
            return {"error": "Mapping not found", "mapping_id": mapping_id}
            
        obl = db.query(ObligationNode).filter(ObligationNode.id == mapping.obligation_id).first()
        ctrl = db.query(FrameworkControlObjectiveNode).filter(FrameworkControlObjectiveNode.id == mapping.framework_objective_id).first()
        
        old_rel = mapping.semantic_relation.value if hasattr(mapping.semantic_relation, "value") else str(mapping.semantic_relation)
        old_cov = mapping.assurance_coverage.value if hasattr(mapping.assurance_coverage, "value") else str(mapping.assurance_coverage)
        
        mapping.semantic_relation = SemanticRelation(semantic_relation)
        mapping.assurance_coverage = AssuranceCoverage(assurance_coverage)
        mapping.rationale = f"[AUDITOR OVERRIDE by {auditor_id}]: {justification} | Original: {mapping.rationale}"
        
        audit_entry = AuditLog(
            event_type="MAPPING_AUDITOR_OVERRIDE",
            actor_id=auditor_id,
            actor_type="auditor",
            event_data={
                "mapping_id": mapping_id,
                "source_id": obl.obligation_id if obl else "",
                "target_id": ctrl.framework_obj_id if ctrl else "",
                "old_relation": old_rel,
                "new_relation": semantic_relation,
                "old_coverage": old_cov,
                "new_coverage": assurance_coverage,
                "justification": justification,
            }
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(mapping)
        
        return {
            "id": str(mapping.id),
            "obligation_id": obl.obligation_id if obl else "",
            "framework_obj_id": ctrl.framework_obj_id if ctrl else "",
            "semantic_relation": mapping.semantic_relation.value,
            "assurance_coverage": mapping.assurance_coverage.value,
            "confidence_score": float(mapping.confidence_score or 1.0),
            "rationale": mapping.rationale,
            "override_applied": True,
            "auditor_id": auditor_id,
            "justification": justification
        }
    finally:
        db.close()


# =============================================================================
# STORY-MCP-203: MCP Resources, Prompts & Contextual Audit Templates
# =============================================================================

@mcp_server.resource("rckg://governance/summary")
def get_governance_summary_resource() -> str:
    """Provides realtime summary of active regulatory and framework compliance counts."""
    db: Session = SessionLocal()
    try:
        total_obls = db.query(ObligationNode).count()
        active_ctrls = db.query(FrameworkControlObjectiveNode).filter(
            ~FrameworkControlObjectiveNode.framework_obj_id.in_(WITHDRAWN_NIST_IDS)
        ).count()
        total_mappings = db.query(ObligationFrameworkMapping).count()
        return (
            f"Pure RCKG Governance Status:\n"
            f"- Total MAS TRM Obligations: {total_obls}\n"
            f"- Active NIST SP 800-53 Controls: {active_ctrls}\n"
            f"- Audit-Defensible Mappings: {total_mappings}\n"
            f"- Two-Dimensional Set-Theoretic NLI Engine: ACTIVE"
        )
    finally:
        db.close()


@mcp_server.resource("rckg://gaps/true-gaps")
def get_true_gaps_resource() -> str:
    """Returns formatted Category B Retail Consumer Mandate compliance gap descriptions."""
    lines = ["Pure RCKG Defensible Compliance Gaps (Category B: Retail Consumer Mandates):"]
    for gap_id, (cause, rem) in RETAIL_CONSUMER_GAP_IDS.items():
        lines.append(f"\n[{gap_id}]\n  - Root Cause: {cause}\n  - Remediation: {rem}")
    return "\n".join(lines)


@mcp_server.prompt()
def audit_crosswalk_review(obligation_id: str) -> str:
    """Prompt template for AI agents reviewing an obligation crosswalk mapping."""
    return (
        f"You are an expert IT Risk and Compliance Auditor reviewing regulatory obligation '{obligation_id}'.\n"
        f"1. Use 'query_crosswalk_mapping(source_id=\"{obligation_id}\")' to inspect mapped controls.\n"
        f"2. Verify whether any mapped control provides FULL_COVERAGE or PARTIAL_COVERAGE.\n"
        f"3. If coverage gaps exist or directionality is inverted, propose an override using 'override_crosswalk_mapping'."
    )


@mcp_server.prompt()
def gap_remediation_planner() -> str:
    """Prompt template for AI agents generating remediation plans for unmapped obligations."""
    return (
        "You are a Senior GRC Remediation Architect.\n"
        "1. Inspect true compliance gaps using 'get_compliance_gaps()'.\n"
        "2. Formulate concrete engineering, operational, and customer communication procedures for each Category B retail mandate.\n"
        "3. Provide a timeline and RACI matrix for audit sign-off."
    )


if __name__ == "__main__":
    # Standard stdio entrypoint when spawned as an MCP subprocess by Claude/Gemini/Cursor
    mcp_server.run()
