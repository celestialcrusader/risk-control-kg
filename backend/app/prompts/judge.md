Evaluate the following extracted obligation for quality.
Score each criterion from 0.0 to 1.0.

Obligation:
{{obligation_json}}

Original Text:
{{original_markdown}}

Criteria:
1. Metadata Accuracy (0.0-1.0): Are action_verb, subject_noun, clause_ref correctly extracted from the original text?
2. Legal Definition Alignment (0.0-1.0): Does the obligation align with compliance and legal terminology (e.g., uses proper modal verbs like "must", "shall", "required")?
3. Rule Semantics (0.0-1.0): Is the original intent of the regulation preserved without loss or distortion?

Output ONLY valid JSON with this structure:
{
  "metadata_accuracy": <float 0.0-1.0>,
  "legal_alignment": <float 0.0-1.0>,
  "semantics": <float 0.0-1.0>,
  "overall_score": <float 0.0-1.0>,
  "status": "approved" or "repair",
  "feedback": "<string explaining what was good or what needs fixing>"
}

Scoring Guidelines:
- metadata_accuracy: 1.0 if all three fields match the source text exactly; deduct for missing or incorrect fields.
- legal_alignment: 1.0 if the obligation uses standard compliance language (must/shall/must not); deduct for informal or ambiguous language.
- semantics: 1.0 if the obligation preserves the original regulatory intent; deduct for semantic drift or over-interpretation.
- overall_score: arithmetic mean of the three criterion scores, rounded to 2 decimal places.
- status: "approved" if all three criteria >= 0.80; "repair" otherwise.
