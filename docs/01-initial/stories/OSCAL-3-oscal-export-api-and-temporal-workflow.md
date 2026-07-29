# OSCAL-3: OSCAL Export API and Temporal Workflow

**Type**: Story
**Sprint**: Sprint 8
**Story Points**: 7
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, api, oscal, temporal

---

## User Story

> As a **compliance officer**, I want an OSCAL export API endpoint and scheduled Temporal workflow, so that I can generate and export compliance artifacts on demand or on a schedule.

---

## Context and Background

Per TRD Section 19.1, OSCAL export must be accessible via:
- REST API: `POST /api/v1/oscal/export`
- Scheduled Temporal workflow: `oscal_export_workflow` with cron trigger running monthly at 00:00 UTC

---

## Acceptance Criteria

1. Given a valid export request, when `POST /api/v1/oscal/export` is called, then the OSCAL file is generated and stored in MinIO
2. Given the export is complete, when the API responds, then it returns a download URL: `{"download_url": "https://minio.internal/oscal-exports/oscal-123.json"}`
3. Given the monthly Temporal workflow runs, when it executes, then OSCAL exports are generated for all registered frameworks
4. Export includes: `requested_by`, `requested_at`, `export_type` (SSP/POA&M/SAR)
5. Export files are versioned with timestamp: `oscal-{framework_id}-{timestamp}.json`
6. Export API includes authentication: requires valid API token or OAuth2 token

---

## Technical Notes

- API endpoint:
  ```python
  @router.post("/oscal/export")
  async def export_oscal(
      request: OSCALExportRequest,
      user: User = Depends(get_current_user),
      s3: MinIO = Depends(get_minio)
  ):
      oscal_data = await generate_oscal_export(
          framework_id=request.framework_id,
          export_type=request.export_type,
          requested_by=user.id
      )
      filename = f"oscal-{request.framework_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
      s3.put_object(bucket="oscal-exports", object_name=filename, data=oscal_data)
      return {"download_url": f"/api/v1/oscal/download/{filename}", "filename": filename}
  ```
- Temporal workflow for monthly scheduled exports with cron trigger

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for OSCAL export API
- [ ] Integration tests for Temporal workflow
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: OSCAL-1, OSCAL-2
- **Blocks**: None
