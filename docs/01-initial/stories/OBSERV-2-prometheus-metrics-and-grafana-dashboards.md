# OBSERV-2: Prometheus Metrics and Grafana Dashboards

**Type**: Story
**Sprint**: Sprint 9
**Story Points**: 6
**Priority**: High
**Assigned To**: DevOps Engineer
**Labels**: infrastructure, prometheus, grafana, metrics

---

## User Story

> As a **DevOps engineer**, I want Prometheus metrics and Grafana dashboards, so that I can monitor system health, pipeline performance, and AI model accuracy.

---

## Context and Background

Per TRD Section 16.1, monitoring must include:
- Pipeline metrics: ingestion rate, extraction latency, validation pass rate
- Graph metrics: node count, edge count, query latency
- AI metrics: LLM confidence scores, judge agreement rates, mapping accuracy
- Dashboards: System Health, Pipeline Performance, AI Accuracy

---

## Acceptance Criteria

1. Given the system is running, when Prometheus scrapes metrics, then all defined metrics are exposed
2. Given Grafana is configured, when dashboards are loaded, then the System Health, Pipeline Performance, and AI Accuracy dashboards display correctly
3. Pipeline metrics include: `ingestion_total`, `extraction_latency_seconds`, `validation_pass_rate`
4. Graph metrics include: `graph_node_count`, `graph_edge_count`, `query_latency_seconds`
5. AI metrics include: `llm_confidence_score`, `judge_agreement_rate`, `mapping_accuracy`
6. Alerts configured: High error rate (>5%), Low validation pass rate (<90%), High query latency (>5s)

---

## Technical Notes

- Prometheus metrics using `prometheus-client`:
  ```python
  from prometheus_client import Counter, Histogram, Gauge

  INGESTION_TOTAL = Counter('rckg_ingestion_total', 'Total documents ingested', ['status'])
  EXTRACTION_LATENCY = Histogram('rckg_extraction_latency_seconds', 'Extraction pipeline latency', buckets=[0.5, 1, 2, 5, 10, 30, 60])
  GRAPH_NODE_COUNT = Gauge('rckg_graph_node_count', 'Total nodes in the graph', ['type'])
  ```
- Grafana dashboard JSON stored in `grafana/dashboards/`

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for metrics export
- [ ] Integration tests for Prometheus scraping
- [ ] All acceptance criteria verified
- [ ] Grafana dashboards deployed and verified

---

## Dependencies

- **Blocked by**: INFRA-1, OBSERV-1
- **Blocks**: OBSERV-3
