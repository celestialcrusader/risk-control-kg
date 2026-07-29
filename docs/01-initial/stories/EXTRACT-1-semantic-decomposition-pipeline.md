# EXTRACT-1: Semantic Decomposition Pipeline

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 13
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, llm, extraction, nlp

---

## User Story

> As a **ML engineer**, I want an LLM-driven semantic decomposition pipeline that extracts atomic rule units from regulatory text, so that each obligation can be represented as a discrete, structured node in the knowledge graph.

---

## Context and Background

Per TRD Section 7.4, the extraction pipeline must:
1. Read from Bronze layer (Markdown content)
2. Use Mistral 8B (local LLM via Ollama/vLLM) for extraction
3. Output structured JSON with fields: `id`, `prose`, `action_verb`, `subject_noun`, `clause_ref`, `effective_date`
4. Follow De Jure canonical schema

---

## Acceptance Criteria

1. Given Markdown content from Bronze layer, when `extract_obligations(markdown)` is called, then the output is a list of obligation objects
2. Given an obligation is extracted, when the object is validated, then it has all required fields: `id`, `prose`, `action_verb`, `subject_noun`, `clause_ref`
3. Given a complex regulation clause, when extraction is performed, then the output includes parent section reference and clause hierarchy
4. Extraction uses Mistral 8B model via vLLM API: `http://localhost:8000/v1/chat/completions` (dev: Ollama fallback at `localhost:11434`)
5. Output schema validated against Pydantic model in `/backend/app/schemas/obligation.py`
6. Extraction results stored in PostgreSQL `semantic_controls` (Silver layer)

---

## Technical Notes

- LLM prompt template (in `/backend/app/prompts/extraction.md`):
  ```
  Extract atomic obligations from the following regulatory text.
  Each obligation must include: id, prose, action_verb, subject_noun, clause_ref.
  
  Text:
  {{markdown_content}}
  
  Output JSON:
  [
    {
      "id": "AC-1.a",
      "prose": "The organization must limit access...",
      "action_verb": "limit",
      "subject_noun": "information system access",
      "clause_ref": "Section 3.1"
    }
  ]
  ```
- **Production (vLLM)**: Use OpenAI-compatible client for vLLM endpoint
  ```python
  from openai import OpenAI
  
  client = OpenAI(
      base_url="http://localhost:8000/v1",
      api_key="not-required"  # vLLM doesn't require auth internally
  )
  
  response = client.chat.completions.create(
      model="mistralai/Mistral-7B-Instruct-v0.3",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.3,
      max_tokens=4000,
      response_format={"type": "json_object"}
  )
  ```
  
- **Development fallback (Ollama)**: For local dev without GPU
  ```python
  import ollama
  
  response = ollama.chat(
      model='mistral',
      messages=[{"role": "user", "content": prompt}],
      options={"temperature": 0.3}
  )
  ```
  
- Temperature: 0.3 for deterministic extraction
- Max tokens: 4000 per extraction

> **IMPORTANT**: The acceptance criteria state the primary implementation uses vLLM. The Ollama client shown in the technical notes was incorrect for production. Developers should use the vLLM client as primary and only use Ollama as a development fallback when vLLM is not available.

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for extraction with sample Markdown
- [ ] Integration tests for Ollama/Mistral API
- [ ] All acceptance criteria verified
- [ ] Documentation in `docs/01-initial/extraction-pipeline.md`

---

## Dependencies

- **Blocked by**: INGEST-4, INFRA-1
- **Blocks**: EXTRACT-2
