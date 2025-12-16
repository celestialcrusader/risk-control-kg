# Security Policy

## Supported Versions

Use this section to look up which versions of the project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in RCKG, please follow these steps:

1.  **Do not create a public issue.**
2.  Email the security team at `security@rckg.local` (Replace with actual email).
3.  Include a brief description of the vulnerability and steps to reproduce.

We will acknowledge receipt of your report within 48 hours and provide an estimated timeline for a fix.

### AI Safety

RCKG uses Local Large Language Models (LLMs).
- **Data Privacy**: Input data sent to the LLM stays within your infrastructure (localhost/Ollama). It is NOT sent to external providers.
- **Prompt Injection**: While we implement guardrails, LLMs can be susceptible to prompt injection. Users should review AI-generated risk assessments before actioning them.
