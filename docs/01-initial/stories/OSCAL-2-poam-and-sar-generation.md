# OSCAL-2: POA&M and SAR Generation

**Type**: Story
**Sprint**: Sprint 8
**Story Points**: 7
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, oscal, export

---

## User Story

> As a **compliance officer**, I want Plan of Action and Milestones (POA&M) and Security Assessment Report (SAR) OSCAL exports, so that gaps and test results can be documented in the NIST standard format.

---

## Context and Background

Per TRD Section 13.2, OSCAL exports must include:
- POA&M: Lists all gaps (SUBSET_OF, NO_RELATIONSHIP) with remediation plans
- SAR: Documents control testing results and effectiveness scores
- Both formats follow NIST OSCAL 1.1.3 specification

---

## Acceptance Criteria

1. Given gaps exist in the system, when `generate_oscal_poam(framework_id)` is called, then a valid OSCAL POA&M JSON is generated
2. Given the POA&M is generated, when it is validated against NIST OSCAL schema, then validation passes
3. POA&M includes: gap_id, obligation_id, severity, state, due_date, responsible_party, remediation_plan
4. Given control tests exist, when `generate_oscal_sar(framework_id)` is called, then a valid OSCAL SAR JSON is generated
5. SAR includes: test_id, control_id, test_date, result, tester_id, evidence_references
6. Export includes provenance metadata for all fields

---

## Technical Notes

- POA&M OSCAL structure includes gap details with remediation milestones
- SAR OSCAL structure includes assessed controls with findings
- Use same validation approach as OSCAL-1 with `trestle` library

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for POA&M generation
- [ ] Unit tests for SAR generation
- [ ] Integration tests for OSCAL validation
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: OSCAL-1
- **Blocks**: OSCAL-3
