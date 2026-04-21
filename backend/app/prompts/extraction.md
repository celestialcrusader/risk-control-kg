Extract atomic obligations from the following regulatory text.
Each obligation must include: id, prose, action_verb, subject_noun, clause_ref.

Text:
{{markdown_content}}

Output JSON:
{
  "obligations": [
    {
      "id": "AC-1.a",
      "prose": "The organization must limit access...",
      "action_verb": "limit",
      "subject_noun": "information system access",
      "clause_ref": "Section 3.1",
      "effective_date": null,
      "section_ref": "Section 3",
      "clause_hierarchy": {
        "parent": "Section 3",
        "level": 2,
        "path": "3.1"
      }
    }
  ]
}

Guidelines:
1. Split compound obligations into separate entries
2. Use canonical identifiers based on section numbering
3. Extract the primary action verb (e.g., must, shall, required to)
4. Identify the primary subject noun phrase
5. Include section references and hierarchy for nested clauses
6. Set effective_date to null if not explicitly stated
