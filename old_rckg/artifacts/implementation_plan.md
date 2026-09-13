# Epic 6: Human-in-the-Loop & Advanced Workflows

## Goal
Enable users to review, approve, or reject AI-generated graph elements (Risks, Controls, Links) before they become authoritative.

## Proposed Changes

### Data Model
- **Schema Update**: Add `status` property to all `Risk`, `Control`, `Definition` nodes.
    - Values: `APPROVED` (Authoritative), `DRAFT` (AI-Generated/Pending).
    - Default for Adapter Iniest: `APPROVED`.
    - Default for GraphEnricher: `DRAFT`.

### Backend Components

#### [MODIFY] [ingest/enricher.py](file:///home/rckg/coding/rckg/backend/app/ingest/enricher.py)
- Update `create_node_tx`:
    - Set `status='DRAFT'` when creating nodes from LLM extraction.

#### [NEW] [api/routers/approvals.py](file:///home/rckg/coding/rckg/backend/app/api/routers/approvals.py)
- `GET /api/approvals`:
    - Query: `MATCH (n) WHERE n.status = 'DRAFT' RETURN n`
    - Returns list of draft/pending items with context (what they are linked to).
- `POST /api/approvals/{element_id}/approve`:
    - Action: `MATCH (n {id: $element_id}) SET n.status = 'APPROVED'`
- `POST /api/approvals/{element_id}/reject`:
    - Action: `MATCH (n {id: $element_id}) DETACH DELETE n`
- `PUT /api/approvals/{element_id}`:
    - Input: `{"name": "...", "description": "...", "status": "APPROVED"}`
    - Action: Update properties and status. Allows correction before approval.

### Verification Plan
1. **Unit Test**: `test_api_approvals.py`
    - Create a DRAFT node.
    - Verify it appears in `GET /api/approvals`.
    - Approve it -> Verify status changes.
    - Reject another -> Verify deletion.

### Audit Program Generator (Story 6.3)

#### [NEW] [api/routers/audit.py](file:///home/rckg/coding/rckg/backend/app/api/routers/audit.py)
- `POST /api/audit/generate`:
    - Input: `{"topic": "str"}`
    - Logic: Search Graph -> RAG Synthesis -> Structured Test Plan.

#### [NEW] [core/generator.py](file:///home/rckg/coding/rckg/backend/app/core/generator.py)
- `AuditGenerator`:
    - `generate_program(topic)`:
        - Query: Find Controls where name/desc contains topic keywords.
        - Prompt: "Generate audit steps for these controls."
2. **UAT Scenario**:
    - Ingest PDF.
    - Check `/api/approvals` for extracted drafts.
    - Approve one.
    - Check `/api/graph` (Drafts might be excluded or visually distinct).
