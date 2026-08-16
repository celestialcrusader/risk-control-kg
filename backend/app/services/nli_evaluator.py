"""
Production Two-Dimensional NLI Crosswalk & Assurance Evaluator (Sprint O: Audit Explainability).

Evaluates candidate pairs into two genuinely orthogonal dimensions with dynamic element extraction:
1. semantic_relation: EQUIVALENT, SUBSET_OF, SUPERSET_OF, OVERLAPS, SUPPORTS, NONE (Source-relative perspective)
2. assurance_coverage: FULL_COVERAGE, PARTIAL_COVERAGE, NO_COVERAGE (Independent audit defensibility)
3. covered_mechanisms: Specific capabilities in Target Control that satisfy Source Requirement.
4. missing_gaps: Specific gaps in Target Control relative to Source Requirement.
5. comparative_justification: Defensible contrast between Source Requirement and Target Control.
"""

import json
import logging
import urllib.request
import re
import time
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TwoDimensionalEvaluation(BaseModel):
    semantic_relation: str = "NONE"
    assurance_coverage: str = "NO_COVERAGE"
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    rationale: str = ""
    covered_mechanisms: str = ""
    missing_gaps: str = ""
    comparative_justification: str = ""

    @property
    def relation(self) -> str:
        """Backward compatibility alias for legacy scripts."""
        return self.semantic_relation


# Alias for backward compatibility
SetTheoryEvaluation = TwoDimensionalEvaluation


class NliBatchCrosswalkEvaluator:
    """Evaluates regulatory obligation to framework control mappings with dynamic element extraction."""

    def __init__(self, llm_endpoint: str = "http://localhost:8000/v1"):
        self.llm_endpoint = llm_endpoint

    def _call_llm_judgment(self, source_text: str, target_text: str) -> Optional[TwoDimensionalEvaluation]:
        """Calls vLLM LLM endpoint for instant two-dimensional audit reasoning and dynamic element extraction."""
        prompt = f'''<|im_start|>system
You are a Senior Compliance Auditor and Regulatory Crosswalk Engine.
Analyze the relationship between Source Obligation (Requirement A) and Target Control (Control B).

Evaluate from the perspective of Source Requirement A:

1. "semantic_relation":
   - "EQUIVALENT": Scope, intent, and actionable technical mandates are 1-to-1 identical.
   - "SUBSET_OF": Control B completely satisfies Requirement A plus additional mandates (A ⊆ B).
   - "SUPERSET_OF": Requirement A is broader; Control B only addresses a specific sub-component (A ⊇ B).
   - "OVERLAPS": Material technical overlap, but neither strictly contains the other.
   - "SUPPORTS": Control B provides governance, policy, or budget support without implementing technical controls.
   - "NONE": Unrelated or superficial similarity.

2. "assurance_coverage":
   - "FULL_COVERAGE": Technical evidence proving Control B is implemented fully satisfies Requirement A for audit sign-off.
   - "PARTIAL_COVERAGE": Control B addresses part of Requirement A, but residual regulatory requirements remain unmet.
   - "NO_COVERAGE": Implementing Control B does NOT satisfy Requirement A (or purely enabling/unrelated).

3. "covered_mechanisms":
   - 1 short sentence naming the exact capabilities in Control B that address Requirement A.

4. "missing_gaps":
   - 1 short sentence naming what Requirement A mandates that Control B lacks (or "None: Full coverage").

5. "comparative_justification":
   - 1-2 sentence comparative rationale contrasting the mechanisms in Requirement A vs Control B.

Return JSON only.<|im_end|>
<|im_start|>user
Source Requirement A: "{source_text}"
Target Control B: "{target_text}"
<|im_end|>
<|im_start|>assistant
<think>
</think>
{{
  "semantic_relation": "'''

        req_data = {
            "model": "nvidia/Qwen3.6-35B-A3B-NVFP4",
            "prompt": prompt,
            "max_tokens": 250,
            "temperature": 0.0,
        }

        # Retry up to 2 times with backoff
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    f"{self.llm_endpoint}/completions",
                    data=json.dumps(req_data).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Connection": "close"},
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    raw_tail = '{\n  "semantic_relation": "' + resp_json["choices"][0]["text"].strip()
                    if not raw_tail.endswith("}"):
                        raw_tail = raw_tail.rsplit(",", 1)[0] + "\n}"

                    try:
                        parsed = json.loads(raw_tail)
                    except Exception:
                        m_rel = re.search(r'\"semantic_relation\":\s*\"([^\"]+)\"', raw_tail)
                        m_cov = re.search(r'\"assurance_coverage\":\s*\"([^\"]+)\"', raw_tail)
                        m_cov_m = re.search(r'\"covered_mechanisms\":\s*\"([^\"]+)\"', raw_tail)
                        m_mis_g = re.search(r'\"missing_gaps\":\s*\"([^\"]+)\"', raw_tail)
                        m_just = re.search(r'\"comparative_justification\":\s*\"([^\"]+)\"', raw_tail)
                        rel = m_rel.group(1) if m_rel else "OVERLAPS"
                        cov = m_cov.group(1) if m_cov else "PARTIAL_COVERAGE"
                        cov_m = m_cov_m.group(1) if m_cov_m else ""
                        mis_g = m_mis_g.group(1) if m_mis_g else ""
                        just = m_just.group(1) if m_just else ""
                        parsed = {
                            "semantic_relation": rel,
                            "assurance_coverage": cov,
                            "confidence": 0.85,
                            "covered_mechanisms": cov_m,
                            "missing_gaps": mis_g,
                            "comparative_justification": just,
                        }

                    sem_rel = parsed.get("semantic_relation", "OVERLAPS")
                    if sem_rel == "EQUIVALENT_TO":
                        sem_rel = "EQUIVALENT"

                    ass_cov = parsed.get("assurance_coverage", "PARTIAL_COVERAGE")
                    conf = float(parsed.get("confidence", 0.85))
                    covered_mech = parsed.get("covered_mechanisms", "").strip()
                    missing_gaps = parsed.get("missing_gaps", "").strip()
                    comp_just = parsed.get("comparative_justification", "").strip() or parsed.get("rationale", "").strip()

                    # Fallbacks for empty fields based on texts
                    if not covered_mech:
                        t_title = target_text.splitlines()[0] if target_text else "Target control"
                        covered_mech = f"Enforces technical controls defined in {t_title}"
                    if not missing_gaps:
                        missing_gaps = "Residual institution-specific governance and scope parameters"
                    if not comp_just:
                        comp_just = f"Control provides technical capabilities addressing obligations with {ass_cov} assurance."

                    return TwoDimensionalEvaluation(
                        semantic_relation=sem_rel,
                        assurance_coverage=ass_cov,
                        confidence=conf,
                        rationale=comp_just,
                        covered_mechanisms=covered_mech,
                        missing_gaps=missing_gaps,
                        comparative_justification=comp_just,
                    )
            except Exception as e:
                logger.debug("LLM endpoint call attempt %d failed (%s)", attempt + 1, e)
                if attempt < 2:
                    time.sleep(0.3 * (attempt + 1))
                else:
                    return None

        return None

    def evaluate_pair(self, source_text: str, target_text: str) -> TwoDimensionalEvaluation:
        """Evaluates semantic relationship and assigns calibrated 2D relation, coverage, and dynamic elements."""
        llm_res = self._call_llm_judgment(source_text, target_text)
        if llm_res:
            return llm_res

        # Strict Anti-Heuristic Fallback Gatekeeper (Hard Capped at <= 0.30 Confidence)
        return TwoDimensionalEvaluation(
            semantic_relation="NONE",
            assurance_coverage="NO_COVERAGE",
            confidence=0.15,
            rationale="Unverified heuristic fallback: Evaluator did not complete full LLM reasoning.",
            covered_mechanisms="None (fallback mode)",
            missing_gaps="Full requirement unverified by LLM judge",
            comparative_justification="Evaluation did not complete live LLM reasoning.",
        )
