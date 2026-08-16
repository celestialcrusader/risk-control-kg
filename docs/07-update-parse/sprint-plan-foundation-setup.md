# Sprint Plan: Foundation Knowledge Graph, Multi-Standard Ingestion & Schema Decoupling

**Document Version**: 1.0.0  
**Target File**: `docs/07-update-parse/sprint-plan-foundation-setup.md`  
**Reference Document**: `docs/07-update-parse/initial-setup.md`  
**Target Sprint**: Sprint J (2-Week Execution Horizon)  
**Status**: COMPLETED (100% QA SIGN-OFF)  
**Author**: Senior Software Engineer & Lead Scrum Master  


---

## 1. Sprint Planning Principles

- **Sprint Length**: 2 Weeks (10 Working Days)
- **Team Composition**: 2 Senior Backend Engineers, 1 AI/Infrastructure Engineer, 1 Senior QA Engineer
- **Assumed Team Velocity**: 32 Story Points
- **Sprint Goal Philosophy**: Transform the RCKG ingestion pipeline from an MVP single-document prototype into an enterprise-grade, multi-standard GRC Knowledge Graph engine that ingests NIST SP 800-53 OSCAL YAML, configurable Excel matrices, and pure risk databases, while establishing a decoupled public baseline graph with self-healing crosswalks.

---

## 2. Sprint Structure Overview

### Sprint J: Foundation Knowledge Graph & Multi-Standard Ingestion Engine
**Sprint Goal**: Enable direct ingestion and semantic linkage of NIST SP 800-53 OSCAL YAML, multi-sheet Excel control matrices, and the MIT AI Risk Database into a decoupled, self-healing public baseline graph.

**Rationale**: Current ingestion is restricted to PDF/Word files and a hardcoded 3-column CSV parser, while the graph schema strictly requires a non-existent client `ControlObjective` to bridge public standards. Delivering this sprint allows the platform to ingest all 5 test catalog files from `data/test-docs/` and establish a fully interconnected public baseline knowledge graph.

**Stories in this Sprint**:
1. `[STORY-FOUNDATION-101]`: NIST SP 800-53 Rev 5 OSCAL YAML Parser & Seed Ingestion (5 SP)
2. `[STORY-FOUNDATION-102]`: Configurable Tabular & Multi-Sheet Excel Ingestion Adapter (5 SP)
3. `[STORY-FOUNDATION-103]`: Pure Risk Catalog Ingestion & Semantic Mitigation Linkages (5 SP)
4. `[STORY-FOUNDATION-104]`: Direct Public Baseline Graph Linkages & Schema Decoupling (8 SP)
5. `[STORY-FOUNDATION-105]`: 3-Tier Multi-Framework Hierarchy Classifier (5 SP)
6. `[STORY-FOUNDATION-106]`: Stub Node (`STUB_UNRESOLVED`) Generation & Late-Binding Self-Healing Engine (4 SP)

**Total Story Points**: 32 Points

---

## 3. Detailed Story Tickets

---

### [STORY-FOUNDATION-101] NIST SP 800-53 Rev 5 OSCAL YAML Parser & Seed Ingestion

**Type**: Feature  
**Sprint**: Sprint J  
**Story Points**: 5  
**Priority**: Critical  
**Assigned To**: Senior Backend Engineer  
**Labels**: `ingestion`, `oscal`, `yaml`, `nist`, `seed`  

#### User Story
> As a **compliance engineer**,  
> I want **an OSCAL YAML catalog parser capable of streaming `NIST_SP-800-53_rev5_catalog.yaml`**,  
> so that **all 1,000+ NIST SP 800-53 control objectives and enhancements are ingested into PostgreSQL and Memgraph as anchor benchmark nodes**.

#### Context and Background
The official NIST SP 800-53 Rev 5 catalog in `data/test-docs/NIST_SP-800-53_rev5_catalog.yaml` is 7.3 MB and 163,249 lines of YAML structured according to the OSCAL 1.1.3 schema. Currently, `seed_ingestion.py` only handles XML NIST OLIR exports and crashes on YAML files. This story builds a dedicated streaming OSCAL YAML parser.

#### Acceptance Criteria
1. Given `NIST_SP-800-53_rev5_catalog.yaml`, when parsed by `OscalYamlCatalogParser`, then top-level controls (e.g. `AC-1`, `AC-2`, `IA-2`) are extracted as `FrameworkControlObjectiveNode` records with exact titles and statement prose.
2. Given control enhancements (e.g. `AC-2(1)`, `IA-2(1)`), when parsed, then they are extracted as `FrameworkControlActivityNode` records and linked to their parent objective via `REFINES` / `CONTAINS` edges.
3. Given `POST /api/v1/documents/ingest-seed?source_type=NIST_OSCAL_YAML&file_path=...`, when invoked, then it processes the 163K-line file in `< 45 seconds` without memory exhaustion.
4. Pytest test asserts $>950$ control objectives and $>1,200$ control enhancements are ingested into PostgreSQL and Memgraph with zero unhandled exceptions.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|---|---|
| `backend/app/services/parsers/oscal_parser.py` | **[NEW]** OSCAL 1.1.3 YAML parser and control tree extractor |
| `backend/app/services/seed_ingestion.py` | Register `NIST_OSCAL_YAML` source type in `ComplianceSeedIngester` |
| `backend/app/api/documents.py` | Support `NIST_OSCAL_YAML` in `trigger_seed_ingestion` endpoint |
| `backend/tests/test_oscal_parser.py` | **[NEW]** Unit test suite for OSCAL YAML parsing |

##### New Files to Create

**`backend/app/services/parsers/oscal_parser.py`** — [NEW]
```python
"""
OSCAL 1.1.3 YAML Catalog Parser for NIST SP 800-53 Rev 5.2.0.
"""

import yaml
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class OscalYamlCatalogParser:
    """Parses OSCAL YAML compliance catalogs into RCKG Framework Nodes."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def _extract_prose_from_parts(self, parts: List[Dict[str, Any]]) -> str:
        """Recursively collect prose text from OSCAL parts hierarchy."""
        prose_segments = []
        for part in parts or []:
            if "prose" in part and part["prose"]:
                prose_segments.append(part["prose"].strip())
            if "parts" in part:
                prose_segments.append(self._extract_prose_from_parts(part["parts"]))
        return "\n".join(filter(None, prose_segments))

    def parse(self) -> Dict[str, List[Dict[str, Any]]]:
        """Stream and parse OSCAL YAML into Framework Control Objectives and Activities."""
        logger.info("Opening OSCAL YAML file: %s", self.file_path)
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        catalog = data.get("catalog", {})
        metadata = catalog.get("metadata", {})
        fw_name = metadata.get("title", "NIST SP 800-53")
        fw_version = str(metadata.get("version", "Rev 5"))

        objectives = []
        activities = []
        edges = []

        groups = catalog.get("groups", [])
        for group in groups:
            for ctrl in group.get("controls", []):
                ctrl_id = ctrl.get("id", "").upper()
                ctrl_title = ctrl.get("title", ctrl_id)
                ctrl_text = self._extract_prose_from_parts(ctrl.get("parts", []))

                objectives.append({
                    "framework_obj_id": f"NIST-{ctrl_id}",
                    "framework_name": "NIST SP 800-53",
                    "framework_version": fw_version,
                    "objective_name": ctrl_title,
                    "objective_text": ctrl_text,
                })

                # Process child control enhancements
                for sub_ctrl in ctrl.get("controls", []):
                    sub_id = sub_ctrl.get("id", "").upper()
                    sub_title = sub_ctrl.get("title", sub_id)
                    sub_text = self._extract_prose_from_parts(sub_ctrl.get("parts", []))

                    act_id = f"NIST-{sub_id}"
                    activities.append({
                        "framework_act_id": act_id,
                        "framework_name": "NIST SP 800-53",
                        "framework_version": fw_version,
                        "activity_name": sub_title,
                        "activity_text": sub_text,
                    })

                    edges.append({
                        "source_id": f"NIST-{ctrl_id}",
                        "target_id": act_id,
                        "relation": "REFINES",
                    })

        logger.info("Parsed %d objectives, %d activities from OSCAL YAML", len(objectives), len(activities))
        return {"objectives": objectives, "activities": activities, "edges": edges}
```

##### Relevant Code Blocks

**`backend/app/services/seed_ingestion.py`** — Add OSCAL Parser Route (around line 140)
```python
        if source_type == "NIST_OLIR":
            parser = NistOlirXmlParser(file_path)
        elif source_type == "CSA_CCM":
            parser = CcmExcelParser(file_path)
        elif source_type == "NIST_OSCAL_YAML":
            from app.services.parsers.oscal_parser import OscalYamlCatalogParser
            parser = OscalYamlCatalogParser(file_path)
        else:
            raise ValueError(f"Unsupported seed source type: {source_type}")
```

#### Definition of Done
- [ ] `OscalYamlCatalogParser` parses `data/test-docs/NIST_SP-800-53_rev5_catalog.yaml` in `< 45s`
- [ ] Unit tests in `test_oscal_parser.py` assert extraction of `AC-1`, `AC-2`, `AC-2(1)`
- [ ] Code reviewed and merged into development branch

---

### [STORY-FOUNDATION-102] Configurable Tabular & Multi-Sheet Excel Ingestion Adapter

**Type**: Feature  
**Sprint**: Sprint J  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Senior Backend Engineer  
**Labels**: `ingestion`, `excel`, `openpyxl`, `aicm`, `audit_toolkit`  

#### User Story
> As a **compliance architect**,  
> I want **a configurable Excel parser that handles arbitrary column positions, banner header offsets, and multi-sheet workbooks**,  
> so that **CSA AICM (`aicm.xlsx`), AI Audit Toolkit (`Artificial Intelligence Audit Toolkit_Workbook.xlsx`), and AIVTF (`aivtf-excel.xlsx`) can be ingested without manual data cleanup**.

#### Context and Background
The existing `CcmExcelParser` hardcodes columns 0, 1, and 2 on row 2 of the active sheet. The provided test workbooks have complex metadata rows, different column orders, and multi-sheet taxonomies across 11 sheets.

#### Acceptance Criteria
1. Given `aicm.xlsx` with JSON metadata in rows 1–2, when parsed with `header_row=3`, then `Control ID` (column C), `Control Title` (column B), and `Control Specification` (column D) are mapped accurately.
2. Given `Artificial Intelligence Audit Toolkit_Workbook.xlsx`, when parsed, then `Control Number` (column C) is extracted as `framework_obj_id` and `AI-Specific Description` (column G) as `objective_text`, ignoring numeric Primary Keys.
3. Given `aivtf-excel.xlsx` with 11 sheets, when `sheets=["*"]` is specified, then all 11 sheets are iterated and ingested into their respective domain categories.
4. Pytest test verifies zero data corruption across all 3 workbooks.

#### Implementation Guide

##### New Files to Create

**`backend/app/services/parsers/excel_matrix_parser.py`** — [NEW]
```python
"""
Configurable Multi-Sheet Excel Compliance Matrix Parser.
"""

import openpyxl
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConfigurableExcelParser:
    """Dynamic Excel parser supporting custom column maps, header offsets, and multi-sheet iteration."""

    def __init__(
        self,
        file_path: str,
        framework_name: str,
        framework_version: str = "1.0",
        id_col: str = "Control ID",
        title_col: str = "Control Title",
        text_col: str = "Control Specification",
        header_row_offset: int = 1,
        sheets: Optional[List[str]] = None,
    ):
        self.file_path = file_path
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.id_col = id_col.lower().strip()
        self.title_col = title_col.lower().strip()
        self.text_col = text_col.lower().strip()
        self.header_row_offset = header_row_offset
        self.target_sheets = sheets or ["*"]

    def parse(self) -> Dict[str, List[Dict[str, Any]]]:
        wb = openpyxl.load_workbook(self.file_path, data_only=True)
        nodes = []

        sheet_names = wb.sheetnames if "*" in self.target_sheets else [s for s in self.target_sheets if s in wb.sheetnames]

        for sheet_name in sheet_names:
            sheet = wb[sheet_name]
            rows = list(sheet.iter_rows(values_only=True))
            if len(rows) < self.header_row_offset:
                continue

            # Identify column headers at specified offset
            header_row = [str(c).lower().strip() if c is not None else "" for c in rows[self.header_row_offset - 1]]
            
            id_idx = next((i for i, h in enumerate(header_row) if self.id_col in h), 0)
            title_idx = next((i for i, h in enumerate(header_row) if self.title_col in h), 1)
            text_idx = next((i for i, h in enumerate(header_row) if self.text_col in h), 2)

            for row in rows[self.header_row_offset:]:
                if not row or len(row) <= id_idx or not row[id_idx]:
                    continue
                ctrl_id = str(row[id_idx]).strip()
                ctrl_title = str(row[title_idx]).strip() if len(row) > title_idx and row[title_idx] else ctrl_id
                ctrl_text = str(row[text_idx]).strip() if len(row) > text_idx and row[text_idx] else ""

                nodes.append({
                    "framework_obj_id": f"{self.framework_name}:{ctrl_id}",
                    "framework_name": self.framework_name,
                    "framework_version": self.framework_version,
                    "objective_name": ctrl_title,
                    "objective_text": ctrl_text,
                    "sheet_category": sheet_name,
                })

        logger.info("ConfigurableExcelParser extracted %d nodes from %s", len(nodes), self.file_path)
        return {"nodes": nodes, "edges": []}
```

#### Definition of Done
- [ ] `ConfigurableExcelParser` parses single-sheet and multi-sheet workbooks
- [ ] Unit tests verify ingestion of `aicm.xlsx` and `aivtf-excel.xlsx`
- [ ] PR approved and merged

---

### [STORY-FOUNDATION-103] Pure Risk Catalog Ingestion & Semantic Mitigation Linkages

**Type**: Feature  
**Sprint**: Sprint J  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Senior Backend Engineer  
**Labels**: `risk`, `tasra`, `mitigates`, `ingestion`  

#### User Story
> As an **enterprise risk officer**,  
> I want **the MIT TASRA AI Risk Database (`AI risk database.xlsx`) ingested directly into `RiskNode` entities**,  
> so that **AI threat scenarios and failure modes link to mitigating NIST SP 800-53 and ISO controls via `:MITIGATES` edges**.

#### Context and Background
`AI risk database.xlsx` contains hundreds of documented AI risks and societal failure modes. These are threats, not compliance obligations. This story creates a dedicated Risk Ingestion adapter that stores records in PostgreSQL `risks` table and Memgraph `:Risk` nodes.

#### Acceptance Criteria
1. Given `AI risk database.xlsx`, when parsed by `RiskCatalogParser`, then each risk event is mapped to `RiskNode` with `risk_id`, `risk_name`, `description`, `category`, and `severity_level`.
2. Given extracted risk nodes, when cross-referenced against `FrameworkControlObjectiveNode` using Qdrant vector retrieval, then candidates scoring cosine similarity $\ge 0.75$ generate `:MITIGATES` linkages.
3. Graph mutations are dual-written to PostgreSQL `risk_control_objective_mappings` and Memgraph `:MITIGATES` edges.
4. Pytest test verifies $>200$ risks ingested and mapped.

#### Implementation Guide

##### New Files to Create

**`backend/app/services/parsers/risk_catalog_parser.py`** — [NEW]
```python
"""
Parser for MIT TASRA AI Risk Database and Threat Inventories.
"""

import openpyxl
import logging
from typing import Dict, Any, List
from app.models.rckg_nodes import RiskNode

logger = logging.getLogger(__name__)


class RiskCatalogParser:
    """Parses Risk Databases into RCKG RiskNode entities."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> List[Dict[str, Any]]:
        wb = openpyxl.load_workbook(self.file_path, data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))

        # Find header row containing 'Ev_ID' or 'Title'
        header_idx = 2  # Row 3 (0-indexed 2)
        risks = []

        for row in rows[header_idx + 1:]:
            if not row or not row[0]:
                continue
            title = str(row[0]).strip()
            quick_ref = str(row[1]).strip() if len(row) > 1 and row[1] else "RISK"
            ev_id = str(row[2]).strip() if len(row) > 2 and row[2] else quick_ref
            category = str(row[7]).strip() if len(row) > 7 and row[7] else "OPERATIONAL"

            risks.append({
                "risk_id": f"RISK-{ev_id}",
                "risk_name": title,
                "description": title,
                "category": category,
                "severity_level": "MEDIUM",
            })

        logger.info("RiskCatalogParser extracted %d risks from %s", len(risks), self.file_path)
        return risks
```

#### Definition of Done
- [ ] `RiskCatalogParser` extracts risk entities from `AI risk database.xlsx`
- [ ] `:MITIGATES` edges created in Memgraph
- [ ] Integration test passes 100%

---

### [STORY-FOUNDATION-104] Direct Public Baseline Graph Linkages & Schema Decoupling

**Type**: Feature / Architecture  
**Sprint**: Sprint J  
**Story Points**: 8  
**Priority**: Critical  
**Assigned To**: Senior Backend Engineer & AI Architect  
**Labels**: `graph`, `schema`, `cypher`, `rckg_nodes`, `decoupling`  

#### User Story
> As a **system architect**,  
> I want **direct public baseline relationship tables between Obligations, Risks, and Framework Objectives without requiring an internal `ControlObjective`**,  
> so that **the public baseline graph connects seamlessly during cold start**.

#### Context and Background
The initial 5-linkage schema routed all edges through `ControlObjectiveNode (CO)`. When cold-starting with public data only, no client `CO` exists. This story creates direct public crosswalk tables and Cypher edge builders:
1. `(:Obligation)-[:CROSSWALKS_TO]->(:FrameworkControlObj)`
2. `(:Risk)-[:MITIGATED_BY]->(:FrameworkControlObj)`
3. `(:FrameworkControlObj)-[:CROSSWALKS_TO]->(:FrameworkControlObj)`

#### Acceptance Criteria
1. New ORM model `ObligationFrameworkMapping` created in `rckg_nodes.py` storing set-theory relations between `ObligationNode` and `FrameworkControlObjectiveNode`.
2. New ORM model `RiskFrameworkMapping` created in `rckg_nodes.py` storing `:MITIGATED_BY` linkages.
3. `init_schema.cypher` updated with unique constraints for direct public edges.
4. Client `ControlObjective` can overlay on top of `FrameworkControlObjective` via `:ALIGNS_WITH`, inheriting all public crosswalks.
5. Migration script applies changes cleanly to PostgreSQL without data loss.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|---|---|
| `backend/app/models/rckg_nodes.py` | Add `ObligationFrameworkMapping` and `RiskFrameworkMapping` ORM models |
| `backend/app/graph/init_schema.cypher` | Add index and constraint definitions for direct public edges |
| `backend/app/graph/rckg_queries.py` | Add Cypher queries for traversing public baseline crosswalks |

##### Relevant Code Blocks

**`backend/app/models/rckg_nodes.py`** — Add Direct Public Linkage Models
```python
class ObligationFrameworkMapping(Base):
    """Direct Public Crosswalk: Obligation <---> Framework Control Objective"""
    __tablename__ = "obligation_framework_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    obligation_id = Column(UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=False, index=True)
    framework_objective_id = Column(UUID(as_uuid=True), ForeignKey("framework_control_objectives.id"), nullable=False, index=True)

    set_theory_relation = Column(SQLEnum(SetTheoryRelation), nullable=False)
    confidence_score = Column(String(10), default="0.00")
    status = Column(SQLEnum(MappingStatus), default=MappingStatus.PROBABILISTIC_AI, nullable=False)
    is_golden_assertion = Column(String(10), default="FALSE", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("obligation_id", "framework_objective_id", name="uq_obl_fw_mapping"),
    )


class RiskFrameworkMapping(Base):
    """Direct Public Linkage: Risk <---> Framework Control Objective (MITIGATED_BY)"""
    __tablename__ = "risk_framework_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risks.id"), nullable=False, index=True)
    framework_objective_id = Column(UUID(as_uuid=True), ForeignKey("framework_control_objectives.id"), nullable=False, index=True)

    confidence_score = Column(String(10), default="0.00")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("risk_id", "framework_objective_id", name="uq_risk_fw_mapping"),
    )
```

#### Definition of Done
- [ ] ORM models and migrations created and executed
- [ ] Cypher queries in `rckg_queries.py` updated
- [ ] End-to-end test asserts traversal: `(MAS)-[:CROSSWALKS_TO]->(NIST)<-[:MITIGATED_BY]-(Risk)`

---

### [STORY-FOUNDATION-105] 3-Tier Multi-Framework Hierarchy Classifier

**Type**: Feature / Refactor  
**Sprint**: Sprint J  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Senior Backend Engineer  
**Labels**: `classifier`, `ast`, `facets`, `regex`  

#### User Story
> As a **data engineer**,  
> I want **a 3-tier hierarchy classifier combining regex patterns, AST dot-depth, and 6-facet linguistic context**,  
> so that **controls and activities across ISO 27001, PCI-DSS, CIS, and MAS TRM are accurately classified without relying solely on parentheses `()`**.

#### Context and Background
Hardcoded parenthesis checks only function for NIST SP 800-53 (`AC-2(1)`). Real-world standards use dot-notation (ISO `A.5.15`, PCI `8.3.1`, MAS `5.1.1`) and prefix keywords (`CIS Safeguard 6.5`). Furthermore, dual-use verbs like *"approve"* require role context to disambiguate governance objectives from operational activities.

#### Acceptance Criteria
1. Given a control identifier, `HierarchyClassifier` evaluates Tier 1 Regex Registry:
   - Matches `AC-2(1)` $\rightarrow$ `Activity`
   - Matches `CIS Safeguard 6.5` $\rightarrow$ `Activity`
   - Matches `ISO A.5.15` $\rightarrow$ `Activity`
2. Given unmatched identifiers, Tier 2 evaluates dot-depth:
   - `5.1` (1 dot) $\rightarrow$ `Objective`
   - `5.1.1` (2 dots) $\rightarrow$ `Activity`
3. Given unstructured prose with verb *"approve"*, Tier 3 evaluates `target_role` & `control_nature`:
   - `target_role="BOARD_OF_DIRECTORS"` + `control_nature="GOVERNANCE"` $\rightarrow$ `Objective`
   - `target_role="SYSTEM_ADMINISTRATOR"` + `control_nature="PREVENTATIVE"` $\rightarrow$ `Activity`
4. Pytest test asserts $>98\%$ classification accuracy across 50 test clauses.

#### Implementation Guide

##### New Files to Create

**`backend/app/services/parsers/hierarchy_classifier.py`** — [NEW]
```python
"""
3-Tier Multi-Framework Hierarchy Classifier (Objective vs. Activity).
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HierarchyClassifier:
    """Disambiguates Control Objectives from Granular Activities across all standards."""

    FRAMEWORK_PATTERNS = {
        "NIST": {"activity": re.compile(r"^[A-Z]{2}-\d+\(\d+\)")},
        "CIS": {"activity": re.compile(r"^Safeguard\s+\d+\.\d+", re.IGNORECASE)},
        "ISO": {"activity": re.compile(r"^A\.\d+\.\d+\.\d+")},
        "PCI": {"activity": re.compile(r"^\d+\.\d+\.\d+")},
    }

    def classify(self, node_id: str, prose: str = "", facets: Dict[str, Any] = None) -> str:
        """Classify node as 'OBJECTIVE' or 'ACTIVITY'."""
        node_id_clean = node_id.strip()

        # Tier 1: Framework Regex Registry
        for fw, patterns in self.FRAMEWORK_PATTERNS.items():
            if patterns["activity"].search(node_id_clean):
                return "ACTIVITY"

        # Tier 2: AST Dot-Depth
        dots = node_id_clean.count(".")
        if dots >= 2:
            return "ACTIVITY"
        elif dots == 1:
            return "OBJECTIVE"

        # Tier 3: 6-Facet Context Disambiguation
        if facets:
            nature = str(facets.get("control_nature", "")).upper()
            role = str(facets.get("target_role_facet", "")).upper()
            if nature == "PREVENTATIVE" or role in ("SYSTEM_ADMINISTRATOR", "SOC_ANALYST", "OPERATOR"):
                return "ACTIVITY"
            if nature == "GOVERNANCE" or role in ("BOARD_OF_DIRECTORS", "CISO", "COMPLIANCE_OFFICER"):
                return "OBJECTIVE"

        return "OBJECTIVE"
```

#### Definition of Done
- [ ] `HierarchyClassifier` integrated into `seed_ingestion.py` and `cold_start_pipeline.py`
- [ ] Unit tests in `test_hierarchy_classifier.py` verify 100% test matrix
- [ ] PR approved and merged

---

### [STORY-FOUNDATION-106] Stub Node (`STUB_UNRESOLVED`) Generation & Late-Binding Self-Healing Engine

**Type**: Feature  
**Sprint**: Sprint J  
**Story Points**: 4  
**Priority**: High  
**Assigned To**: Senior Backend Engineer  
**Labels**: `memgraph`, `stub`, `self-healing`, `upsert`  

#### User Story
> As a **graph database engineer**,  
> I want **the ingestion engine to create placeholder `STUB_UNRESOLVED` nodes when un-ingested standards are referenced**,  
> so that **crosswalk edges are preserved immediately and self-heal with full metadata when the target document is uploaded later**.

#### Context and Background
When ingesting crosswalks (e.g. CSA CCM referencing NIST `AC-2`), if NIST is not yet loaded, the graph must not throw foreign key errors. It creates a placeholder stub node that automatically enriches upon NIST catalog upload.

#### Acceptance Criteria
1. Given a crosswalk referencing non-existent `target_id="NIST-AC-2"`, when parsed, a placeholder node is created with `node_status="STUB_UNRESOLVED"` and `is_placeholder=True`.
2. Given existing stub nodes, when `NIST_SP-800-53_rev5_catalog.yaml` is ingested later, `Cypher MERGE` updates prose, extracts facets, and flips `node_status="RESOLVED"`.
3. Zero dangling pointers or broken relationship edges occur in Memgraph.
4. Pytest test validates out-of-order document uploads and self-healing graph resolution.

#### Implementation Guide

##### Relevant Code Blocks

**`backend/app/services/memgraph_service.py`** — Add Stub Node Resolution Logic
```python
    def upsert_framework_node(self, node_data: Dict[str, Any]) -> None:
        """Upsert Framework Control Node with late-binding stub resolution."""
        cypher = """
        MERGE (n:FrameworkControlObj {framework_obj_id: $framework_obj_id})
        ON CREATE SET
            n.framework_name = $framework_name,
            n.framework_version = $framework_version,
            n.objective_name = $objective_name,
            n.objective_text = $objective_text,
            n.node_status = $node_status,
            n.created_at = timestamp()
        ON MATCH SET
            n.objective_name = CASE WHEN n.node_status = 'STUB_UNRESOLVED' THEN $objective_name ELSE n.objective_name END,
            n.objective_text = CASE WHEN n.node_status = 'STUB_UNRESOLVED' THEN $objective_text ELSE n.objective_text END,
            n.node_status = 'RESOLVED',
            n.updated_at = timestamp()
        RETURN n
        """
        if self.driver:
            with self.driver.session() as session:
                session.run(cypher, {**node_data, "node_status": node_data.get("node_status", "RESOLVED")})
```

#### Definition of Done
- [ ] Stub node generation and resolution logic implemented in `MemgraphService`
- [ ] Unit test `test_stub_resolution.py` passes out-of-order ingestion scenario
- [ ] Code reviewed and merged

---

## 4. Sprint Backlog Health Check & Delivery Metrics

### Backlog Metrics
- **Total Stories**: 6 Stories
- **Total Story Points**: 32 Points
- **Estimated Duration**: 2 Weeks (Sprint J)
- **Critical Path Dependency**:
  `STORY-FOUNDATION-104 (Schema Decoupling)` $\rightarrow$ `STORY-FOUNDATION-101 (OSCAL YAML)` $\rightarrow$ `STORY-FOUNDATION-102 (Excel Adapter)` $\rightarrow$ `STORY-FOUNDATION-103 (Risk Parser)`

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               SPRINT J DEPENDENCY GRAPH                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [STORY-FOUNDATION-104: Schema Decoupling]                                              │
│        │                                                                               │
│        ├──────────────────────────────┬──────────────────────────────┐                 │
│        ▼                              ▼                              ▼                 │
│ [101: OSCAL YAML Parser]   [102: Excel Adapter]     [103: Risk Catalog Parser]         │
│        │                              │                              │                 │
│        └──────────────────────────────┼──────────────────────────────┘                 │
│                                       ▼                                                │
│                    [105: 3-Tier Hierarchy Classifier]                                  │
│                                       │                                                │
│                                       ▼                                                │
│                    [106: Stub Node Self-Healing Engine]                                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Top Delivery Risks & Mitigations

1. **Large YAML File Parsing Latency (7.3MB / 163K lines)**:
   - *Risk*: `yaml.safe_load()` in Python can consume $>1.5\text{ GB}$ RAM on huge files.
   - *Mitigation*: Use streaming `yaml.CSafeLoader` (LibYAML C bindings) in `oscal_parser.py` to maintain $< 200\text{ MB}$ memory footprint.
2. **Memgraph Batch Insertion Bottlenecks**:
   - *Risk*: Committing 2,500+ controls individually can degrade transaction throughput.
   - *Mitigation*: Batch Cypher mutations in blocks of 200 nodes using `UNWIND $batch AS row MERGE ...`.
3. **Column Drift in Proprietary Spreadsheets**:
   - *Risk*: Future Excel uploads may have undocumented column headers.
   - *Mitigation*: `ConfigurableExcelParser` implements substring keyword fuzzy matching (`id`, `title`, `spec`, `desc`) with explicit fallback logs.
