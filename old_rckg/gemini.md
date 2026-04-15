# Coding Standards & Best Practices Guide  
_For AI Agent Implementation_

## Purpose

This document defines **mandatory coding standards and best practices** that must be followed by the AI agent when designing and implementing the Risk and Control Knowledge Graph solution.

The goals are to ensure:
- Security by default
- Consistency and maintainability
- Readability and auditability
- Long-term extensibility
- Suitability for regulated, risk-sensitive environments

These practices are **not optional**.

---

## 1. Secure Coding Practices

### 1.1 General Security Principles

- Follow **least privilege** for all components
- Assume all external inputs are **untrusted**
- Prefer **deny-by-default** logic
- Avoid hard-coded secrets, credentials, or tokens
- Fail securely and explicitly

---

### 1.2 Input Validation & Sanitisation

- Validate **all inputs** at system boundaries:
  - API requests
  - Uploaded files (PDF, Excel, JSON)
  - User-submitted text
- Enforce:
  - Type validation
  - Length limits
  - Allowed character sets
- Reject unexpected fields rather than ignoring them

**Mandatory**
- Use **Pydantic models** for all API request and response schemas
- Use explicit schemas for:
  - LLM outputs
  - Graph updates
  - Review / approval actions

---

### 1.3 File Handling Security

- Restrict allowed file types explicitly:
  - PDF (`application/pdf`)
  - Excel (`.xlsx`)
  - JSON (OSCAL)
- Enforce file size limits
- Store uploads outside executable paths
- Scan files for structure integrity before processing

---

### 1.4 LLM Security & Safety

- Treat LLM output as **untrusted**
- Never execute:
  - Generated code
  - Generated queries
  - Generated system commands
- All LLM outputs must:
  - Be schema-validated
  - Be reviewed before persistence
- Guard against:
  - Prompt injection
  - Data leakage
  - Over-permissive instructions

---

### 1.5 Graph Database Safety

- Use **parameterised queries** for Neo4j (Cypher)
- Do not construct Cypher queries via string concatenation
- Restrict write operations to explicit service layers
- Log all write operations with:
  - Actor (human or AI)
  - Timestamp
  - Change summary

---

## 2. Naming, Case & Structural Consistency

### 2.1 Naming Conventions

#### Python
- `snake_case` for:
  - Variables
  - Functions
  - Module names
- `PascalCase` for:
  - Classes
  - Pydantic models
- Constants in `UPPER_SNAKE_CASE`

#### JavaScript / TypeScript (React)
- `camelCase` for:
  - Variables
  - Functions
- `PascalCase` for:
  - Components
  - Classes
- File names must match exported component names

---

### 2.2 Graph Naming Conventions

#### Node Labels
- Use **singular nouns**
- `PascalCase`
- Examples:
  - `Risk`
  - `Control`
  - `Framework`
  - `Obligation`

#### Relationship Types
- `UPPER_SNAKE_CASE`
- Verb-based and directional
- Examples:
  - `MITIGATES`
  - `SATISFIES`
  - `DERIVED_FROM`

#### Property Names
- `snake_case`
- Avoid reserved keywords
- Be explicit and descriptive

---

### 2.3 Directory & Module Structure

- Organise code by **domain**, not by technical layer
- Avoid deep nesting (>3 levels)
- Separate:
  - API layer
  - Business logic
  - AI workflows
  - Persistence logic


---

## 3. Coding Style & Readability

### 3.1 General Style Rules

- Follow **PEP 8** for Python
- Follow **ESLint / Prettier** standards for frontend code
- Prefer explicit code over clever shortcuts
- Avoid global state

---

### 3.2 Functions & Methods

- Single responsibility per function
- Keep functions small and composable
- Use explicit return types
- Avoid side effects where possible

---

### 3.3 Error Handling

- Do not suppress errors
- Catch only specific exceptions
- Provide:
  - Clear error messages
  - Actionable remediation hints
- Do not leak sensitive details in error responses

---

### 3.4 Logging & Observability

- Use structured logging
- Log:
  - Ingestion events
  - AI proposals
  - Human approvals
  - Graph mutations
- Do not log:
  - Raw documents
  - Sensitive data
  - Secrets

---

## 4. AI-Specific Engineering Practices

### 4.1 Deterministic Outputs

- Prefer:
  - Low-temperature settings
  - Constrained prompts
  - Schema-enforced outputs
- Avoid free-form text when structured output is required

---

### 4.2 Prompt Management

- Store prompts as versioned templates
- Avoid inline prompt strings in code
- Document:
  - Purpose
  - Inputs
  - Expected outputs
  - Known limitations

---

### 4.3 Human-in-the-Loop Enforcement

- No AI-generated graph changes without human approval
- Review UI must:
  - Show source evidence
  - Show confidence level
  - Show proposed diff

---

## 5. Testing & Quality Assurance

### 5.1 Automated Testing

- Write unit tests for:
  - Parsers
  - Normalisation logic
  - Graph write operations
- Write integration tests for:
  - Ingestion pipelines
  - AI-assisted workflows

---

### 5.2 Test Data Handling

- Use synthetic or anonymised data
- Never commit real client or regulatory data
- Maintain test fixtures for:
  - PDFs
  - Excel files
  - OSCAL samples

---

## 6. Documentation & Maintainability

- Every module must include:
  - Purpose
  - Inputs
  - Outputs
- Public APIs must be documented
- Complex logic must include rationale comments

---

## 7. Performance & Scalability

- Avoid loading entire documents into memory unnecessarily
- Process large files incrementally
- Batch graph writes where possible
- Measure and document performance assumptions

---

## 8. Version Control & Change Management

- Commit small, logically grouped changes
- Write meaningful commit messages
- Maintain changelogs for:
  - Graph schema
  - Ontology changes
  - AI prompt updates

---

## 9. Design Principles (Non-Negotiable)

- The graph database is the **source of truth**
- AI assists; humans decide
- Explicit is better than implicit
- Traceability is mandatory
- Audit-readiness is a first-class requirement

---

## 3. Coding Style & Readability

### 3.1 General Style Rules

- Follow **PEP 8** for Python
- Follow **ESLint / Prettier** standards for frontend code
- Prefer explicit code over clever shortcuts
- Avoid global state

---

### 3.2 Functions & Methods

- Single responsibility per function
- Keep functions small and composable
- Use explicit return types
- Avoid side effects where possible

---

### 3.3 Error Handling

- Do not suppress errors
- Catch only specific exceptions
- Provide:
  - Clear error messages
  - Actionable remediation hints
- Do not leak sensitive details in error responses

---

### 3.4 Logging & Observability

- Use structured logging
- Log:
  - Ingestion events
  - AI proposals
  - Human approvals
  - Graph mutations
- Do not log:
  - Raw documents
  - Sensitive data
  - Secrets

---

## 4. AI-Specific Engineering Practices

### 4.1 Deterministic Outputs

- Prefer:
  - Low-temperature settings
  - Constrained prompts
  - Schema-enforced outputs
- Avoid free-form text when structured output is required

---

### 4.2 Prompt Management

- Store prompts as versioned templates
- Avoid inline prompt strings in code
- Document:
  - Purpose
  - Inputs
  - Expected outputs
  - Known limitations

---

### 4.3 Human-in-the-Loop Enforcement

- No AI-generated graph changes without human approval
- Review UI must:
  - Show source evidence
  - Show confidence level
  - Show proposed diff

---

## 5. Testing & Quality Assurance

### 5.1 Automated Testing

- Write unit tests for:
  - Parsers
  - Normalisation logic
  - Graph write operations
- Write integration tests for:
  - Ingestion pipelines
  - AI-assisted workflows

---

### 5.2 Test Data Handling

- Use synthetic or anonymised data
- Never commit real client or regulatory data
- Maintain test fixtures for:
  - PDFs
  - Excel files
  - OSCAL samples

---

## 6. Documentation & Maintainability

- Every module must include:
  - Purpose
  - Inputs
  - Outputs
- Public APIs must be documented
- Complex logic must include rationale comments

---

## 7. Performance & Scalability

- Avoid loading entire documents into memory unnecessarily
- Process large files incrementally
- Batch graph writes where possible
- Measure and document performance assumptions

---

## 8. Version Control & Change Management

- Commit small, logically grouped changes
- Write meaningful commit messages
- Maintain changelogs for:
  - Graph schema
  - Ontology changes
  - AI prompt updates

---

## 9. Design Principles (Non-Negotiable)

- The graph database is the **source of truth**
- AI assists; humans decide
- Explicit is better than implicit
- Traceability is mandatory
- Audit-readiness is a first-class requirement


---

## 3. Coding Style & Readability

### 3.1 General Style Rules

- Follow **PEP 8** for Python
- Follow **ESLint / Prettier** standards for frontend code
- Prefer explicit code over clever shortcuts
- Avoid global state

---

### 3.2 Functions & Methods

- Single responsibility per function
- Keep functions small and composable
- Use explicit return types
- Avoid side effects where possible

---

### 3.3 Error Handling

- Do not suppress errors
- Catch only specific exceptions
- Provide:
  - Clear error messages
  - Actionable remediation hints
- Do not leak sensitive details in error responses

---

### 3.4 Logging & Observability

- Use structured logging
- Log:
  - Ingestion events
  - AI proposals
  - Human approvals
  - Graph mutations
- Do not log:
  - Raw documents
  - Sensitive data
  - Secrets

---

## 4. AI-Specific Engineering Practices

### 4.1 Deterministic Outputs

- Prefer:
  - Low-temperature settings
  - Constrained prompts
  - Schema-enforced outputs
- Avoid free-form text when structured output is required

---

### 4.2 Prompt Management

- Store prompts as versioned templates
- Avoid inline prompt strings in code
- Document:
  - Purpose
  - Inputs
  - Expected outputs
  - Known limitations

---

### 4.3 Human-in-the-Loop Enforcement

- No AI-generated graph changes without human approval
- Review UI must:
  - Show source evidence
  - Show confidence level
  - Show proposed diff

---

## 5. Testing & Quality Assurance

### 5.1 Automated Testing

- Write unit tests for:
  - Parsers
  - Normalisation logic
  - Graph write operations
- Write integration tests for:
  - Ingestion pipelines
  - AI-assisted workflows

---

### 5.2 Test Data Handling

- Use synthetic or anonymised data
- Never commit real client or regulatory data
- Maintain test fixtures for:
  - PDFs
  - Excel files
  - OSCAL samples

---

## 6. Documentation & Maintainability

- Every module must include:
  - Purpose
  - Inputs
  - Outputs
- Public APIs must be documented
- Complex logic must include rationale comments

---

## 7. Performance & Scalability

- Avoid loading entire documents into memory unnecessarily
- Process large files incrementally
- Batch graph writes where possible
- Measure and document performance assumptions

---

## 8. Version Control & Change Management

- Commit small, logically grouped changes
- Write meaningful commit messages
- Maintain changelogs for:
  - Graph schema
  - Ontology changes
  - AI prompt updates

---

## 9. Design Principles (Non-Negotiable)

- The graph database is the **source of truth**
- AI assists; humans decide
- Explicit is better than implicit
- Traceability is mandatory
- Audit-readiness is a first-class requirement
