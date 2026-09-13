# Risk Control Knowledge Graph (RCKG)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Memgraph](https://img.shields.io/badge/Memgraph-MAGE-blueviolet.svg)](https://memgraph.com/)
[![ModelContextProtocol](https://img.shields.io/badge/MCP-FastMCP-brightgreen.svg)](https://modelcontextprotocol.io/)

**RCKG** is an open-source, deterministic **Governance & Risk Control Knowledge Graph Harness**. It bridges probabilistic Large Language Models (LLMs) and rigorous regulatory compliance through mathematical graph topologies, set-theoretic crosswalks, and formal Natural Language Inference (NLI).

Instead of relying on ungrounded AI hallucinations to evaluate compliance, RCKG provides an immutable, graph-based single source of truth across global cybersecurity and risk frameworks (such as NIST SP 800-53 Rev 5, MAS TRM Guidelines, ISO/IEC 27001, and CIS Benchmarks).

---

## Key Capabilities

* **Deterministic Knowledge Graph (`Memgraph` / openCypher)**: Encodes obligations, controls, objectives, activities, and metrics into a strictly typed directed graph.
* **Bi-Directional 2D Crosswalk Engine**: Evaluates mappings across both *Semantic Alignment* (`EQUIVALENT_TO`, `SUBSET_OF`, `SUPERSET_OF`, `INTERSECTS`, `NO_ALIGNMENT`) and *Assurance Coverage* (`SUBSTANTIVE`, `PARTIAL`, `ADMINISTRATIVE_ONLY`).
* **Cross-Encoder NLI Grounding**: Integrates local high-throughput NLI models (e.g. ModernBERT-large-NLI) to calculate premise-to-hypothesis entailment and contradiction scores with zero external data leakage.
* **Defensible Compliance Gap Analysis**: Automatically isolates unmatched obligations (Category A Gaps) and unmapped mandates (Category B Gaps) through graph traversals rather than prompt approximations.
* **Auditor Override & Governance Outbox**: Provides an auditable human-in-the-loop override mechanism backed by PostgreSQL transactional outboxes for immutable tracking.
* **Autonomous Agent Readiness (FastMCP)**: Exposes a standardized Model Context Protocol (MCP) server with 7 governance tools, enabling autonomous coding and auditing agents to query and verify compliance constraints.

---

## Flexible Inference Architecture: Cloud API vs. Air-Gapped GPU

RCKG is designed to be **inference-agnostic**, supporting two distinct operational deployment profiles:

| Profile | Target Environment | Hardware Requirements | Setup Command |
| :--- | :--- | :--- | :--- |
| ⚡ **Mode A: Cloud API (Developer Mode)** | Any laptop (Mac/Windows/Linux), CI/CD | 4GB RAM, **0 GB VRAM** | `docker compose up -d` + `OPENAI_API_KEY` |
| 🛡️ **Mode B: On-Prem Air-Gapped (Enterprise Mode)** | Regulated banks, defense, DGX servers | NVIDIA GPU (16GB–80GB VRAM) | `docker compose -f docker-compose.yml -f docker-compose.ai.yml up -d` |

* In **Mode A**, document extraction and dual-judge evaluation route via your OpenAI-compatible API key (OpenAI `gpt-4o-mini`, Groq, Together, DeepSeek).
* In **Mode B**, local vLLM containers serve quantized open models (`Qwen3.6-35B-A3B-NVFP4`, `PaddleOCR-VL-1.6`) with zero data leaving your security boundary.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │    Regulatory Sources & Frameworks     │
                      │  (NIST SP 800-53, MAS TRM, ISO, CIS)   │
                      └───────────────────┬────────────────────┘
                                          │
                        [Multi-Format Parser Dispatcher]
                        (PDF, OSCAL, XML/OLIR, Excel Matrix)
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          Graph Compiler Engine         │
                      │    AST Builder & Clause Decompounder   │
                      └───────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │         NLI Cross-Encoder &            │
                      │         Semantic Evaluator             │
                      └───────────────────┬────────────────────┘
                                          │
                ┌─────────────────────────┴─────────────────────────┐
                ▼                                                   ▼
┌───────────────────────────────┐                   ┌───────────────────────────────┐
│     Memgraph (openCypher)     │                   │     PostgreSQL Relational     │
│   Knowledge Graph Topology    │◄─────────────────►│   Outbox & Audit Trail Logs   │
└───────────────┬───────────────┘                   └───────────────┬───────────────┘
                │                                                   │
                └─────────────────────────┬─────────────────────────┘
                                          │
                                          ▼
                ┌───────────────────────────────────────────────────┐
                │          API Gateway & FastMCP Server             │
                │  - REST API (/api/v1/crosswalk, /obligations)     │
                │  - Model Context Protocol (FastMCP 7 Tools)       │
                │  - Auditor Governance & Interactive Matrix UI     │
                └───────────────────────────────────────────────────┘
```

---

## Quickstart

### 1. Prerequisites
- Docker & Docker Compose (v2.20+)
- Python 3.12+ (if running backend services locally)

### 2. Configure Environment
Clone the repository and copy the environment template:
```bash
git clone https://github.com/celestialcrusader/risk-control-kg.git
cd risk-control-kg
cp .env.example .env
```

#### Choose Your Inference Profile in `.env`:
* **For Cloud API (Zero VRAM)**:
  ```bash
  OPENAI_API_KEY="sk-proj-your-key"
  MODEL_EXTRACTION_ENDPOINT="https://api.openai.com/v1"
  MODEL_EXTRACTION_NAME="gpt-4o-mini"
  MODEL_JUDGE_ENDPOINT="https://api.openai.com/v1"
  MODEL_JUDGE_NAME="gpt-4o-mini"
  LLM_PROVIDER="openai"
  ```
* **For Air-Gapped GPU (vLLM on-prem)**: Keep the defaults pointing to `http://localhost:8000/v1` and use the AI compose overlay in step 3.

### 3. Launch Supporting Infrastructure

**Option A (Standard / Cloud API):**
```bash
docker compose up -d memgraph postgres qdrant redis
```

**Option B (Full Air-Gapped Stack with NVIDIA vLLM Containers):**
```bash
docker compose -f docker-compose.yml -f docker-compose.ai.yml up -d
```

### 4. Local Python Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 5. Database Initialization & Seed Ingestion
Seed baseline regulatory standards (e.g. MAS TRM obligations and NIST SP 800-53 controls):
```bash
python3 backend/app/services/seed_ingestion.py
```

### 6. Run Verification Test Suite
```bash
pytest backend/tests -v
```

### 7. Start the API Server & Thin Governance UI
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```
- **Interactive Matrix UI**: [http://localhost:8000/ui](http://localhost:8000/ui)
- **OpenAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 8. Run FastMCP Server for AI Agents
```bash
python3 backend/app/mcp_server/server.py
```

---

## MCP Tool Reference for Autonomous Agents

When integrated into Claude Desktop, Antigravity, or custom agent runtimes, RCKG exposes the following tools:

| Tool | Description |
| :--- | :--- |
| `query_obligations` | Search and filter statutory obligations by framework, chapter, and keywords. |
| `query_controls` | Retrieve active framework security controls and implementation parameters. |
| `query_crosswalk` | Search 2D crosswalk linkages with semantic relations and assurance levels. |
| `get_defensible_gaps` | Graph-traversal discovery of unmatched regulatory obligations. |
| `evaluate_crosswalk_realtime` | On-demand cross-encoder NLI evaluation between requirement texts. |
| `record_auditor_override` | Human-in-the-loop approval or correction with mandatory reasoning. |
| `explain_crosswalk` | Explain multi-hop graph paths connecting a policy to controls. |

---

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.
