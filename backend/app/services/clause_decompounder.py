"""
Multi-Intent Clause Decompounder & Query Expansion Service (STORY-COMP-301).

Deconstructs multi-threat, compound, and multi-sentence regulatory obligations into
atomic, high-precision technical query expressions for hybrid candidate retrieval.
"""

import re
from typing import List


class ClauseDecompounder:
    """Decomposes compound regulatory clauses into atomic sub-intent queries."""

    # Threat and control pattern mappings for precision expansion
    COMPOUND_PATTERNS = [
        (r"sql injection|cross-site scripting|xss|injection", "input validation error handling information input injection web application security"),
        (r"denial-of-service|dos|ddos", "denial of service protection capacity management availability boundary protection"),
        (r"malware|malicious code|ransomware|virus", "malicious code protection anti-malware antivirus execution prevention"),
        (r"man-in-the-middle|mitm|eavesdropping|interception", "transmission confidentiality and integrity session authenticity communication protection"),
        (r"communication channels|transmitted over the internet|transit|transmission", "transmission confidentiality and integrity cryptographic protection secure communications channels"),
        (r"multi-factor|mfa|2fa|authentication|credentials", "NIST-IA-2 identification and authentication multi-factor authentication for non-privileged and privileged access authenticator management"),
        (r"segregation of duties|separation of duties|single individual", "separation of duties access authorizations dual control"),
        (r"technology refresh|end-of-support|obsolete", "unsupported system components component replacement life cycle maintenance"),
        (r"adversarial attacks|penetration|simulat|threat scenario", "penetration testing red team adversary simulation technical surveillance"),
    ]

    def decompose(self, clause_text: str) -> List[str]:
        """
        Deconstructs a regulatory obligation statement into atomic sub-queries.
        Returns a list of search query strings (original + atomic sub-intents).
        """
        if not clause_text or not clause_text.strip():
            return []

        cleaned = clause_text.strip()
        lower = cleaned.lower()
        sub_queries = [cleaned]

        # 1. Check for compound list syntax ("such as X, Y, and Z", "including A, B, and C")
        match = re.search(r"(?:such as|including|namely|consisting of)\s+(.+)$", lower, re.IGNORECASE)
        if match:
            items_clause = match.group(1)
            # Split by commas, semicolons, and 'and'
            parts = re.split(r",\s*|\s+and\s+|;\s*", items_clause)
            for p in parts:
                clean_p = p.strip().strip(".").strip()
                if len(clean_p) > 3 and clean_p not in ["etc", "other"]:
                    sub_queries.append(f"{clean_p} security controls")

        # 2. Check for domain-specific threat patterns to add atomic technical expansions
        for pat, expansion in self.COMPOUND_PATTERNS:
            if re.search(pat, lower):
                if expansion not in sub_queries:
                    sub_queries.append(expansion)

        # 3. Deduplicate while preserving order
        unique_queries = []
        for q in sub_queries:
            if q not in unique_queries:
                unique_queries.append(q)

        return unique_queries
