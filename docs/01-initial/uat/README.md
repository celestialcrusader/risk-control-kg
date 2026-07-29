# User Acceptance Testing

End-to-end UAT scenarios for the RCKG platform, mapped to completed stories from sprint history.

## Table of Contents

| UAT | Scenario | Covers Stories |
|-----|----------|---------------|
| UAT-01 | Infrastructure Stack Health Check | INFRA-1, INFRA-2, INFRA-3, INFRA-4, INFRA-5, INFRA-6, INFRA-7, INFRA-8, INFRA-9 |
| UAT-02 | Document Upload with Dedup and Validation | INGEST-1 |
| UAT-03 | PDF-to-Markdown Conversion | INGEST-2 |
| UAT-04 | Hybrid Chunking | INGEST-3 |
| UAT-05 | Bronze Layer Storage in MinIO | INGEST-4 |
| UAT-06 | Kafka Event Publishing | INGEST-5 |
| UAT-07 | End-to-End Ingestion Pipeline | INGEST-1, INGEST-2, INGEST-3, INGEST-4, INGEST-5 |
| UAT-08 | Obligation Extraction from Markdown | EXTRACT-1 |
| UAT-09 | Graph Schema Health and SHACL Validation | INFRA-9 |
| UAT-10 | Model Registry Validation | INFRA-8 |
| UAT-11 | Extraction Quality Loop (Judge + Repair) | EXTRACT-2, EXTRACT-3, EXTRACT-4 |
| UAT-12 | Langfuse Observability and Trace Linkage | OBSERV-1 |
| UAT-13 | DLQ Metrics and Early Warning System | DLQ-1 |
| UAT-14 | Golden 50 Local Validation Test | GOLDEN-1 |

## Prerequisites

1. All infrastructure services running:
   ```bash
   docker-compose up -d
   ```
2. Wait for all services to become healthy (~3-5 minutes)
3. vLLM serving Mistral model (or Ollama with `mistral` model loaded) for EXTRACT-1
4. Environment variables set (see `.env.example`)

## Test Data

A sample PDF regulatory document is required for UAT-02 through UAT-07. Place it at:
```
tests/test_data/sample_regulation.pdf
```

If you do not have a sample PDF, create one for smoke testing:
```bash
python3 -c "
import weasyprint
html = '''
<html><body>
<h1>Section 3: Access Control</h1>
<p>The organization must limit information system access to authorized users.</p>
<p>The organization must monitor all access for unauthorized activities.</p>
<p>The organization must revoke access for terminated employees within 24 hours.</p>
</body></html>
'''
weasyprint.HTML(string=html).write_pdf('tests/test_data/sample_regulation.pdf')
"
```

## Running Tests

Each UAT scenario below has:
- **Steps**: What to execute
- **Expected Result**: What should happen
- **Verification**: How to confirm success

Scenarios can be run independently unless noted. Infrastructure health (UAT-01) must pass before others.
