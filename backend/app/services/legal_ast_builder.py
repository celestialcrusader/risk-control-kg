"""
Legal Hierarchy AST Builder using Regex State Machine for RCKG.
Constructs parent-child section containment trees for regulatory sub-clauses.
"""

import re
from typing import List, Dict, Any, Optional


class LegalHierarchyBuilder:
    LEVEL_PATTERNS = [
        ("part", re.compile(r"^(PART|Part)\s+([IVXLCDM\d]+)")),
        ("section", re.compile(r"^(\d+\.)\s+")),
        ("sub_section", re.compile(r"^(\d+\.\d+)\s+")),
        ("clause", re.compile(r"^(\d+\.\d+\.\d+)\s+")),
        ("roman_sub", re.compile(r"^(\([ivxlcdm]+\))\s+")),
        ("sub_clause", re.compile(r"^(\([a-z0-9]+\))\s+")),
    ]



    LEVEL_ORDER = {
        "part": 1,
        "section": 2,
        "sub_section": 3,
        "clause": 4,
        "sub_clause": 5,
        "roman_sub": 6,
    }

    def __init__(self):
        self.stack: List[Dict[str, Any]] = []

    def process_elements(self, text_blocks: List[str]) -> List[Dict[str, Any]]:
        ast_nodes: List[Dict[str, Any]] = []
        for text in text_blocks:
            cleaned = text.strip()
            if not cleaned:
                continue
                
            matched_level = None
            clause_id = ""

            for level_name, regex in self.LEVEL_PATTERNS:
                match = regex.match(cleaned)
                if match:
                    matched_level = level_name
                    clause_id = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                    break

            parent_id = self._resolve_parent(matched_level, clause_id) if matched_level else (self.stack[-1]["clause_id"] if self.stack else None)

            node = {
                "clause_id": clause_id,
                "level": matched_level or "body_text",
                "text": cleaned,
                "parent_clause_id": parent_id,
            }
            ast_nodes.append(node)
            
            if matched_level:
                self.stack.append({"clause_id": clause_id, "level": matched_level, "order": self.LEVEL_ORDER[matched_level]})

        return ast_nodes

    def _resolve_parent(self, matched_level: str, clause_id: str) -> Optional[str]:
        current_order = self.LEVEL_ORDER.get(matched_level, 99)
        while self.stack and self.stack[-1]["order"] >= current_order:
            self.stack.pop()
        return self.stack[-1]["clause_id"] if self.stack else None
