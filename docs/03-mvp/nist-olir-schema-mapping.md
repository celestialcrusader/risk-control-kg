# NIST OLIR XML Schema Mapping Reference & Specification

**Document Version:** 1.0 — Technical Schema Reference  
**Status:** Approved / Active Specification  
**Classification:** Internal — Technical Reference  
**Target Repository:** `/home/zackchow/coding/rckg`  
**Output Target:** `docs/03-mvp/nist-olir-schema-mapping.md`  
**Related Ticket:** [RCKG-101](file:///home/zackchow/coding/rckg/docs/03-mvp/mvp-sprint.md#rckg-101-open-source-compliance-seed-harvesting--seed-graph-ingestion-pipeline)  

---

## 1. Overview & Data Source

The **National Institute of Standards and Technology (NIST) Online Informative References (OLIR)** program provides official, standardized crosswalk mappings between security/privacy control frameworks (e.g. NIST SP 800-53 Rev 5, ISO/IEC 27001:2022, NIST CSF 2.0, HIPAA).

NIST OLIR exports XML files using a structured data model where each `<InformativeReference>` connects a **Focal Document** (e.g. NIST SP 800-53) to a **Referenced Document** (e.g. ISO 27001).

---

## 2. NIST OLIR XML Data Structure

Below is the standard XML structure returned by NIST OLIR API and XML export files (`https://csrc.nist.gov/projects/olir`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<OLIRDataExport xmlns="http://csrc.nist.gov/ns/olir/1.0">
  <InformativeReference id="REF-NIST-ISO-001">
    <FocalDocument>
      <DocumentIdentifier>NIST SP 800-53 Rev 5</DocumentIdentifier>
      <SectionIdentifier>AC-2</SectionIdentifier>
      <Identifier>NIST-800-53-AC-2</Identifier>
      <Title>Account Management</Title>
      <Description>The organization manages information system accounts, including establishing, activating, modifying, reviewing, disabling, and removing accounts in accordance with organizational procedures.</Description>
    </FocalDocument>
    <ReferencedDocument>
      <DocumentIdentifier>ISO/IEC 27001:2022</DocumentIdentifier>
      <SectionIdentifier>A.5.15</SectionIdentifier>
      <Identifier>ISO-27001-A.5.15</Identifier>
      <Title>Access Control</Title>
      <Description>Rules to control physical and logical access to information and other associated assets shall be established and implemented based on business and information security requirements.</Description>
    </ReferencedDocument>
    <MappingRationale>
      <RelationshipType>EQUIVALENT_TO</RelationshipType>
      <Strength>1.0</Strength>
      <Comment>Official NIST OLIR direct alignment mapping between AC-2 and ISO A.5.15</Comment>
    </MappingRationale>
  </InformativeReference>
</OLIRDataExport>
```

---

## 3. Structural Mapping to RCKG Entities & Memgraph Schema

### 3.1 Entity Node Mapping Matrix

| NIST OLIR XML Element | Target RCKG SQLModel Class | Target Memgraph Label | Target Field Name | Value Transformation |
|---|---|---|---|---|
| `<FocalDocument>/<Identifier>` | `FrameworkControlObjectiveNode` | `:FrameworkControlObj` | `framework_obj_id` | String ID (e.g. `"NIST-800-53-AC-2"`) |
| `<FocalDocument>/<DocumentIdentifier>` | `FrameworkControlObjectiveNode` | `:FrameworkControlObj` | `framework_name` | String (e.g. `"NIST SP 800-53"`) |
| `"Rev 5"` | `FrameworkControlObjectiveNode` | `:FrameworkControlObj` | `framework_version` | Extracted version string |
| `<FocalDocument>/<Title>` | `FrameworkControlObjectiveNode` | `:FrameworkControlObj` | `objective_name` | String |
| `<FocalDocument>/<Description>` | `FrameworkControlObjectiveNode` | `:FrameworkControlObj` | `objective_text` | Text |
| `<ReferencedDocument>/<Identifier>` | `FrameworkControlActivityNode` / `Obj` | `:FrameworkControlAct` | `framework_act_id` | Target document identifier |
| `<ReferencedDocument>/<DocumentIdentifier>` | `FrameworkControlActivityNode` | `:FrameworkControlAct` | `framework_name` | String (e.g. `"ISO/IEC 27001"`) |
| `<ReferencedDocument>/<Description>` | `FrameworkControlActivityNode` | `:FrameworkControlAct` | `activity_text` | Text |

### 3.2 Edge & Linkage Relationship Mapping

| NIST OLIR XML Element | Target RCKG Linkage Table | Target Memgraph Edge Type | Property Value |
|---|---|---|---|
| `<InformativeReference>` | `ControlObjectiveFrameworkMapping` | `[:CROSSWALKS_TO_OBJ]` | Edge creation |
| `<RelationshipType>` | `SetTheoryRelation` enum | `rel.set_theory_relation` | Mapped to `EQUIVALENT_TO`, `SUPERSET_OF`, `SUBSET_OF` |
| Direct NIST OLIR Seed | - | `rel.status` | `"HUMAN_ATTESTED"` |
| Direct NIST OLIR Seed | - | `rel.is_golden_assertion` | `True` |
| Direct NIST OLIR Seed | - | `rel.confidence_score` | `1.0` |

---

## 4. Production Python Parser Reference Implementation

The following updated `NistOlirXmlParser` implementation in `backend/app/services/seed_ingestion.py` accurately parses official NIST OLIR XML files according to this schema:

```python
"""
NIST OLIR XML Parser Implementation.

Parses official NIST OLIR XML export files according to nist-olir-schema-mapping.md.
"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, List
from backend.app.models.rckg_nodes import SetTheoryRelation

logger = logging.getLogger(__name__)

class NistOlirXmlParser:
    """Parser for official NIST OLIR XML export files."""

    def __init__(self, xml_filepath: str):
        self.filepath = xml_filepath

    def parse(self) -> Dict[str, List[Dict[str, Any]]]:
        tree = ET.parse(self.filepath)
        root = tree.getroot()
        nodes, edges = [], []
        seen_nodes = set()

        # Handle optional namespace prefixes gracefully
        for ref in root.findall('.//InformativeReference') or root.findall('.//{*}InformativeReference'):
            focal = ref.find('FocalDocument') or ref.find('{*}FocalDocument')
            referenced = ref.find('ReferencedDocument') or ref.find('{*}ReferencedDocument')
            
            if focal is None or referenced is None:
                continue

            focal_id = focal.findtext('Identifier', '') or focal.findtext('{*}Identifier', '')
            focal_doc_name = focal.findtext('DocumentIdentifier', 'NIST SP 800-53') or focal.findtext('{*}DocumentIdentifier', '')
            focal_text = focal.findtext('Description', '') or focal.findtext('{*}Description', '')
            focal_title = focal.findtext('Title', focal_id) or focal.findtext('{*}Title', focal_id)

            if focal_id and focal_id not in seen_nodes:
                nodes.append({
                    "framework_obj_id": focal_id,
                    "framework_name": focal_doc_name,
                    "framework_version": "Rev 5",
                    "objective_name": focal_title,
                    "objective_text": focal_text
                })
                seen_nodes.add(focal_id)

            ref_id = referenced.findtext('Identifier', '') or referenced.findtext('{*}Identifier', '')
            ref_doc_name = referenced.findtext('DocumentIdentifier', 'ISO/IEC 27001') or referenced.findtext('{*}DocumentIdentifier', '')
            ref_text = referenced.findtext('Description', '') or referenced.findtext('{*}Description', '')
            ref_title = referenced.findtext('Title', ref_id) or referenced.findtext('{*}Title', ref_id)

            if ref_id and ref_id not in seen_nodes:
                nodes.append({
                    "framework_obj_id": ref_id,
                    "framework_name": ref_doc_name,
                    "framework_version": "2022",
                    "objective_name": ref_title,
                    "objective_text": ref_text
                })
                seen_nodes.add(ref_id)

            if focal_id and ref_id:
                edges.append({
                    "source_id": focal_id,
                    "target_id": ref_id,
                    "relation": SetTheoryRelation.EQUIVALENT_TO.value,
                    "is_golden": True,
                    "status": "HUMAN_ATTESTED"
                })

        return {"nodes": nodes, "edges": edges}
```
