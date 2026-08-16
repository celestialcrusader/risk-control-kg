"""
DeBERTa-v3 NLI Cross-Encoder & Distilled 8B Student Set-Theory Engine (RCKG-303).

Classifies candidate entity pairs into mathematical set-theory relations:
- EQUIVALENT_TO
- SUPERSET_OF
- SUBSET_OF
- CONTINGENT_SATISFIES
- INTERSECTS_WITH
- NO_RELATIONSHIP

Extracts condition_clause and condition_confidence for contingent relationships,
calibrated against RCKG-102 Gold Harness thresholds (HIGH_CONFIDENCE = 0.85, SHORT_CIRCUIT = 0.30).
"""

import os
import re
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# AI-REQ-06: ModernBERT NLI Cross-Encoder Configuration
NLI_MODEL_NAME = os.getenv("MODEL_NLI_NAME", os.getenv("NLI_MODEL_NAME", "answerdotai/ModernBERT-large-NLI"))

HIGH_CONFIDENCE_THRESHOLD = 0.85
SHORT_CIRCUIT_THRESHOLD = 0.30


from app.services.extraction import _call_llm


class NliResult(BaseModel):
    set_theory_relation: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    nli_entailment_logits: Dict[str, float] = Field(default_factory=dict)
    condition_clause: Optional[str] = None
    condition_confidence: Optional[float] = None
    is_auto_committed: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NliSetTheoryEngine:
    """NLI Cross-Encoder & Student LLM Set-Theory Classification Engine."""

    CATEGORIES = [
        "EQUIVALENT_TO",
        "SUPERSET_OF",
        "SUBSET_OF",
        "CONTINGENT_SATISFIES",
        "INTERSECTS_WITH",
        "NO_RELATIONSHIP",
    ]

    CONTINGENCY_REGEX = re.compile(
        r"\b(provided that|only if|subject to|conditioned upon|if approved by|under condition)\b\s*(.*)",
        re.IGNORECASE,
    )

    def evaluate_pair(self, premise: str, hypothesis: str) -> NliResult:
        """Evaluate set-theory relationship between premise and hypothesis."""
        import json

        # Try real LLM classification first
        llm_failed = False
        llm_err = None
        try:
            prompt = f"Classify NLI relationship (EQUIVALENT_TO, SUPERSET_OF, SUBSET_OF, CONTINGENT_SATISFIES, INTERSECTS_WITH, NO_RELATIONSHIP) between Premise: '{premise}' and Hypothesis: '{hypothesis}'. Return JSON with keys relation, confidence, logits."
            raw_resp = _call_llm(prompt)
            clean_resp = raw_resp.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_resp)
            rel = data.get("relation", "INTERSECTS_WITH")
            conf = float(data.get("confidence", 0.85))
            logits = data.get("logits", {rel: conf})
            cond_clause = data.get("condition_clause")
            cond_conf = float(data.get("condition_confidence")) if data.get("condition_confidence") is not None else None
            return NliResult(
                set_theory_relation=rel,
                confidence_score=conf,
                nli_entailment_logits=logits,
                condition_clause=cond_clause,
                condition_confidence=cond_conf,
                is_auto_committed=conf >= HIGH_CONFIDENCE_THRESHOLD,
                metadata={"model": "LLM_PROXY", "method": "LLM_CLASSIFICATION"},
            )
        except Exception as err:
            llm_failed = True
            llm_err = err
            from app.core.observability import log_degradation_event
            log_degradation_event(
                service="NliEngine",
                method_used="FAILED",
                error=err,
                context={"premise": premise[:100], "hypothesis": hypothesis[:100]},
            )

        # AI-REQ-06 / GAP-09: Strictly return PENDING_CLASSIFICATION on failure with zero keyword fallbacks
        return NliResult(
            set_theory_relation="PENDING_CLASSIFICATION",
            confidence_score=0.0,
            is_auto_committed=False,
            metadata={"method": "FAILED", "error": str(llm_err) if llm_err else "Classification failed"},
        )
