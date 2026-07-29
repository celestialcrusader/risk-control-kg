# Technical Requirement Document (TRD)
## Clear Trace (CT) & Risk Control Knowledge Graph (RCKG) Suite

**Document Version:** 7.0 — Executive Control Tower & DGX Spark End-State Architecture  
**Status:** Approved / Active Technical Specification  
**Classification:** Internal — Confidential  
**Last Updated:** July 27, 2026  
**Supersedes:** `docs/01-initial/master_tech_req.md` v6.0  
**Linked Requirements:**
- BRD: [01-business-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/01-business-requirement-doc.md) v3.0
- PRD: [02-product-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/02-product-requirement-doc.md) v3.0

---

## 1. System Architecture Overview

The **Clear Trace (CT)** platform is built on a high-throughput, self-hosted microservices architecture designed to run on-premises within an **NVIDIA DGX Spark** environment.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             FRONTEND WORKSPACE (REACT / VITE)                     │
│   Tri-Panel UI: Chat Panel  │  Reasoning CoT Panel  │  Generative Canvas Panel  │
│   SDK: @ai-sdk/react v4 (DefaultChatTransport -> POST /api/v1/agent/chat)         │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ HTTP Streaming (SSE / JSON Lines)
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND SERVICE CORE                          │
│                                                                                  │
│   ┌───────────────────────────┐                ┌─────────────────────────────┐   │
│   │   Agentic Copilot API     │                │   DeepEval Testkit Engine   │   │
│   │  /api/v1/agent/chat       │                │  Runtime Metric Runner      │   │
│   └─────────────┬─────────────┘                └──────────────┬──────────────┘   │
│                 │                                             │                  │
│                 ▼                                             ▼                  │
│   ┌───────────────────────────┐                ┌─────────────────────────────┐   │
│   │   MCP Tool Bridge Layer   │                │   De Jure Ingestion &       │   │
│   │  - get_risk_profile()     │                │   Extraction Pipeline       │   │
│   │  - assess_control()       │                │  (Bronze -> Silver -> Gold) │   │
│   │  - run_deepeval_test()    │                └──────────────┬──────────────┘   │
│   └─────────────┬─────────────┘                               │                  │
└─────────────────┼─────────────────────────────────────────────┼──────────────────┘
                  │                                             │
                  ▼                                             ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            DUAL-STORAGE VAULT LAYER                              │
│                                                                                  │
│   ┌───────────────────────────────────┐    ┌─────────────────────────────────┐   │
│   │   PostgreSQL 16 (SQLModel)        │    │   Memgraph (Hot Graph DB)       │   │
│   │ • Static RCKG Tables              │    │ • Regulatory Clause Topology    │   │
│   │ • Bronze / Silver / Gold Vaults   │    │ • Multi-Hop Cypher Crosswalks   │   │
│   │ • Audit Logs & System Risk        │    │ • SHACL Constraint Validations  │   │
│   └───────────────────────────────────┘    └─────────────────────────────────┘   │
│   ┌───────────────────────────────────┐    ┌─────────────────────────────────┐   │
│   │   Qdrant (Vector DB)              │    │   MinIO (S3 Object Store)       │   │
│   │ • Dense Embeddings (BGE-M3)       │    │ • Raw Regulatory PDFs           │   │
│   │ • Clause Similarity Search        │    │ • Markdown Conversions & Proofs │   │
│   └───────────────────────────────────┘    └─────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Architecture & Relational Schema (PostgreSQL / SQLModel)

The system maintains two distinct database domains inside PostgreSQL 16:
1. **Static RCKG & AI Governance Domain** (New Phase 2 addition for Clear Trace).
2. **Three-Layer Document & Extraction Vault** (Original RCKG baseline).

### 2.1 Static RCKG & AI Governance Schema Specifications

```python
# Models defined in backend/app/models/audit.py (or __init__.py)

import enum
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ControlType(str, enum.Enum):
    PROCESS = "PROCESS"
    TECHNICAL = "TECHNICAL"

class AssessmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "N/A"

class DeploymentType(str, enum.Enum):
    INTERNAL = "INTERNAL"
    PUBLIC = "PUBLIC"

class AgencyLevel(str, enum.Enum):
    DRAFT = "DRAFT"
    HITL = "HITL"
    AUTONOMOUS = "AUTONOMOUS"

class DataSensitivity(str, enum.Enum):
    PUBLIC = "PUBLIC"
    CONFIDENTIAL = "CONFIDENTIAL"
    PII = "PII"

class AIPrinciple(SQLModel, table=True):
    """Top-level organizational values (e.g. Fairness, Robustness)."""
    __tablename__ = "ai_principles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=255)
    description: str = Field(sa_column_kwargs={"type_": "TEXT"})
    weight: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Risk(SQLModel, table=True):
    """Identified AI threats mapped to Principles."""
    __tablename__ = "rckg_risks"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    principle_id: UUID = Field(foreign_key="ai_principles.id", index=True)
    name: str = Field(max_length=255)
    description: str = Field(sa_column_kwargs={"type_": "TEXT"})
    severity_level: SeverityLevel = Field(default=SeverityLevel.MEDIUM)

class Control(SQLModel, table=True):
    """Mitigating requirements mapped to Risks."""
    __tablename__ = "rckg_controls"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    risk_id: UUID = Field(foreign_key="rckg_risks.id", index=True)
    name: str = Field(max_length=255)
    description: str = Field(sa_column_kwargs={"type_": "TEXT"})
    type: ControlType = Field(default=ControlType.TECHNICAL)
    evidence_required: Optional[str] = Field(default=None)
    deepeval_metric: Optional[str] = Field(default=None, index=True)  # e.g., 'bias', 'toxicity'

class SystemRiskProfile(SQLModel, table=True):
    """Inherent risk calculation output for a given AI solution (Zack/Wukongtai Model)."""
    __tablename__ = "system_risk_profiles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ai_solution_id: UUID = Field(index=True)
    solution_name: str = Field(max_length=255)
    facing_score: int = Field(ge=1, le=5)        # 1: Internal, 3: Ops, 5: Public
    jurisdiction_score: int = Field(ge=1, le=5)  # 1: General, 3: Privacy, 5: Strict Law
    agency_score: int = Field(ge=1, le=5)        # 1: Draft, 3: HITL, 5: Autonomous
    impact_score: int = Field(ge=1, le=5)        # 1: Low, 3: Ops breakdown, 5: Financial/Safety
    data_score: int = Field(ge=1, le=5)          # 1: Public, 3: Internal, 5: PII/Biometric
    is_black_box: bool = Field(default=False)
    calculated_score: int = Field(ge=5, le=25)
    assigned_tier: str = Field(max_length=50)    # Tier 1, Tier 2, Tier 3
    explainability_mandatory: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ControlAssessment(SQLModel, table=True):
    """Bridge table tracking Pass/Fail status for a Control on an AI Solution."""
    __tablename__ = "control_assessments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ai_solution_id: UUID = Field(index=True)
    control_id: UUID = Field(foreign_key="rckg_controls.id", index=True)
    status: AssessmentStatus = Field(default=AssessmentStatus.PENDING, index=True)
    evidence_link: Optional[str] = Field(default=None)  # MinIO URL or DeepEval Run ID
    assessed_by: str = Field(default="System")
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 3. Frontend Architecture & Vercel AI SDK v4 Migration

The frontend is built with **React**, **Vite**, **Tailwind CSS**, and **Shadcn UI**.

### 3.1 Vercel AI SDK v4 Implementation Protocol (`@ai-sdk/react` v1.x / `ai` v4.x)

To avoid breaking changes introduced in v4, all chat components must follow strict implementation rules:

```tsx
// src/components/workspace/ChatPanel.tsx
import React, { useState } from 'react';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';

export const ChatPanel: React.FC = () => {
    // 1. Explicit custom React state for input (v4 removed automatic input management)
    const [input, setInput] = useState('');

    // 2. Network Transport setup using DefaultChatTransport
    const { messages, sendMessage, isLoading } = useChat({
        transport: new DefaultChatTransport({
            api: '/api/v1/agent/chat',
            headers: {
                'Content-Type': 'application/json',
                'X-Forwarded-User': 'ciso-admin'
            }
        })
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        // 3. Manually dispatch message via sendMessage
        sendMessage({ role: 'user', content: input });
        setInput('');
    };

    return (
        <div className="flex flex-col h-full border-r">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((m) => (
                    <div key={m.id} className={`p-3 rounded-lg ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-100'}`}>
                        <div className="font-semibold text-xs uppercase">{m.role}</div>
                        <div>{m.content}</div>
                    </div>
                ))}
            </div>
            <form onSubmit={handleSubmit} className="p-4 border-t flex gap-2">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask Clear Trace Copilot..."
                    className="flex-1 bg-gray-900 border rounded px-3 py-2 text-sm focus:outline-none"
                />
                <button type="submit" disabled={isLoading} className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium">
                    Send
                </button>
            </form>
        </div>
    );
};
```

### 3.2 Generative Canvas Event Protocol
The LLM streams tool calls and structured commands to render UI widgets dynamically:

```json
{
  "type": "canvas_command",
  "action": "RENDER_WIDGET",
  "widget": "NistRadarChart",
  "props": {
    "ai_solution_id": "8a7c1234-90ab-41cd-ef12-34567890abcd",
    "solution_name": "Chatbot Alpha",
    "scores": {
      "GOVERN": 92.0,
      "MAP": 88.5,
      "MEASURE": 94.0,
      "MANAGE": 90.0
    }
  }
}
```

---

## 4. Agent API & Model Context Protocol (MCP) Tool Specifications

### 4.1 Agent Chat Endpoint (`POST /api/v1/agent/chat`)
- Accepts standard Vercel AI SDK message stream requests.
- Wraps local vLLM endpoint (`http://vllm-engine:8000/v1`) using LangChain / LlamaIndex agent execution loops.

### 4.2 Core MCP Tools Exposed to the Agent

```python
# FastAPI / MCP Tool Definitions in app/api/v1/endpoints/agent.py

@mcp_tool
def get_inherent_risk_profile(ai_solution_id: str) -> dict:
    """Fetch the 5-dimension risk profile and assigned tier for an AI Solution."""
    # Queries system_risk_profiles table
    ...

@mcp_tool
def calculate_risk_tier(
    ai_solution_id: str,
    facing: int,
    jurisdiction: int,
    agency: int,
    impact: int,
    data: int,
    is_black_box: bool
) -> dict:
    """Calculate and save Zack/Wukongtai risk score (5-25) and assign Tier 1/2/3."""
    total_score = facing + jurisdiction + agency + impact + data
    tier = "Tier 1 (Critical)" if total_score >= 20 else "Tier 2 (High)" if total_score >= 12 else "Tier 3 (Standard)"
    explainability_mandatory = (tier in ["Tier 1 (Critical)", "Tier 2 (High)"]) and is_black_box
    ...

@mcp_tool
def run_deepeval_test(ai_solution_id: str, control_id: str, metric_name: str) -> dict:
    """Trigger DeepEval metric evaluation execution for a technical control."""
    # Invokes DeepEval runner, records result in control_assessments
    ...

@mcp_tool
def get_principle_dashboard_score(ai_solution_id: Optional[str] = None) -> dict:
    """Aggregate ControlAssessments to compute AI Principle scores."""
    ...
```

---

## 5. DGX Spark Infrastructure & Deployment Architecture

### 5.1 DGX Spark Host Specifications
- **Hardware Box:** NVIDIA DGX Spark box (128GB Unified Memory, ARM64 Architecture).
- **Operating System:** Ubuntu 24.04 LTS (ARM64 Server).
- **NVIDIA Stack:** NVIDIA Driver 550+, CUDA Toolkit 13.0, NVIDIA Container Toolkit.

### 5.2 Local vLLM Inference Engine Setup
- **Model:** `Llama-3.1-Nemotron-70B-Instruct` (Quantized for 79GB VRAM footprint).
- **Compilation:** vLLM compiled natively from source on ARM64 with CUDA 13.0 support.
- **Port:** Exposed internally on `http://localhost:8000/v1`.

### 5.3 Memory Budget Allocation (`docker-compose.dgx.yml`)

```yaml
# DGX Spark total memory: 128GB
# vLLM Instance: 79GB
# Available for Docker Infrastructure Stack: ~49GB

services:
  postgres:
    mem_limit: 8gb
  memgraph:
    mem_limit: 4gb
  qdrant:
    deploy:
      resources:
        limits:
          memory: 2G
  redis:
    mem_limit: 1gb
  temporal:
    mem_limit: 1gb
  langfuse:
    mem_limit: 2gb
  kafka:
    mem_limit: 1gb
  zookeeper:
    mem_limit: 1gb
```

### 5.4 Automated CI/CD SSH Deployment Pipeline
- GitLab/Jenkins runner maintains SSH access to DGX Spark.
- On push to `main` and successful unit test run:
  1. SSH into DGX host.
  2. Execute `git pull origin main`.
  3. Run `docker compose -f docker-compose.yml -f docker-compose.dgx.yml up -d --build`.
  4. Perform healthcheck probe against `http://localhost:8000/health` and FastAPI `/healthz`.
