# CROSSWALK-4: SATISFIES Edge Creation and Gap Node Generation

**Type**: Story
**Sprint**: Sprint 5
**Story Points**: 6
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, graph, memgraph, gaps

---

## User Story

> As a **backend developer**, I want SATISFIES edges to be created in Memgraph for successful control-obligation mappings and Gap nodes to be generated for SUBSET_OF/NO_RELATIONSHIP classifications, so that the knowledge graph accurately represents compliance relationships and deficiencies.

---

## Context and Background

Per TRD Section 5.3, the system must:
- Create `[:SATISFIES]` edges with relationship attributes (relationship_type, confidence_score, mapping_date)
- Generate `Gap` nodes for SUBSET_OF and NO_RELATIONSHIP classifications
- Apply Gap lifecycle state machine: NEW -> IN_REMEDIATION -> REMEDIATED -> VERIFIED -> CLOSED
- All graph writes must pass SHACL validation before commit

---

## Acceptance Criteria

1. Given a successful classification (EQUIVALENT_TO or SUPERSET_OF), when `create_satisfies_edge(control_id, obligation_id, relationship_type, confidence)` is called, then a SATISFIES edge is created in Memgraph with attributes
2. Given a classification is SUBSET_OF or NO_RELATIONSHIP, when `create_gap_node(obligation_id, relationship_type, severity)` is called, then a Gap node is created with `state=NEW` and `due_date` set to 30 days from now
3. Given a SATISFIES edge is created, when SHACL validation is run against the graph, then the edge passes all shape constraints
4. Given a Gold record exists in PostgreSQL, when the graph write is attempted, then the FK check passes and the commit succeeds
5. SATISFIES edge attributes: `relationship_type`, `confidence_score`, `logic_judge_score`, `technical_judge_score`, `mapping_date`, `source_document_id`
6. Gap node attributes: `gap_id`, `obligation_id`, `severity` (high/medium/low), `state`, `due_date`, `created_at`, `reviewer_id`

---

## Technical Notes

- Memgraph Cypher for SATISFIES edge:
  ```cypher
  MATCH (c:Control {id: $control_id}), (o:Obligation {id: $obligation_id})
  MERGE (c)-[r:SATISFIES {
    relationship_type: $relationship_type,
    confidence_score: $confidence,
    logic_judge_score: $logic_score,
    technical_judge_score: $tech_score,
    mapping_date: datetime()
  }]->(o)
  RETURN r
  ```
- Gap node creation:
  ```cypher
  MATCH (o:Obligation {id: $obligation_id})
  CREATE (g:Gap {
    gap_id: randomUUID(),
    obligation_id: $obligation_id,
    relationship_type: $relationship_type,
    severity: CASE
      WHEN $relationship_type = 'NO_RELATIONSHIP' THEN 'high'
      WHEN $relationship_type = 'SUBSET_OF' THEN 'medium'
      ELSE 'low'
    END,
    state: 'NEW',
    due_date: datetime({epochSeconds: timestamp() + 30*24*60*60}),
    created_at: datetime()
  })
  CREATE (g)-[:ADDRESSES_OBLIGATION]->(o)
  RETURN g
  ```
- SHACL validation before commit using Memgraph's native MAGE SHACL extension (consistent with INFRA-9)
- Use PostgreSQL `golden_controls` as source of truth before Memgraph write

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for Cypher query generation
- [ ] Integration tests for Memgraph write operations
- [ ] SHACL validation tests
- [ ] All acceptance criteria verified
- [ ] Documentation in `docs/01-initial/graph-schema.md`

---

## Dependencies

- **Blocked by**: CROSSWALK-3, INFRA-1
- **Blocks**: COVERAGE-1
