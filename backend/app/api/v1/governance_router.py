"""
FastAPI Router for Governance, Gap Analytics, and Realtime NLI Evaluation (STORY-MCP-102)
"""
from typing import Optional, List, Dict
from collections import defaultdict
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.rckg_nodes import ObligationNode, FrameworkControlObjectiveNode, ObligationFrameworkMapping, AssuranceCoverage, SemanticRelation
from app.schemas.crosswalk_api import (
    GapItem, CategorizedGapsResponse,
    ChapterCoverageItem, CoverageRateBreakdown, CoverageSummaryResponse,
    RealtimeEvaluationRequest, RealtimeEvaluationResponse
)
from app.services.nli_evaluator import NliBatchCrosswalkEvaluator
from app.services.coverage_verifier import AtomicCoverageVerifier
from app.services.confidence_calibrator import format_structured_rationale

router = APIRouter(prefix="", tags=["Governance & Gap Analytics"])

# Known Category B Retail Consumer Mandates
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

WITHDRAWN_NIST_IDS = {
    "NIST-AC-9", "NIST-AC-13", "NIST-AC-15", "NIST-AT-5", "NIST-AU-13", "NIST-AU-15",
    "NIST-CA-4", "NIST-CM-13", "NIST-CP-5", "NIST-IA-13", "NIST-IR-10", "NIST-MA-1",
    "NIST-MP-8", "NIST-PE-7", "NIST-PE-11", "NIST-PE-12", "NIST-PE-19", "NIST-PL-3",
    "NIST-PS-9", "NIST-RA-4", "NIST-SA-6", "NIST-SA-7", "NIST-SA-12", "NIST-SA-13",
    "NIST-SA-14", "NIST-SA-18", "NIST-SA-19", "NIST-SC-6", "NIST-SC-9", "NIST-SI-9"
}


@router.get("/gaps", response_model=CategorizedGapsResponse)
def get_gaps(
    framework: Optional[str] = Query("MAS-TRM", description="Framework name"),
    db: Session = Depends(get_db)
):
    query = db.query(ObligationNode)
    if framework:
        f_clean = framework.replace("-", " ")
        query = query.filter(
            (ObligationNode.framework_name.ilike(f"%{framework}%")) |
            (ObligationNode.framework_name.ilike(f"%{f_clean}%"))
        )
    all_obls = query.all()
    
    # Check mappings in DB
    mapped_obl_ids = set(
        row[0] for row in db.query(ObligationFrameworkMapping.obligation_id).distinct().all()
    )
    
    cat_a: List[GapItem] = []
    cat_b: List[GapItem] = []
    
    for obl in all_obls:
        if obl.obligation_id in RETAIL_CONSUMER_GAP_IDS:
            root_cause, remediation = RETAIL_CONSUMER_GAP_IDS[obl.obligation_id]
            cat_b.append(GapItem(
                obligation_id=obl.obligation_id,
                statement_text=obl.statement_text or "",
                framework_name=obl.framework_name or "MAS-TRM",
                category="Category B: Retail Consumer Mandates",
                audit_root_cause=root_cause,
                suggested_remediation=remediation
            ))
        elif obl.id not in mapped_obl_ids:
            cat_a.append(GapItem(
                obligation_id=obl.obligation_id,
                statement_text=obl.statement_text or "",
                framework_name=obl.framework_name or "MAS-TRM",
                category="Category A: Unmatched Obligations",
                audit_root_cause="Zero candidate controls above semantic retrieval threshold.",
                suggested_remediation="Review custom institutional controls or supplementary standards."
            ))
            
    return CategorizedGapsResponse(
        total_true_gaps=len(cat_a) + len(cat_b),
        category_a_unmatched=cat_a,
        category_b_retail_mandates=cat_b
    )


@router.get("/coverage/summary", response_model=CoverageSummaryResponse)
def get_coverage_summary(db: Session = Depends(get_db)):
    total_obls = db.query(ObligationNode).count()
    active_ctrls = db.query(FrameworkControlObjectiveNode).filter(
        ~FrameworkControlObjectiveNode.framework_obj_id.in_(WITHDRAWN_NIST_IDS)
    ).count()
    
    total_mappings = db.query(ObligationFrameworkMapping).count()
    
    # Coverage percentages on mappings
    full_cnt = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.assurance_coverage == AssuranceCoverage.FULL_COVERAGE).count()
    part_cnt = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.assurance_coverage == AssuranceCoverage.PARTIAL_COVERAGE).count()
    no_cnt = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.assurance_coverage == AssuranceCoverage.NO_COVERAGE).count()
    
    denom = max(total_mappings, 1)
    rates = CoverageRateBreakdown(
        full_coverage_pct=round((full_cnt / denom) * 100, 1),
        partial_coverage_pct=round((part_cnt / denom) * 100, 1),
        no_coverage_pct=round((no_cnt / denom) * 100, 1)
    )
    
    # Chapter breakdown
    all_obls = db.query(ObligationNode).all()
    chap_map = defaultdict(list)
    for o in all_obls:
        parts = o.obligation_id.replace("MAS-", "").split(".")
        chap_num = parts[0] if parts else "General"
        chap_map[f"Chapter {chap_num}"].append(o)
    
    chapters: List[ChapterCoverageItem] = []
    for chap_name in sorted(chap_map.keys(), key=lambda x: int(x.split()[1]) if x.split()[1].isdigit() else 99):
        obls_in_chap = chap_map[chap_name]
        chap_total = len(obls_in_chap)
        
        chap_full = 0
        chap_part = 0
        chap_un = 0
        
        for o in obls_in_chap:
            if o.obligation_id in RETAIL_CONSUMER_GAP_IDS:
                chap_un += 1
                continue
            
            # Check best coverage among mappings for this obligation
            m_list = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.obligation_id == o.id).all()
            if any(m.assurance_coverage == AssuranceCoverage.FULL_COVERAGE for m in m_list):
                chap_full += 1
            elif any(m.assurance_coverage == AssuranceCoverage.PARTIAL_COVERAGE for m in m_list):
                chap_part += 1
            else:
                chap_un += 1
                
        cov_pct = round(((chap_full + chap_part) / max(chap_total, 1)) * 100, 1)
        chapters.append(ChapterCoverageItem(
            chapter=chap_name,
            total_obligations=chap_total,
            fully_covered=chap_full,
            partially_covered=chap_part,
            uncovered=chap_un,
            coverage_pct=cov_pct
        ))
        
    return CoverageSummaryResponse(
        total_obligations=total_obls,
        active_controls=active_ctrls,
        total_linkages=total_mappings,
        coverage_rates=rates,
        chapter_breakdown=chapters
    )


@router.post("/evaluation/realtime", response_model=RealtimeEvaluationResponse)
def evaluate_pair_realtime(req: RealtimeEvaluationRequest):
    evaluator = NliBatchCrosswalkEvaluator()
    verifier = AtomicCoverageVerifier()
    
    res = evaluator.evaluate_pair(req.source_text, req.target_text)
    
    rel_raw = getattr(res, "semantic_relation", "OVERLAPS")
    cov_raw = getattr(res, "assurance_coverage", "PARTIAL_COVERAGE")
    
    if hasattr(rel_raw, "value"):
        rel_raw = rel_raw.value
    if hasattr(cov_raw, "value"):
        cov_raw = cov_raw.value
    
    # Calibrate direction and verify coverage
    adj_rel_str, adj_cov_str, gate_note = verifier.verify_and_gate(
        "CUSTOM-SRC", "CUSTOM-TGT", req.source_text, req.target_text, str(rel_raw), str(cov_raw)
    )
    
    adj_rel = SemanticRelation(adj_rel_str)
    adj_cov = AssuranceCoverage(adj_cov_str)
    
    formatted_rat = format_structured_rationale(
        source_id="CUSTOM-SRC",
        target_id="CUSTOM-TGT",
        source_text=req.source_text,
        target_text=req.target_text,
        sem_rel=adj_rel.value,
        ass_cov=adj_cov.value,
        covered_elements=getattr(res, "covered_mechanisms", None),
        missing_elements=getattr(res, "missing_gaps", None),
        conclusion_text=getattr(res, "comparative_justification", None)
    )
    
    return RealtimeEvaluationResponse(
        semantic_relation=adj_rel,
        assurance_coverage=adj_cov,
        confidence_score=res.confidence,
        rationale=formatted_rat
    )
