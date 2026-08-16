# Sprint Plan: Graph Maintenance, Spreading Activation ("Zombie Infection") & NLI Semantic Evaluation

**Document Version**: 1.0.0  
**Target File**: `docs/07-update-parse/graph-maintenance.md`  
**Target Sprint**: Sprint K (Graph Topology Maintenance & AI NLI Inference)  
**Status**: COMPLETED (100% QA SIGN-OFF)  
**Author**: Lead Scrum Master & AI Systems Architect  


---

## 1. Sprint Goals & Principles

- **Sprint Length**: 1-Week Rapid Engineering Sprint
- **Team Velocity**: 18 Story Points
- **Core Objectives**:
  1. **`STORY-MAINT-101` [Spreading Activation Wavefront Engine]** (5 SP): When a new control node links to a seed node, automatically propagate energy to 1-hop/2-hop neighbors ("zombie infection") and fire targeted micro-NLI checks.
  2. **`STORY-MAINT-102` [Transitive Reduction & Graph Pruning Engine]** (5 SP): Eliminate redundant multi-hop transitive triangles, collapse verified shortcuts, and prune orphaned stub nodes.
  3. **`STORY-MAINT-103` [NLI Cross-Encoder & Dual-Judge MAS-NIST Live Evaluator]** (8 SP): Execute batch NLI semantic evaluation across all MAS TRM $\longleftrightarrow$ NIST SP 800-53 pairs to elevate confidence scores to 0.75 – 0.95+ in PostgreSQL and Memgraph.

---

## 2. Story Backlog Breakdown

### `STORY-MAINT-101`: Graph Wavefront Spreading Activation Engine ("Zombie Infection")
- **Points**: 5 SP
- **Target Files**: `backend/app/services/graph_wavefront.py`, `backend/tests/test_graph_wavefront.py`
- **Acceptance Criteria**:
  - `AC-1`: Given a new node attached to a seed node with $\text{confidence} \ge 0.80$, query Memgraph for 1-hop and 2-hop connected neighbors.
  - `AC-2`: Fire targeted candidate evaluations for discovered neighbors with decaying energy factor ($E_{t+1} = E_t \times \lambda$).
  - `AC-3`: Halt propagation when energy drops below minimum threshold ($E_{\min} = 0.50$).

### `STORY-MAINT-102`: Transitive Reduction & Graph Pruning Engine
- **Points**: 5 SP
- **Target Files**: `backend/app/services/transitive_reduction.py`, `backend/tests/test_transitive_reduction.py`
- **Acceptance Criteria**:
  - `AC-1`: Detect transitive triangles ($A \rightarrow B$, $B \rightarrow C$, $A \rightarrow C$) in Memgraph and prune weaker indirect edges when direct golden edges exist.
  - `AC-2`: Perform Transitive Shortcut Collapse ($A \xrightarrow{\text{EQUIV}} B \land B \xrightarrow{\text{EQUIV}} C \implies A \xrightarrow{\text{EQUIV}} C$).
  - `AC-3`: Garbage collect orphaned `STUB_UNRESOLVED` nodes that have 0 incoming and outgoing edges.

### `STORY-MAINT-103`: MAS TRM $\longleftrightarrow$ NIST SP 800-53 Production NLI Evaluation
- **Points**: 8 SP
- **Target Files**: `backend/app/services/nli_evaluator.py`, `scripts/run_mas_nist_nli_eval.py`, `backend/tests/test_nli_evaluator.py`
- **Acceptance Criteria**:
  - `AC-1`: Evaluate candidate pairs using local AI reasoning / NLI Cross-Encoder.
  - `AC-2`: Assign mathematically rigorous set theory relations (`EQUIVALENT_TO`, `SUPERSET_OF`, `SUBSET_OF`, `INTERSECTS_WITH`, `NO_RELATIONSHIP`).
  - `AC-3`: Update PostgreSQL `obligation_framework_mappings` and Memgraph `:CROSSWALKS_TO` edges with high confidence scores ($0.75 - 0.95+$).
