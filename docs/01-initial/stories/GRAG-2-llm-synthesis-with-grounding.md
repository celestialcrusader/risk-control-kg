# GRAG-2: LLM Synthesis with Grounding

**Type**: Story
**Sprint**: Sprint 7
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, llm, synthesis, rag

---

## User Story

> As a **ML engineer**, I want an LLM synthesizer that generates answers grounded exclusively in graph context, so that hallucinations are eliminated and all answers are traceable to source nodes.

---

## Context and Background

Per TRD Section 10.2, the LLM synthesizer must:
- Accept structured context (chunks + subgraph)
- Generate answers grounded in the context
- Include citations for all claims (node IDs, edge paths)
- Reject queries where context is insufficient (return "I don't have enough information")

---

## Acceptance Criteria

1. Given graph context is provided, when `synthesize_answer(context)` is called, then the LLM generates an answer with citations
2. Given the answer includes a claim, when the claim is verified, then it is linked to a specific node ID or edge path in the context
3. Given the context is insufficient, when `synthesize_answer(context)` is called, then the LLM returns "I don't have enough information to answer this question"
4. LLM output format: `{ "answer": "...", "citations": [{"node_id": "...", "text": "..."}, ...] }`
5. Answer generation uses local Mistral 8B via Ollama with temperature 0.3
6. All synthesis traces are logged to Langfuse with `trace_id`

---

## Technical Notes

- Synthesis prompt:
  ```
  You are a compliance assistant. Answer the following question using ONLY the provided context.
  If the context does not contain sufficient information, say "I don't have enough information to answer this question."
  
  Question: {{query}}
  
  Context:
  {{context_chunks}}
  
  Graph Context:
  {{graph_nodes}}
  {{graph_edges}}
  
  Requirements:
  1. All claims must be backed by citations
  2. Cite using the format: [Node: node_id]
  3. Do not make claims that cannot be verified from the context
  
  Output JSON:
  {
    "answer": "...",
    "citations": [
      {"node_id": "node-123", "text": "excerpt from context"}
    ]
  }
  ```
- Output validation with Pydantic:
  ```python
  class AnswerWithCitations(BaseModel):
      answer: str
      citations: List[dict]
  ```

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for synthesis with sample context
- [ ] Integration tests for Ollama/Mistral API
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: GRAG-1
- **Blocks**: GRAG-3
