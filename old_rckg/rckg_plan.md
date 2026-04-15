# Risk and Control Knowledge Graph – System Design Instruction

## Role & Objective

You are a **senior software architect and AI engineer**.

Your task is to design a **risk and control knowledge graph solution** that acts as a **system of record** for risk management, governance, and audit use cases, and that can later support **AI-driven recommendations** for GRC-related work.

The system must prioritise:
- Correctness
- Traceability
- Explainability
- Human-in-the-loop governance  

Probabilistic inference alone must **not** be treated as authoritative.

---

## Core Purpose

The solution will:

- Ingest and normalise risk, control, and framework information from multiple authoritative sources
- Synthesize and maintain this information in a **persistent, governed knowledge graph**
- Enable downstream use cases such as:
  - Risk assessment
  - Control mapping across frameworks
  - Audit work program generation
  - Governance and compliance analysis

---

## Key Functional Requirements

### 1. Multi-Source Knowledge Ingestion

The system must extract and ingest risk and control information from the following sources.

#### a) PDF Documents (e.g. NIST, ISO, regulatory publications)

- Extract obligation / requirement statements (e.g. “shall”, “should”, “must”)
- Preserve document structure and metadata:
  - Standard name
  - Version
  - Chapter / section / paragraph
- Maintain source attribution
- Flag low-confidence or ambiguous extractions for **human review**

#### b) Structured Excel Files

- Ingest curated lists of:
  - Risks
  - Controls
  - Control objectives
  - Existing mappings
- Perform:
  - Normalisation
  - De-duplication
  - Consistency checks
- Maintain:
  - Source attribution
  - Versioning
  - Change history

#### c) OSCAL Structured Data

- Treat OSCAL as a **first-class structured input**
- Map:
  - OSCAL controls
  - Control statements
  - Control relationships
- Preserve:
  - Native OSCAL identifiers
  - Hierarchy and structure
- Use OSCAL as a **backbone reference model** where applicable

---

## 2. Knowledge Graph Management (Human-in-the-Loop)

- Store all synthesised knowledge in a **Neo4j Community Edition** graph database
- Use an explicit and extensible ontology, including (but not limited to):
  - Framework / Standard
  - Requirement / Obligation
  - Risk
  - Control
  - Control Activity
  - Asset
  - Test / Evidence

### AI Usage Rules

- AI may propose:
  - New nodes
  - New relationships
  - Mappings across frameworks
- **AI must never directly commit changes**
- All AI-generated proposals must be:
  - Reviewable
  - Explainable
  - Explicitly approved by a human before persistence
- Support versioning and change tracking for:
  - Nodes
  - Relationships
  - Framework updates

---

## 3. Audit, Risk & Governance Use Cases

The system must support generation of:

- Audit work programs
- Control testing plans
- Risk-to-control coverage analysis

All outputs must:
- Be traceable back to:
  - Source documents
  - Graph relationships
- Be explainable **without relying solely on LLM reasoning**
- Allow auditors and risk professionals to validate logic independently

---

## Architecture & Technology Constraints

Use **only open-source technologies**.

### Mandatory Components

- **Graph Database:** Neo4j Community Edition
- **Local LLM Runtime:** Ollama (no external API calls)
- **Backend API:** FastAPI
- **Frontend:** React

### AI & Orchestration (Evaluate and Select)

Consider and select from the following where appropriate:
- Pydantic (schema validation, structured outputs)
- LangChain (LLM interaction patterns)
- LangGraph (stateful, multi-step AI workflows)
- FastMCP (only if Model Context Protocol is required)

Tool selection must be justified based on:
- Determinism
- Maintainability
- Observability
- Suitability for human-in-the-loop workflows

---

## Non-Functional Requirements

- Offline-capable (no dependency on cloud AI services)
- Modular and extensible design
- Clear separation between:
  - Authoritative data storage (graph database)
  - AI-assisted extraction and reasoning
  - Presentation and user interaction layer
- Designed to support future expansion into:
  - Recommendation engines
  - Impact analysis
  - Decision-support systems

---

## Expected Output

Produce a **step-by-step programming plan** that includes:

1. High-level system architecture
2. Data model and graph schema
3. Ingestion pipelines for each source type
4. AI-assisted extraction and human review workflow
5. Audit work program generation logic
6. Technology selection rationale
7. Implementation phases and milestones

---

## Design Principle Summary

- The **graph database is the source of truth**
- AI assists with extraction and reasoning, not authority
- Human oversight is mandatory for all knowledge changes
- The system must be audit-ready by design
