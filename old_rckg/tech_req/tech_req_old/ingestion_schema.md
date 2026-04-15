# Canonical Ingestion Schema (YAML)

This document defines the standard YAML format for ingesting data into the RCKG pipeline. 
External scripts should transform their source data (CSV, PDF, etc.) into this format.

## File Structure

```yaml
metadata:
  title: "Framework Name (e.g. NIST 800-53)"
  version: "Revision 5"
  last_modified: "2023-12-01"

control-groups:
  - id: "AC"
    title: "Access Control"
    
    objectives:
      - id: "AC-1"
        title: "Policy and Procedures"
        prose: "The organization establishes..." # (Optional) High-level intent
        risk-scenario: "Lack of policy leads to..." # (Optional)
        
        statements:
          - id: "AC-1.a"
            prose: "The organization must limit information system access..."
            
  - id: "AU"
    title: "Audit"
    objectives:
      - id: "AU-1"
        title: "Audit Policy"
        statements: []

# Optional: Direct Risk/Threat Ingestion
risks:
  - id: "RISK-1"
    title: "Unmitigated Access"
    statement: "Attackers gain access due to weak passwords."
```

## Field Definitions

### Metadata
*   `title` (Required): Name of the regulation or document.
*   `version` (Optional): Version string.

### Control Groups (`control-groups`)
Logical grouping of controls.
*   `id` (Required): Short code (e.g., "AC", "1.0").
*   `title` (Required): Human readable name.

### Objectives (`objectives`)
The core reasoning unit.
*   `id` (Required): Unique Control ID (e.g., "AC-1").
*   `title` (Required): Name of the control.
*   `prose` (Optional): The main body text or "objective".
*   `statements` (List): The granular requirements.

### Statements (`statements`)
Specific actionable requirements.
*   `id` (Required): Sub-ID (e.g., "AC-1.a").
*   `prose` (Required): The requirement text.

### Risks (`risks`)
Standalone value propositions or threat scenarios.
*   `id`: Unique ID.
*   `title`: Short name.
*   `statement`: Full description.
