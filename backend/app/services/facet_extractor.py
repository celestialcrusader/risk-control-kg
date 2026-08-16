"""
De Jure 6-Facet Extraction Service for Pure RCKG Engine (RCKG-203b / CFIX-200).

Extracts six orthogonal legal facets (action_verb, subject_noun, domain_facet,
modality_facet, target_role_facet, control_nature) from legal rule unit text blocks using LLM with regex fallback.
"""

import json
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DeJureFacetExtractor:
    """Extracts 6 orthogonal facets from legal and policy text chunks."""

    VERB_PATTERN = re.compile(
        r"\b(limit|restrict|encrypt|monitor|audit|review|authorize|authenticate|retain|delete)\b",
        re.IGNORECASE,
    )
    NOUN_PATTERN = re.compile(
        r"\b(access|credentials|pii data|pii|data|backups|logs|networks|systems|privileges)\b",
        re.IGNORECASE,
    )

    def extract_facets(self, text: str) -> Dict[str, str]:
        """Extract all 6 orthogonal facet keys from text using LLM with regex fallback."""
        # Try LLM extraction first
        try:
            from app.services.extraction import _call_llm
            prompt = f"Extract 6 orthogonal facets (action_verb, subject_noun, domain_facet, modality_facet, target_role_facet, control_nature) from: '{text}'. Return JSON."
            raw_resp = _call_llm(prompt)
            clean_resp = raw_resp.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_resp)
            
            if isinstance(data, dict) and "action_verb" in data:
                return {
                    "action_verb": str(data.get("action_verb", "manage")).lower(),
                    "subject_noun": str(data.get("subject_noun", "system access")).lower(),
                    "domain_facet": str(data.get("domain_facet", "GeneralCompliance")),
                    "modality_facet": str(data.get("modality_facet", "MANDATORY")),
                    "target_role_facet": str(data.get("target_role_facet", "COMPLIANCE_OFFICER")),
                    "control_nature": str(data.get("control_nature", "PREVENTATIVE")),
                    "extraction_method": "LLM",
                }
        except Exception as err:
            from app.core.observability import log_degradation_event
            log_degradation_event(
                service="DeJureFacetExtractor",
                method_used="REGEX_FALLBACK",
                error=err,
                context={"text": text[:100]},
            )

        # Regex fallback path
        verb_match = self.VERB_PATTERN.search(text)
        noun_match = self.NOUN_PATTERN.search(text)

        action_verb = verb_match.group(1).lower() if verb_match else "manage"
        subject_noun = noun_match.group(1).lower() if noun_match else "system access"

        text_lower = text.lower()

        # Determine domain facet
        if "access" in text_lower or "credentials" in text_lower:
            domain_facet = "IDENTITY_ACCESS_MANAGEMENT"
        elif "encrypt" in text_lower or "pii" in text_lower or "data" in text_lower:
            domain_facet = "DATA_PROTECTION"
        else:
            domain_facet = "GENERAL_COMPLIANCE"

        # Determine modality
        if "must" in text_lower or "shall" in text_lower:
            modality = "MANDATORY"
        elif "should" in text_lower or "recommended" in text_lower:
            modality = "RECOMMENDED"
        else:
            modality = "OPTIONAL"

        # Determine target role
        if "officer" in text_lower or "security administrator" in text_lower or "system administrator" in text_lower:
            target_role = "SYSTEM_ADMINISTRATOR"
        else:
            target_role = "COMPLIANCE_OFFICER"

        return {
            "action_verb": action_verb,
            "subject_noun": subject_noun,
            "domain_facet": domain_facet,
            "modality_facet": modality,
            "target_role_facet": target_role,
            "control_nature": "PREVENTATIVE",
            "extraction_method": "REGEX_FALLBACK",
        }
