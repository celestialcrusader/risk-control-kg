# Master Sprint Plan: RCKG Governance Intelligence & Headless-First Platform

**Target Folder**: `docs/09-mcp-ui/`  
**Standard**: Agile Scrum & TDD Execution Loop  
**Total Sprints**: 3 Sprints (Sprint P, Sprint Q, Sprint R)  
**Total Story Points**: 45 SP  
**Architecture**: Headless-First (Canonical REST API $\rightarrow$ Enterprise MCP Server $\rightarrow$ Thin Governance UI)  

---

## 1. Executive Summary & Delivery Philosophy

Following expert architectural review, RCKG adopts a **Headless-First Governance Intelligence Architecture**:
1. **Core Product (50%)**: Canonical REST API as the single source of truth for machine-verifiable regulatory mappings and 2D set-theoretic assurance coverage.
2. **Agent Interface (30%)**: Model Context Protocol (MCP) Server exposing tools, resources, and reasoning prompts to autonomous AI agents and enterprise copilots.
3. **Human Review Surface (20%)**: Thin, high-density Web UI focused strictly on human governance tasks: approval workflows (`[Approve]`, `[Override]`, `[Reject]`), coverage heatmaps, graph inspection, and immutable audit trails.

```text
                         ┌──────────────────────┐
                         │   RCKG Engine & API   │
                         │   (Core Product)     │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
           REST / JSON             MCP              Thin UI
                 │                  │                  │
                 ▼                  ▼                  ▼
          Enterprise GRC       AI Agents          Human Review
          (CI/CD, Jira)        (Copilots)         (Sign-off & Override)
```

---

## 2. Master Sprints Summary

| Sprint | Name | Goal | Points | Priority | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Sprint P** | **Canonical REST API Standardization** | Freeze and expose machine-readable REST API endpoints for obligations, controls, crosswalks, gap analysis, and human override tracking. | 15 SP | P0 (Blocker) | `COMPLETED` |
| **Sprint Q** | **Enterprise Model Context Protocol (MCP) Server** | Implement official FastMCP server wrapping the API with high-level agentic tools, resources, and reasoning prompts. | 15 SP | P0 (Blocker) | `COMPLETED` |
| **Sprint R** | **Thin Human Governance & Reviewer UI** | Build a sleek, high-performance web dashboard for mapping approvals, chapter coverage heatmaps, and interactive graph topology. | 15 SP | P0 (Blocker) | `COMPLETED` |

---

## 3. Sprint P: Canonical REST API Standardization (15 SP)

**Sprint Goal**: Standardize, test, and freeze all backend REST API endpoints with typed Pydantic schemas, pagination, and persistent audit logging.

### SPRINT-P Story Backlog
* **`STORY-MCP-101`**: Canonical Query Endpoints (`/api/v1/obligations`, `/api/v1/controls`, `/api/v1/crosswalk`) (5 SP)
* **`STORY-MCP-102`**: Governance, Gap & Evaluation Endpoints (`/api/v1/gaps`, `/api/v1/coverage/summary`, `/api/v1/evaluation/realtime`) (5 SP)
* **`STORY-MCP-103`**: Auditor Override & Immutable Audit Log Endpoint (`/api/v1/mappings/{id}/override`, `/api/v1/audit-log`) (5 SP)

---

### [STORY-MCP-101] Canonical Query Endpoints (`/api/v1/obligations`, `/api/v1/controls`, `/api/v1/crosswalk`)

**Type**: Story  
**Sprint**: Sprint P  
**Story Points**: 5 SP  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: `backend`, `api`, `rest`, `fastapi`  

#### User Story
> As an **enterprise developer or integration engineer**, I want to **query MAS obligations, active NIST controls, and their crosswalk mappings via standardized REST endpoints**, so that **downstream tools and agents can retrieve structured compliance data with filtering and pagination**.

#### Context and Background
The RCKG platform contains 85 MAS TRM obligations, 294 active NIST controls, and 767 crosswalk edges in PostgreSQL and Memgraph. This story formalizes standard, high-performance query endpoints with strict Pydantic response models and filtering capabilities (by framework, chapter, relation, coverage, and confidence).

#### Acceptance Criteria
1. Given a request to `GET /api/v1/obligations?framework=MAS-TRM`, when executed, then it returns a paginated list of obligations matching the schema with HTTP 200.
2. Given a request to `GET /api/v1/controls?framework=NIST-SP-800-53&active_only=true`, when executed, then it returns only the 294 active controls (excluding 30 withdrawn controls).
3. Given a request to `GET /api/v1/crosswalk?source_id=MAS-7.6.1`, when executed, then it returns all mapped NIST controls including `NIST-AC-5` with `semantic_relation=SUBSET_OF`, `assurance_coverage=FULL_COVERAGE`, dynamic rationale, and confidence score.
4. Given filter parameters `min_confidence=0.85` and `assurance_coverage=FULL_COVERAGE`, when querying `GET /api/v1/crosswalk`, then only matching edges are returned.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/schemas/crosswalk_api.py` | [NEW] | Standard Pydantic v2 DTOs for API requests and responses |
| `backend/app/api/v1/crosswalk_router.py` | [NEW] | FastAPI router exposing query endpoints |
| `backend/app/main.py` | [MODIFY] | Register `crosswalk_router` under prefix `/api/v1` |
| `backend/tests/test_story_mcp_101_query_api.py` | [NEW] | TDD test suite for query endpoints |

##### Definition of Done
- [ ] Pytest unit tests pass 100%.
- [ ] OpenAPI documentation accessible at `/docs`.
- [ ] Zero unhandled database connection leaks.

---

### [STORY-MCP-102] Governance, Gap & Realtime Evaluation Endpoints

**Type**: Story  
**Sprint**: Sprint P  
**Story Points**: 5 SP  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: `backend`, `api`, `gaps`, `coverage`  

#### User Story
> As a **compliance officer or risk officer**, I want to **query gap analytics, chapter coverage summaries, and trigger realtime 2D NLI evaluations via REST endpoints**, so that **I can inspect framework alignment posture and evaluate ad-hoc pairs on demand**.

#### Context and Background
Section C of our audit report identifies Category A (unmatched) and Category B (Retail Consumer Mandates) gaps. This story exposes dedicated endpoints for regulatory gap reporting, coverage percentage aggregation, and realtime pair evaluation.

#### Acceptance Criteria
1. Given a request to `GET /api/v1/gaps?framework=MAS-TRM`, when executed, then it returns Category A and Category B gap items (including `MAS-14.3.3.a`, `MAS-14.3.3.b`, `MAS-14.4.2`, `MAS-14.4.3`) with audit root causes.
2. Given a request to `GET /api/v1/coverage/summary`, when executed, then it returns aggregated totals: total obligations, active controls, percentage full/partial/no coverage, and chapter breakdown.
3. Given a request to `POST /api/v1/evaluation/realtime` with `source_text` and `target_text`, when executed, then it executes the Dual-Judge NLI evaluator and returns the 2D relation, dynamic rationale, and confidence score.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/api/v1/governance_router.py` | [NEW] | Router for gap analytics, coverage summary, and realtime evaluation |
| `backend/app/main.py` | [MODIFY] | Register `governance_router` under `/api/v1` |
| `backend/tests/test_story_mcp_102_governance_api.py` | [NEW] | TDD test suite for gap and evaluation endpoints |

---

### [STORY-MCP-103] Auditor Override & Immutable Audit Log Endpoint

**Type**: Story  
**Sprint**: Sprint P  
**Story Points**: 5 SP  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: `backend`, `api`, `audit`, `override`  

#### User Story
> As a **senior regulatory auditor**, I want to **override an AI mapping decision and record my justification in an immutable audit trail**, so that **regulatory review bodies have a verifiable log of human-in-the-loop decisions**.

#### Context and Background
Human oversight is mandatory for compliance assurance. When an auditor modifies a mapping (e.g. changes `PARTIAL_COVERAGE` to `FULL_COVERAGE` or rejects a linkage), the system must store the override and log the action with timestamp, auditor ID, previous values, new values, and rationale.

#### Acceptance Criteria
1. Given a request to `POST /api/v1/mappings/{id}/override` with `new_relation`, `new_coverage`, `override_reason`, and `auditor_id`, when executed, then the database mapping is updated, an audit log entry is persisted, and HTTP 200 is returned.
2. Given a request to `GET /api/v1/audit-log`, when executed, then it returns the chronological sequence of all human override actions.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/models/audit_log.py` | [NEW] | SQLAlchemy model for `audit_logs` table |
| `backend/app/api/v1/override_router.py` | [NEW] | Router for override mutations and audit log queries |
| `backend/tests/test_story_mcp_103_override_api.py` | [NEW] | TDD test suite for override and audit trails |

---

## 4. Sprint Q: Enterprise Model Context Protocol (MCP) Server (15 SP)

**Sprint Goal**: Implement an official FastMCP Python server exposing RCKG tools, resources, and reasoning prompt templates to autonomous AI agents.

### SPRINT-Q Story Backlog
* **`STORY-MCP-201`**: FastMCP Server Core & Tool Registry (5 SP)
* **`STORY-MCP-202`**: MCP Resource Exposer & Prompt Templates (5 SP)
* **`STORY-MCP-203`**: MCP End-to-End Test Harness & Agent Verification Client (5 SP)

---

### [STORY-MCP-201] FastMCP Server Core & Tool Registry

**Type**: Story  
**Sprint**: Sprint Q  
**Story Points**: 5 SP  
**Priority**: High  
**Assigned To**: AI / Backend Engineer  
**Labels**: `mcp`, `fastmcp`, `tools`, `ai-agent`  

#### User Story
> As an **AI agent (e.g. Claude, Antigravity, or Custom Enterprise Copilot)**, I want to **call specialized RCKG MCP tools**, so that **I can answer compliance questions, crosswalk obligations, and identify regulatory gaps autonomously**.

#### Acceptance Criteria
1. FastMCP server exposes `rckg_search_obligations(query, framework)`.
2. FastMCP server exposes `rckg_crosswalk_obligation(obligation_id, target_framework)`.
3. FastMCP server exposes `rckg_find_regulatory_gaps(framework)`.
4. FastMCP server exposes `rckg_explain_mapping(source_id, target_id)`.
5. FastMCP server exposes `rckg_evaluate_pair(source_text, target_text)`.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/mcp/server.py` | [NEW] | FastMCP server implementation exposing tools |
| `backend/app/mcp/tools.py` | [NEW] | Tool implementations connecting to the internal RCKG services |
| `backend/tests/test_story_mcp_201_mcp_tools.py` | [NEW] | Unit tests verifying all MCP tools return structured responses |

---

### [STORY-MCP-202] MCP Resource Exposer & Prompt Templates

**Type**: Story  
**Sprint**: Sprint Q  
**Story Points**: 5 SP  
**Priority**: Medium  
**Assigned To**: AI / Backend Engineer  
**Labels**: `mcp`, `resources`, `prompts`  

#### User Story
> As an **AI agent**, I want to **subscribe to RCKG URI resources and invoke standardized audit prompt templates**, so that **I have zero-friction access to full framework taxonomies and pre-built compliance workflows**.

#### Acceptance Criteria
1. MCP server exposes resource `rckg://frameworks/mas-trm` returning all MAS obligations JSON.
2. MCP server exposes resource `rckg://frameworks/nist-sp-800-53` returning all active NIST controls JSON.
3. MCP server exposes resource `rckg://audit-report/latest` returning the latest markdown crosswalk audit summary.
4. MCP server exposes prompt template `compliance_gap_analysis(framework, target_framework)`.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/mcp/resources.py` | [NEW] | Resource URI handlers |
| `backend/app/mcp/prompts.py` | [NEW] | Prompt templates for audit gap assessment |
| `backend/tests/test_story_mcp_202_mcp_resources.py` | [NEW] | Tests for URI resources and prompt resolution |

---

### [STORY-MCP-203] MCP End-to-End Test Harness & Agent Verification Client

**Type**: Story  
**Sprint**: Sprint Q  
**Story Points**: 5 SP  
**Priority**: High  
**Assigned To**: QA / SWE Engineer  
**Labels**: `mcp`, `testing`, `e2e`  

#### User Story
> As a **system architect**, I want an **automated test harness that simulates an MCP client session**, so that **I can guarantee seamless integration with Claude Desktop, Antigravity, and Cursor**.

#### Acceptance Criteria
1. Client harness starts MCP server over stdio / in-memory transport.
2. Client executes tool calls (`rckg_search_obligations`, `rckg_crosswalk_obligation`) and receives valid JSON payloads.
3. Tests confirm error handling on invalid IDs or network timeouts without crashing the MCP daemon.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/mcp/client_harness.py` | [NEW] | Test client harness for stdio / JSON-RPC simulation |
| `backend/tests/test_story_mcp_203_mcp_client_e2e.py` | [NEW] | End-to-end integration test suite |

---

## 5. Sprint R: Thin Reviewer & Governance UI (15 SP)

**Sprint Goal**: Build a high-performance web dashboard for human-in-the-loop governance: chapter heatmaps, crosswalk approval grid, and interactive topology visualizer.

### SPRINT-R Story Backlog
* **`STORY-MCP-301`**: Compliance Dashboard & Chapter Coverage Heatmap (5 SP)
* **`STORY-MCP-302`**: Crosswalk Review & Override Grid (`[Approve]`, `[Override]`, `[Reject]`) (5 SP)
* **`STORY-MCP-303`**: Interactive Graph Inspector & Topology Visualizer (5 SP)

---

### [STORY-MCP-301] Compliance Dashboard & Chapter Coverage Heatmap

**Type**: Story  
**Sprint**: Sprint R  
**Story Points**: 5 SP  
**Priority**: High  
**Assigned To**: Frontend / Full-Stack Engineer  
**Labels**: `frontend`, `dashboard`, `heatmap`  

#### User Story
> As a **compliance officer**, I want to **view executive KPI cards and chapter-by-chapter coverage heatmaps on a responsive web dashboard**, so that **I immediately understand the organization's compliance posture**.

#### Acceptance Criteria
1. Dashboard displays core KPI metrics: Total Obligations (85), Active NIST Controls (294), Full Coverage %, Partial Coverage %, True Gaps (4.7%).
2. Interactive Heatmap displays MAS TRM Chapters (e.g. Ch 1 Governance, Ch 7 Software, Ch 14 Online Services) with color-coded coverage bars.
3. Clicking a chapter filters the view to show obligations belonging to that chapter.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/static/index.html` | [NEW] | Single-Page Application (SPA) dashboard layout |
| `backend/app/static/css/app.css` | [NEW] | Rich modern dark/light CSS design system |
| `backend/app/static/js/dashboard.js` | [NEW] | Dashboard data fetching and heatmap rendering |
| `backend/tests/test_story_mcp_301_dashboard_ui.py` | [NEW] | Test suite validating UI static asset serving |

---

### [STORY-MCP-302] Crosswalk Review & Override Grid (`[Approve]`, `[Override]`, `[Reject]`)

**Type**: Story  
**Sprint**: Sprint R  
**Story Points**: 5 SP  
**Priority**: High  
**Assigned To**: Frontend / Full-Stack Engineer  
**Labels**: `frontend`, `workflow`, `override`  

#### User Story
> As a **compliance auditor**, I want to **review AI-generated crosswalk mappings in a high-density grid and execute `[Approve]`, `[Override]`, or `[Reject]` actions**, so that **human verification is recorded into the official audit trail**.

#### Acceptance Criteria
1. Grid renders MAS-NIST linkages with relation, coverage badge, confidence score, and dynamic rationale excerpt.
2. Clicking `[Approve]` marks the linkage as human-verified.
3. Clicking `[Override]` opens a modal allowing the auditor to adjust semantic relation / coverage and enter mandatory justification notes.
4. Mutation sends request to `/api/v1/mappings/{id}/override` and updates the UI state in realtime.

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/static/js/review_grid.js` | [NEW] | Review grid, pagination, filtering, and modal interaction logic |
| `backend/tests/test_story_mcp_302_review_grid.py` | [NEW] | Tests verifying grid API integration and override mutations |

---

### [STORY-MCP-303] Interactive Graph Inspector & Topology Visualizer

**Type**: Story  
**Sprint**: Sprint R  
**Story Points**: 5 SP  
**Priority**: Medium  
**Assigned To**: Frontend / Full-Stack Engineer  
**Labels**: `frontend`, `graph`, `visualization`  

#### User Story
> As a **system architect or auditor**, I want to **inspect an interactive force-directed graph canvas of mapped nodes**, so that **I can visually explore 1-to-N and N-to-1 clusters and cross-framework connections**.

#### Acceptance Criteria
1. Graph canvas renders MAS obligation nodes and NIST control nodes with color-coded directional edges.
2. Clicking a node highlights connected edges and displays node metadata in a side inspection drawer.
3. Graph supports zoom, pan, and search by ID (e.g. `MAS-14.2.1` or `NIST-IA-2`).

#### Implementation Guide
##### Files to Modify / Create
| File | Change Type | Purpose |
| :--- | :--- | :--- |
| `backend/app/static/js/graph_visualizer.js` | [NEW] | Force-directed canvas renderer using Canvas/SVG/Cytoscape |
| `backend/tests/test_story_mcp_303_graph_ui.py` | [NEW] | Tests validating graph visualizer endpoints and data payload |

---

## 6. Definition of Done & QA Verification

All stories will be executed strictly under `/tdd-story-execution`:
1. 🔴 **RED Phase**: Write failing unit/integration tests in `backend/tests/`.
2. 🟢 **GREEN Phase**: Implement minimal clean code in `backend/app/`.
3. 🔵 **REFACTOR Phase**: Optimize code and verify 100% test pass rate.
4. 📝 **Documentation**: Publish `work-log-<STORY-ID>.md` and `qa-report-<STORY-ID>.md`.
