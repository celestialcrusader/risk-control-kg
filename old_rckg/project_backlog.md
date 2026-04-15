# Refined Project Backlog: Risk and Control Knowledge Graph (TDD Integrated)

This backlog is organized into **Epics**, with each **User Story** explicitly defining a **TDD Mandate** to ensure all code is developed test-first, prioritizing unit and integration testing for governance, data fidelity, and structured LLM outputs.

---

## Epic 1: Core Infrastructure & TDD Foundation

**Goal**: Establish the foundational technology stack, TDD framework, and core LLM orchestration patterns.

**Definition of Done**: All mandated infrastructure components are running via Docker, communicating correctly, and all unit/integration tests are passing for core communication and structured output logic.

| Story ID | User Story                                      | TDD Mandate                                                                                                                                                            | Acceptance Criteria                                                                                                                               |
| -------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1.1**  | Containerized Environment Setup & Health Checks | **Unit Tests (Red/Green)**: Test container entrypoints and service health check responses.                                                                             | `docker-compose up` deploys all four services (Neo4j, Ollama, FastAPI, React). Backend API exposes a `/health` endpoint with a passing unit test. |
| **1.2**  | Local LLM Integration & Connectivity            | **Integration Test (Red/Green)**: Test connectivity to the Ollama API, asserting a successful response structure (even if arbitrary) to a simple query.                | FastAPI successfully prompts a local Ollama instance. The LLM client utility module has **100% unit test coverage**.                              |
| **1.3**  | Pydantic Structured Output Enforcement          | **Unit Test (Red/Green)**: Define a simple Pydantic schema (e.g., `RiskTriplet`). Write a failing test for non-conforming LLM output, then implement logic to pass it. | Structured LLM calls consistently return valid, schema-conforming Python objects.                                                                 |
| **1.4**  | Stateful Workflow Integration (LangGraph)       | **Unit Test (Red/Green)**: Implement a test for a two-step state machine transition to verify state and flow control.                                                  | A basic, stateful workflow (e.g., initial HITL review draft) is implemented using LangGraph or a similar orchestration library.                   |

---

## Epic 2: Foundational Data Modeling & Governance

**Goal**: Define the authoritative graph schema (ontology) and implement mandatory audit and versioning mechanisms.

**Definition of Done**: Neo4j is seeded with the complete, validated ontology, and audit logging is functional and tested for every write transaction.

| Story ID | User Story                             | TDD Mandate                                                                                                                                  | Acceptance Criteria                                                                                                |
| -------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **2.1**  | RCKG Ontology Definition & Constraints | **Integration Tests (Red/Green)**: Test Cypher inserts that violate mandatory properties or uniqueness constraints and assert rejection.     | All required labels (Risk, Control, Framework, Proposal, etc.) and unique ID constraints are defined and enforced. |
| **2.2**  | Transactional Audit Logging Mechanism  | **Integration Test (Red/Green)**: Assert that every successful write creates an immutable audit log entry with *who*, *when*, and *payload*. | Audit logging is mandatory for all CRUD operations via FastAPI and is fully traceable.                             |
| **2.3**  | Read-Only Data Access Layer            | **Unit Tests (Red/Green)**: Test that the read-only client cannot execute write or delete Cypher statements.                                 | Core graph data is protected via a dedicated read-only access pattern.                                             |

---

## Epic 3: Authoritative Data Ingestion (Structured)

**Goal**: Ingest high-fidelity structured data (OSCAL, Excel/CSV) with precise mapping and attribution.

**Definition of Done**: Structured data sources load successfully, validate against the ontology, and retain full source traceability with zero schema violations.

| Story ID | User Story                                 | TDD Mandate                                                                                                                                                          | Acceptance Criteria                                                                                   |
| -------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **3.1**  | OSCAL JSON-to-Graph Ingestion Pipeline     | **Acceptance Test (Given/When/Then)**: Given a valid OSCAL JSON file, when ingested, then corresponding Control nodes exist with preserved native IDs and hierarchy. | OSCAL elements map fully into the Neo4j ontology without data loss or LLM interference.               |
| **3.2**  | Structured Excel/CSV Importer & Validation | **Unit Tests (Red/Green)**: Validate normalization logic (ID casing, deduplication, merge policies) using mock datasets.                                             | Bulk loader accepts Excel/CSV files, normalizes data, and handles duplicates based on defined policy. |
| **3.3**  | Source Attribution Finalization            | **Integration Test (Red/Green)**: Assert every ingested Control/Risk node links back to a unique Source node with file/version metadata.                             | Every ingested node has a mandatory `HAS_SOURCE` relationship.                                        |

---

### Epic 4: Knowledge Graph Construction (Unstructured)
- **Goal**: Ingest unstructured data (PDFs) and extract specialized knowledge.
- **Stories**:
    - **4.1**: Unstructured Data Ingestion Pipeline (PDF/Text) - *Ingest PDFs via Docling*.
    - **4.2**: LLM-Driven Entity & Relationship Extraction - *Extract Risks/Controls via LLM*.
    - **4.3**: Graph Enrichment & Linkage - *Link extracted entities to graph*.

### Epic 5: Visual Exploration & RAG Chat
- **Goal**: Expose graph to users.
- **Stories**:
    - **5.1**: Graph Visualization API.
    - **5.2**: Context-Aware Chat API.
    - **5.3**: Ingestion API Endpoint (Upload & Process).

### Epic 6: Human-in-the-Loop & Advanced Workflows
- **Goal**: Enable human validation of graph links and generate actionable audit programs.
- **Stories**:
    - **6.1**: Human Confirmation Workflow (Draft -> Approve Nodes/Links).
    - **6.2**: Cross-Control Linkage Discovery (LLM suggests links, User confirms).
    - **6.3**: Audit Program Generator (GenAI traverses graph to build test plans).

---

## Epic 4: AI-Assisted Data Extraction (Unstructured – PDF)

**Goal**: Extract structured, relationship-rich data from unstructured documents, producing high-confidence proposals for human review.

**Definition of Done**: The PDF pipeline runs fully offline, extracts structured data, and stores outputs exclusively as Proposal nodes.

| Story ID | User Story                           | TDD Mandate                                                                                                                                                 | Acceptance Criteria                                                                          |
| -------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **4.1**  | Document Pre-Processing & Chunking   | **Unit Tests (Red/Green)**: Validate chunking accuracy, heading detection, and metadata preservation across known PDF test cases.                           | PDFs are chunked and annotated with page numbers and section metadata.                       |
| **4.2**  | LLM-Driven Extraction and Validation | **Integration Test (Red/Green)**: Provide a known PDF sentence and assert the LLM output conforms to a Pydantic `(Entity)-[Relationship]->(Entity)` schema. | LLM extraction reliably produces schema-valid entities and relationships, flagging failures. |
| **4.3**  | Staging / Proposal Node Creation     | **Integration Test (Red/Green)**: Assert that extractions create only Proposal nodes and never directly modify authoritative nodes.                         | All AI-generated knowledge is stored as Proposal nodes with status `PENDING_REVIEW`.         |

---

## Epic 5: Human-in-the-Loop (HITL) Review Workflow

**Goal**: Implement governance workflows to validate, approve, and commit AI-generated proposals.

**Definition of Done**: Users can complete end-to-end review flows with atomic commits and full auditability.

| Story ID | User Story                           | TDD Mandate                                                                                                                                          | Acceptance Criteria                                                                            |
| -------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **5.1**  | HITL State Transition Logic          | **Integration Test (Red/Green)**: Test `PENDING_REVIEW → APPROVED` transition, ensuring Proposal deletion and node creation/update occur atomically. | API enforces valid state transitions and handles concurrency locks.                            |
| **5.2**  | Review Dashboard API                 | **Unit Tests (Red/Green)**: Test proposal retrieval and correct structuring of `Current` vs `Proposed` JSON payloads.                                | FastAPI endpoints return efficient, front-end-ready proposal data.                             |
| **5.3**  | Full Traceability on Proposal Commit | **Integration Test (Red/Green)**: Assert approved nodes retain links to both Proposal (approver) and original Source.                                | Approved transactions ensure two-tier traceability: source data and human governance decision. |

---

## Epic 6: Audit & Reasoning Use Cases

**Goal**: Expose graph insights through traceable, high-performance queries supporting audit and governance use cases.

**Definition of Done**: All governance queries are implemented as FastAPI endpoints with validated, explainable outputs.

| Story ID | User Story                             | TDD Mandate                                                                                                                                                      | Acceptance Criteria                                                                        |
| -------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **6.1**  | Full Traceability Query Endpoint       | **Integration Test (Red/Green)**: Query a complex path (Risk → Control → Obligation → Source) and assert all intermediate properties are returned.               | Cypher queries return fast, explainable end-to-end lineage.                                |
| **6.2**  | LLM-Assisted Test Procedure Generation | **Integration Test (Red/Green)**: Seed a Control node and assert the LLM generates five structured test steps conforming to `TestStepList` schema.               | The system generates structured audit test steps from graph data.                          |
| **6.3**  | Control Coverage Gap Analysis          | **Integration Test (Red/Green)**: Seed five risks (four mitigated) and assert only the unmitigated risk is returned.                                             | Endpoint identifies unmitigated risks or unmapped obligations accurately.                  |
| **6.4**  | Work Program Generation and Export     | **Acceptance Test (Given/When/Then)**: Given 10 scoped controls, when export is triggered, then a single verifiable document is produced with full traceability. | The system exports formal audit work papers (Markdown/JSON) directly from the graph state. |
