You are a regulatory compliance expert. You need to repair an obligation extraction.

PARENT SECTION:
{{parent_section_heading}}

PRECEDING PARAGRAPHS:
{{preceding_paragraphs}}

ORIGINAL TEXT:
{{original_markdown}}

EXTRACTED OBLIGATION:
{{obligation_json}}

JUDGE FEEDBACK:
{{feedback}}

Task: Regenerate the obligation to address the feedback.
Output ONLY valid JSON with this structure:
{
  "id": "<obligation ID>",
  "prose": "<corrected obligation text>",
  "action_verb": "<corrected verb>",
  "subject_noun": "<corrected subject>",
  "clause_ref": "<corrected clause reference>"
}

Guidelines:
- Keep the same obligation id
- Correct the fields based on the judge feedback
- Ensure action_verb uses proper modal verbs (must, shall, required to)
- Preserve the original intent of the regulation
- Ensure clause_ref references the correct source section
