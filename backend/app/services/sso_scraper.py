"""
Singapore Statutes Online (SSO) HTML DOM Parser for RCKG.
Extracts native statutory sections, provisions, and anchors directly from HTML DOM.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SSOSectionNode:
    def __init__(self, clause_id: str, title: str, text: str, parent_clause_id: Optional[str] = None, source_anchor: Optional[str] = None):
        self.clause_id = clause_id
        self.title = title
        self.text = text
        self.parent_clause_id = parent_clause_id
        self.source_anchor = source_anchor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "title": self.title,
            "text": self.text,
            "parent_clause_id": self.parent_clause_id,
            "source_anchor": self.source_anchor,
        }


def parse_sso_html(html_content: str) -> List[Dict[str, Any]]:
    """Parses SSO statutory HTML content into a list of clause nodes."""
    soup = BeautifulSoup(html_content, "html.parser")
    nodes: List[Dict[str, Any]] = []
    
    # Process primary provisions
    for prov in soup.find_all(["div", "section"], class_=re.compile(r"prov\d+")):
        prov_num_elem = prov.find("span", class_="provNum")
        prov_title_elem = prov.find("span", class_="provTitle")
        prov_body_elem = prov.find("div", class_="provBody")
        
        clause_id = prov_num_elem.text.strip() if prov_num_elem else ""
        title = prov_title_elem.text.strip() if prov_title_elem else ""
        text = prov_body_elem.text.strip() if prov_body_elem else prov.text.strip()
        anchor = prov.get("id") or prov.get("data-anchor-id")
        
        if clause_id or text:
            node = SSOSectionNode(
                clause_id=clause_id,
                title=title,
                text=text,
                source_anchor=str(anchor) if anchor else None
            )
            nodes.append(node.to_dict())
            
    return nodes
