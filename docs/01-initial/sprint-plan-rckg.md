# RCKG Platform Sprint Plan

## Sprint Planning Principles

| Parameter | Value |
|---|---|
| **Sprint Length** | 2 weeks |
| **Team Composition** | 1 Backend Lead, 2 Backend Engineers, 1 ML/AI Engineer, 1 Frontend Engineer, 1 DevOps Engineer, 1 QA Engineer (8 total) |
| **Velocity Assumption** | 40-50 story points per sprint (after team ramp-up) |
| **Sprint Goal Philosophy** | Each sprint delivers a demonstrable, working increment — not just completed tasks |

---

## Sprint 1: Infrastructure Foundation

**Sprint Goal**: Deploy a functional single-node development environment with all core infrastructure services running and verified.

**Rationale**: Before any feature work can begin, the team needs a stable, reproducible development environment. This sprint establishes the foundation for all subsequent work and validates the Docker Compose stack.

**Stories in this Sprint**: INFRA-1 through INFRA-9  
**Total Story Points**: 41

---

### INFRA-1: Docker Compose Infrastructure Stack

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: DevOps Engineer  
**Labels**: infrastructure, devops, docker  

#### User Story
> As a **developer**, I want a fully documented Docker Compose stack that spins up all infrastructure services with one command, so that I can start development immediately without manual setup.

#### Context and Background
Per TRD Section 4.2 and Section 18.1, the platform requires PostgreSQL 16, Memgraph, Qdrant, MinIO, Redis, Temporal, and Langfuse. This story establishes the base docker-compose.yml with all services, proper networking, volumes, and environment configuration.

#### Acceptance Criteria
1. Given a clean checkout, when `docker-compose up -d` is executed, then all 9 infrastructure services start successfully within 5 minutes
2. Given all services are running, when `docker-compose ps` is executed, then all containers show status "healthy" or "running"
3. Given the stack is running, when the PostgreSQL health check endpoint is queried, then it returns HTTP 200 with database connectivity
4. Given the stack is running, when the Memgraph REST API is queried, then it returns the service status
5. Given the stack is running, when the Qdrant REST API is queried, then it returns the service version
6. Documentation in `docs/01-initial/setup-guide.md` includes commands to start, stop, and view logs

#### Technical Notes
- Use official Docker Hub images for all services
- Configure proper health checks for each service
- Set memory limits: PostgreSQL 64GB, Memgraph 32GB, Qdrant auto
- Use named volumes for data persistence: `postgres_data`, `memgraph_data`, `qdrant_storage`, `minio_data`
- Network: Create dedicated `rckg-net` bridge network
- Environment variables should reference a `.env.example` file

#### Definition of Done
- [x] Code written and peer-reviewed (PR approved by at least 1 reviewer)
- [x] Unit tests written with coverage meeting project standard
- [x] Integration tests written where applicable
- [x] All acceptance criteria verified by the developer
- [x] Code merged to the main/development branch
- [x] No new linting errors or warnings introduced
- [x] Relevant documentation updated (API docs, README, inline comments)
- [x] Story demoed or verified by Product Owner / Scrum Master

#### Dependencies
- Blocked by: None
- Blocks: INFRA-2, INFRA-3

---

### INFRA-2: PostgreSQL Schema and Three-Layer Vault

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 13  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, database, postgresql  

#### User Story
> As a **backend developer**, I want the PostgreSQL database to have a complete schema with Bronze/Silver/Gold staging layers, so that data can flow through the three-tier quality model as specified in the TRD.

#### Context and Background
Per TRD Section 6 (Data Architecture — Three-Layer PostgreSQL Vault), the platform requires:
- `staging_controls` (Bronze) — raw unstructured text
- `semantic_controls` (Silver) — AI-extracted structure
- `golden_controls` (Gold) — human-verified or highly-confident AI-validated data

Additionally, bitemporal tagging (`valid_from`, `valid_to`, `ingested_at`) must be applied to all nodes.

#### Acceptance Criteria
1. Given the PostgreSQL container is running, when the schema migration script executes, then all tables (staging_controls, semantic_controls, golden_controls) are created
2. Given the schema is applied, when the `staging_controls` table is queried, then it has columns: `id`, `uuid`, `canonical_id`, `raw_file_content` (JSONB), `created_at`
3. Given the schema is applied, when the `semantic_controls` table is queried, then it has columns: `id`, `framework_name`, `group_id`, `objective_text`, `statement_text`, `action_verb`, `subject_noun`, `created_at`
4. Given the schema is applied, when the `golden_controls` table is queried, then it has bitemporal columns: `valid_from`, `valid_to`, `ingested_at`, plus all semantic_controls fields
5. Given the schema is applied, when the audit_log table is queried, then it has columns: `id`, `event_type`, `event_data` (JSONB), `actor_id`, `timestamp`, `ip_address`
6. SQL migration scripts are idempotent and can be run multiple times without error

#### Technical Notes
- Use SQLAlchemy for ORM definitions in `/backend/app/models/`
- Use Alembic for migration management
- Create index on `canonical_id` for fast lookups
- Create GIN index on JSONB columns for full-text search
- Bitemporal columns should use `TIMESTAMP WITH TIME ZONE`
- `raw_file_content` JSONB schema should include: `document_id`, `hash`, `source_path`, `content`, `metadata`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests written with coverage meeting project standard
- [x] Integration tests written where applicable
- [x] All acceptance criteria verified by the developer
- [x] Code merged to the main/development branch
- [x] No new linting errors or warnings introduced
- [x] Relevant documentation updated
- [x] Story demoed or verified by Product Owner / Scrum Master

#### Dependencies
- Blocked by: INFRA-1
- Blocks: INFRA-3, INGEST-1

---

### INFRA-3: MinIO Object Storage Configuration

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: DevOps Engineer  
**Labels**: infrastructure, storage, minio  

#### User Story
> As a **system**, I want MinIO object storage with WORM (Write-Once-Read-Many) policy on `source-regulations` bucket, so that regulatory documents cannot be tampered with and maintain audit integrity.

#### Context and Background
Per TRD Section 11.3 and Section 4.2, MinIO is used for:
- Raw PDFs and policy documents
- Markdown conversions
- Evidence artefacts

The `source-regulations` bucket must have WORM policy to satisfy regulatory audit requirements.

#### Acceptance Criteria
1. Given MinIO is running, when the S3 API is used to create bucket `source-regulations`, then the bucket is created successfully
2. Given the bucket exists, when `mc admin policy info rckg-source-worm` is executed, then the WORM policy is applied and verified
3. Given a file is uploaded to `source-regulations`, when an attempt is made to delete or modify it, then the operation is rejected with HTTP 405 Method Not Allowed
4. Given the bucket exists, when `mc ls rckg/source-regulations` is executed, then the file listing shows all uploaded documents
5. `minio-data` bucket created for temporary/unstructured storage without WORM policy
6. MinIO console accessible at `http://localhost:9001` with documented credentials

#### Technical Notes
- Use MinIO CLI (`mc`) for policy management
- WORM policy configuration: Set bucket to read-only after first write
- Configure access keys via environment variables: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
- Enable versioning on all buckets for audit trail
- Document MinIO endpoints in `.env.example`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Integration tests for MinIO operations
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-1
- Blocks: INGEST-1

---

### INFRA-4: Qdrant Vector Database Initialization

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: infrastructure, vector-database, qdrant, ml  

#### User Story
> As a **ML engineer**, I want Qdrant to have the `document_chunks` collection pre-configured with proper schema and payload indexes, so that embedding storage and retrieval can begin immediately.

#### Context and Background
Per TRD Section 4.3 and Section 3.4, Qdrant stores:
- BGE-M3 dense embeddings
- ColBERTv2.0 token-level embeddings (SQ8 quantized)

The collection schema must support:
- `document_id` payload (for filtering)
- `section` payload (for hierarchy)
- `text` payload (for display)
- `metadata` payload (JSONB)

#### Acceptance Criteria
1. Given Qdrant is running, when the `document_chunks` collection is created, then it uses HNSW indexing with cosine distance metric
2. Given the collection exists, when a sample embedding is uploaded, then it is stored with all payload fields
3. Given the collection exists, when a vector search query is executed with top-K=10, then the results are returned in < 500ms
4. Given the collection exists, when a payload filter is applied (e.g., `document_id = "doc-123"`), then only matching chunks are returned
5. Qdrant storage path configured: `/qdrant/storage` with named volume
6. Documentation in `docs/01-initial/vector-store.md` includes collection creation script

#### Technical Notes
- Collection configuration:
  ```python
  qdrant_client.create_collection(
      collection_name="document_chunks",
      vectors_config=VectorParams(size=1024, distance="Cosine"),
      hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
  )
  ```
- Enable SQ8 quantization for ColBERT embeddings to reduce storage by 4x
- Create payload index on `document_id` for fast filtering
- Use Qdrant Python client SDK for all operations

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Qdrant operations
- [x] Integration tests for vector search
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-1
- Blocks: EMBED-1, CROSSWALK-1

---

### INFRA-5: Redis Cache Layer Setup

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 3  
**Priority**: Medium  
**Assigned To**: Backend Engineer  
**Labels**: infrastructure, cache, redis  

#### User Story
> As a **backend developer**, I want Redis cache configured with appropriate TTL and eviction policies, so that frequent query results can be cached and rate limiting can be enforced.

#### Context and Background
Per TRD Section 4.2, Redis is used for:
- Query result caching (TTL 300 seconds)
- Rate-limit counters
- Session state for multi-step agent tasks

#### Acceptance Criteria
1. Given Redis is running, when a key is set with `SET key value EX 300`, then the key expires after 300 seconds
2. Given rate limit data is stored, when `INCR rate_limit:api:key` is executed, then the counter increments correctly
3. Given Redis memory is full, when a new key is set with `allkeys-lru` eviction policy, then the least recently used key is evicted
4. Redis is accessible at `localhost:6379` with documented password
5. `/backend/app/core/cache.py` includes Redis client initialization with connection pool

#### Technical Notes
- Redis configuration: `--maxmemory 8gb --maxmemory-policy allkeys-lru`
- Use Redis connection pooling (max 50 connections)
- Cache key prefix: `rckg:` for all keys
- Rate limit keys format: `rckg:rate_limit:{endpoint}:{user_id}`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for cache operations
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-1
- Blocks: None

---

### INFRA-6: Temporal Workflow Engine Deployment

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: DevOps Engineer  
**Labels**: infrastructure, temporal, workflow  

#### User Story
> As a **backend developer**, I want Temporal.io deployed with PostgreSQL backend, so that stateful workflows with HITL gates can be implemented and executed.

#### Context and Background
Per TRD Section 19, Temporal.io is the primary workflow engine for:
- Stateful, long-running, human-in-the-loop workflows
- Pause/resume capabilities
- Event sourcing and replay

Temporal requires a PostgreSQL backend for durability.

#### Acceptance Criteria
1. Given Temporal is running, when the `tctl` CLI is used to list namespaces, then the `rckg-production` namespace exists
2. Given Temporal is running, when a test workflow is started, then it completes successfully
3. Given a workflow is paused at a signal gate, when the workflow is queried, then its state shows `PAUSED` with active signal waiting
4. Temporal web UI accessible at `http://localhost:8233` with documented credentials
5. Temporal backend configured to use PostgreSQL on `localhost:5432`
6. `/backend/app/workflows/` directory initialized with base workflow templates

#### Technical Notes
- Temporal Docker image: `temporalio/auto-setup:latest`
- Required ports: 7233 (gRPC), 8233 (Web UI)
- PostgreSQL namespace configuration:
  ```bash
  tctl namespace register --name rckg-production --description "RCKG production workflows"
  ```
- Create workflow task queue: `ingestion-task-queue`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Temporal workflow registration
- [x] Integration tests for workflow execution
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-1, INFRA-2
- Blocks: WORKFLOW-1, WORKFLOW-2

---

### INFRA-7: Apache Kafka Event Bus Provisioning

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: DevOps Engineer  
**Labels**: infrastructure, kafka, messaging  

#### User Story
> As a **system**, I want Apache Kafka provisioned with proper topic configurations, so that the event-driven pipeline can asynchronously trigger downstream workflows (extraction, validation, crosswalk) without tight coupling.

#### Context and Background
Per TRD Section 19.1 and Section 4.2, Kafka is the event bus for the platform. The CTO review identified that Kafka was missing from Sprint 1 but referenced in INGEST-5. This story adds Kafka to the infrastructure stack.

**Required Topics:**
| Topic | Retention | Partitions | Purpose |
|---|---|---|---|
| `document.ingested` | 7 days | 3 | Triggers ingestion workflow |
| `extraction.completed` | 7 days | 3 | Triggers extraction validation workflow |
| `validation.completed` | 7 days | 3 | Triggers graph build workflow |
| `mapping.completed` | 7 days | 3 | Triggers gap detection |
| `coverage.alert` | 30 days | 1 | Alerting on coverage threshold breach |

#### Acceptance Criteria
1. Given Kafka is deployed via Docker Compose, when `docker-compose ps` is executed, then the Kafka container shows status "running"
2. Given Kafka is running, when a test message is published to `document.ingested`, then the message is successfully consumed by a test consumer
3. Given the Docker Compose stack, when Kafka starts, then the Zookeeper container (or KRaft mode) is also running and healthy
4. All 5 required topics are pre-created with correct retention settings
5. Kafka UI accessible at `http://localhost:8000` (Kafka Eagle or equivalent) with documented credentials
6. `/backend/app/kafka/producer.py` includes working Kafka producer with schema validation

#### Technical Notes
- Docker image: `confluentinc/cp-kafka:latest`
- Port: 9092 (broker), 2181 (Zookeeper)
- Use Kafka schema registry for message validation
- Enable ACLs for topic-level access control
- Configure `acks=all` for durability

#### Definition of Done
- [x] Kafka Docker Compose service added to `docker-compose.yml`
- [x] Topic creation script in `/infra/kafka/create-topics.sh`
- [x] Kafka producer working in backend code
- [x] Documentation in `docs/01-initial/kafka-setup.md`
- [x] Integration tests for Kafka producer/consumer

#### Dependencies
- Blocked by: INFRA-1
- Blocks: INGEST-5, EXTRACT-5

---

### INFRA-8: AI Model Download and Local Registry Setup

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: infrastructure, ml, models  

#### User Story
> As a **ML engineer**, I want 3 AI models downloaded, validated, and stored locally on the filesystem, so that the system can run fully offline in air-gapped environments without external API dependencies.

#### Context and Background
The CTO review identified that model procurement was unplanned work that would block Sprints 3 and 4. This story establishes a reproducible model download and storage pipeline.

**Models Required:**
| Model | Purpose | Storage Path |
|---|---|---|
| `BAAI/bge-m3` | Dense embeddings | `models/embeddings/bge-m3` |
| `colbertv2.0-adept` | Token-level embeddings | `models/embeddings/colbertv2.0` |
| `BAAI/bge-reranker-v2-m3` | Reranking | `models/reranker/bge-reranker` |

Note: `Qwen/Qwen3.6-35B` is already installed and running in vLLM on the DGX. It is not part of this download story.

> **CTO APPROVED**: Consolidated from dual 70B/72B to single Qwen 35B for MVP. This eliminates VRAM contention and simplifies the dev environment. Dual-judge can be added later if accuracy demands it.

#### Acceptance Criteria
1. Given the `scripts/download_models.py` script is executed, then 3 models are downloaded and verified against SHA-256 checksums
2. `models/manifest.json` tracks model versions, checksums, and download timestamps
3. Air-gapped deployment checklist documented in `docs/01-initial/model-setup.md`
4. GPU routing configuration documented (sequential judge execution via vLLM)
5. Local model loading from `models/` directory works at runtime without MinIO

#### Technical Notes
- Use `huggingface-cli download` for model downloads
- Store checksums in `models/manifest.json` for integrity verification
- For production: `vLLM` with GPU acceleration
- MinIO is for documents only — models load directly from the local filesystem

**GPU Orchestration:**
- Enforce **sequential judge execution** in Temporal workflows to avoid concurrent OOM errors
- Configure vLLM concurrency limits: `max_model_len`, `num-gpus`
- Model swapping strategy: Load judge model only when needed, unload after completion
- Dev environment: Single GPU (24GB) with 8B models only; prod environment: Multi-GPU (2x48GB+) for 35B+ models

#### Definition of Done
- [x] Model download script with checksum verification (`scripts/download_models.py`)
- [x] `models/manifest.json` tracks metadata
- [x] Air-gapped deployment procedure documented
- [x] GPU routing and sequential execution strategy documented

#### Dependencies
- Blocked by: INFRA-1 (base infrastructure must be running)
- Blocks: EXTRACT-1, DUALJUDGE-1

---

### INFRA-9: Memgraph Schema Initialization

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**labels**: infrastructure, graph, memgraph  

#### User Story
> As a **backend developer**, I want Memgraph to have its schema (node labels, indexes, constraints, SHACL shapes) pre-initialized, so that graph writes in subsequent sprints have a defined structure to validate against.

#### Context and Background
The CTO review identified that no story defined who creates the graph schema between starting Memgraph (INFRA-1) and writing nodes (CROSSWALK-4). This story fills that gap.

#### Acceptance Criteria
1. Given Memgraph is running, when the schema initialization script executes, then all node labels are created: `Obligation`, `Control`, `Regulation`, `Gap`, `Risk`, `Evidence`, `ThirdParty`, `ControlEffectiveness`
2. Given the schema is applied, when indexes are verified, then indexes exist on key properties: `obligation_id`, `control_id`, `framework_id`, `document_id`
3. Given the schema is applied, when constraints are verified, then unique constraints exist on primary keys
4. SHACL shapes are loaded from `/backend/app/shapes/` into Memgraph's SHACL extension
5. Schema version is tracked in `memgraph_schema_versions` system table
6. Schema initialization is idempotent (can be run multiple times without error)

#### Technical Notes
- Cypher for creating labels and indexes:
  ```cypher
  CREATE CONSTRAINT IF NOT EXISTS FOR (o:Obligation) REQUIRE o.obligation_id IS UNIQUE;
  CREATE INDEX IF NOT EXISTS FOR (o:Obligation) ON (o.framework_id);
  ```
- Use Memgraph's SHACL extension: `CALL shacl.load_shapes_from_file('/path/to/shapes.ttl')`
- Store schema metadata in PostgreSQL `schema_migrations` table
- Include validation query to check schema health

#### Definition of Done
- [x] Cypher schema initialization script in `/backend/app/graph/init_schema.cypher`
- [x] SHACL shapes loaded into Memgraph
- [x] Schema health check endpoint `/api/v1/graph/health`
- [x] Documentation in `docs/01-initial/graph-schema.md`
- [x] Unit tests for schema validation
