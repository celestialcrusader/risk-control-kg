# OSCAL-1: OSCAL Schema Mapping

**Type**: Story
**Sprint**: Sprint 8
**Story Points**: 8
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, oscal, export

---

## User Story

> As a **backend developer**, I want OSCAL 1.1.3 schema mapping that translates graph nodes to OSCAL components, so that compliance artifacts can be exported in the NIST standard format.

---

## Context and Background

Per TRD Section 13.1, OSCAL export must:
- Map Control nodes to OSCAL `control` components
- Map Obligation nodes to OSCAL `required` statements
- Include provenance metadata: confidence scores, mapping rationale, responsible_party
- Support JSON, XML, and YAML output formats

---

## Acceptance Criteria

1. Given a control and its obligations exist in the graph, when `generate_oscal_ssp(control_id)` is called, then a valid OSCAL SSP JSON is generated
2. Given the OSCAL is generated, when it is validated against NIST OSCAL schema, then validation passes without errors
3. Given the export includes mapping metadata, when the JSON is inspected, then it includes `confidence_score`, `logic_judge_score`, `technical_judge_score` fields
4. Export includes `responsible_party` field for each mapping
5. Output formats: JSON (default), XML, YAML
6. OSCAL output stored in MinIO `oscal-exports` bucket

---

## Technical Notes

- OSCAL SSP structure follows NIST OSCAL 1.1.3 specification
- Use `trestle` Python library (IBM's open-source OSCAL tool) or `jsonschema` directly
- Validation against NIST OSCAL 1.1.3 schema:
  ```python
  from trestle.core.validator import Validator
  from trestle.oscal import SSP
  
  ssp = SSP.oscal_read("ssp.json")
  validator = Validator()
  validation_results = validator.run(ssp)
  if not validation_results.is_valid:
      raise OSCALValidationError(f"Validation failed: {validation_results.message}")
  ```

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for OSCAL schema mapping
- [ ] Integration tests for OSCAL validation
- [ ] All acceptance criteria verified
- [ ] Documentation in `docs/01-initial/oscal-export.md`

---

## Dependencies

- **Blocked by**: CROSSWALK-4
- **Blocks**: OSCAL-2
