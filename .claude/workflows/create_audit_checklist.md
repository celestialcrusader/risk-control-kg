---
description: Parse policy docs into Governance Audits
---

# Create Audit Checklist

**Purpose:** Transform raw internal policy documents, regulations, or frameworks into the strict JSON schema required by the Governance Module.

**Trigger:** When the user provides a raw policy document, text snippet, or requests a new compliance checklist.

## Workflow Steps

1. **Understand Checklist Schema:**
   - The target output MUST conform to the schema defined in `deepeval_ui/docs/governance_module.md`.
   - The checklist must contain sections, testable criteria, and specific processes with definitions.

2. **Analyze Source Material:**
   - Read the provided policy document or text.
   - Extract the core requirements, separating them into logical "Sections".

3. **Formulate Testable Criteria:**
   - For each section, distil the policy rules into clear, actionable "testableCriteria".
   - An auditor must be able to verify these criteria.

4. **Define Processes & Thresholds:**
   - For each criteria, define the specific "processes".
   - Include a unique `pid` (Process ID).
   - Define a concrete `metric` and `threshold` (e.g., "100% compliance", "0 PII detected").
   - Specify the `processChecks` (what evidence the auditor should look for).

5. **Generate JSON:**
   - Construct the complete JSON document representing the checklist.
   - Ensure it is syntactically valid.

6. **Save to File:**
   - Save the finalized checklist as a `.json` file in a logical location (e.g., `deepeval_ui/docs/checklists/` or another appropriate directory) so the user can easily upload it via the UI.
