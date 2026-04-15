# Project Rules: DeepEval UI

When working on the DeepEval UI project, adhere strictly to the following rules to maintain code quality, consistency, and reliability.

## 1. Backend: AI Output & Error Handling
**Instruction:** Whenever writing backend code that parses LLM evaluations, G-Eval metrics, or JSON outputs, always use strict Pydantic validation.
- **Never trust raw LLM output.**
- Always include `try/except` blocks to handle parsing failures.
- Implement explicit fallback states or default values if the LLM output is malformed or missing expected keys.

## 2. Frontend: UI Component Standards
**Instruction:** When building React components, prioritize a premium, modern aesthetic.
- **Use the established design system.** Adhere to the existing Tailwind configurations and color palettes.
- **Prioritize Interactivity.** Never rely on basic HTML tables for complex data structures (like Governance Audit steps). Instead, build interactive, collapsible data grids or wizard-style interfaces.
- **Micro-animations.** Utilize libraries like `framer-motion` (if present) for smooth state transitions and micro-animations to create a responsive feel.

## 3. Testing: TDD First for Metrics
**Instruction:** Follow Test-Driven Development (TDD) principles when implementing new AI evaluation metrics or audit control processes.
- **Write tests first.** Do not write the implementation algorithm until the corresponding test file is created.
- **Define Fixtures.** Ensure `mock_llm_response` fixtures are defined early.
- **AAA Pattern.** Follow the standard Arrange, Act, Assert pattern for all new tests.

## Contextual Awareness
- Always refer to `docs/governance_module.md` when touching anything related to Process Audits.
- DeepEval UI relies on translating technical code concepts into user-friendly UI elements. Ensure naming conventions in the UI are human-readable (e.g., "Pass/Fail" instead of raw scores where appropriate).
