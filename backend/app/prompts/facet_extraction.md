You are a compliance document analysis expert. Extract exactly 6 orthogonal facets from the following regulatory/policy text chunk.

### Facet Definitions:

1. **action_verb**: The primary regulatory action verb (e.g., "limit", "monitor", "report", "encrypt", "assess", "review", "implement", "maintain", "enforce", "classify", "retain", "delete", "notify", "authorize").
2. **subject_noun**: The specific subject or object of the regulation (e.g., "access credentials", "incident reports", "data breach notifications", "vendor risk assessments", "backup tapes", "privileged accounts").
3. **domain_facet**: One of: AccessControl, DataProtection, Cryptography, IncidentResponse, BusinessContinuity, RiskManagement, VendorManagement, ChangeManagement, AssetManagement, NetworkSecurity, PhysicalSecurity, HumanResources, GeneralCompliance.
4. **modality_facet**: MANDATORY (must/shall), RECOMMENDED (should), or OPTIONAL (may/can).
5. **target_role_facet**: The role or entity responsible (e.g., "SYSTEM_ADMINISTRATOR", "DATA_PROTECTION_OFFICER", "CHIEF_INFORMATION_SECURITY_OFFICER", "COMPLIANCE_OFFICER", "ALL_EMPLOYEES", "THIRD_PARTY_VENDOR").
6. **control_nature**: PREVENTATIVE (stops bad things), DETECTIVE (finds bad things), CORRECTIVE (fixes bad things), or COMPENSATING (alternative control).

### Output Format:
Return valid JSON:
```json
{
  "action_verb": "monitor",
  "subject_noun": "privileged account activity",
  "domain_facet": "AccessControl",
  "modality_facet": "MANDATORY",
  "target_role_facet": "SYSTEM_ADMINISTRATOR",
  "control_nature": "DETECTIVE"
}
```

### Text to Analyze:
{{chunk_text}}
