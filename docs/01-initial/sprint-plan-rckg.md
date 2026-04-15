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
> As a **ML engineer**, I want all AI models downloaded, validated, and stored in a local MinIO registry, so that the system can run fully offline in air-gapped environments without external API dependencies.

#### Context and Background
The CTO review identified that model procurement was unplanned work that would block Sprints 3 and 4. This story establishes a reproducible model download and storage pipeline.

**Models Required:**
| Model | Purpose | Size (4-bit) | Storage Path |
|---|---|---|---|
| `BAAI/bge-m3` | Dense embeddings | 4.7GB | `models/embeddings/bge-m3` |
| `colbertv2.0-adept` | Token-level embeddings | 2.1GB | `models/embeddings/colbertv2.0` |
| `BAAI/bge-reranker-v2-m3` | Reranking | 1.5GB | `models/reranker/bge-reranker` |
| `mistralai/Mistral-7B-Instruct-v0.3` | Extraction | 4.3GB | `models/extraction/mistral-7b` |
| `qwen/Qwen2.5-35B-Instruct` | **Single Judge (prod)** | **18GB** | `models/judge/qwen-35b` |

> **CTO APPROVED**: Consolidated from dual 70B/72B to single Qwen 35B for MVP. This eliminates VRAM contention and simplifies the dev environment. Dual-judge can be added later if accuracy demands it.

#### Acceptance Criteria
1. Given the `scripts/download_models.py` script is executed, then all 5 models are downloaded and verified against SHA-256 checksums
2. Given models are downloaded, when stored in MinIO, then they are accessible via internal registry URL without external internet access
3. Given the local registry, when the system starts, then model loading time is < 30 seconds (from cache)
4. Models are quantized appropriately: 8B/7B models at 4-bit for dev, 70B at 4-bit for prod, Qwen 35B at 4-bit for prod
5. `models/manifest.json` tracks model versions, checksums, and download timestamps
6. Air-gapped deployment checklist includes steps for model pre-loading
7. **GPU routing configuration documented**: Sequential execution strategy for judge models to avoid VRAM contention

#### Technical Notes
- Use `huggingface-cli download` for model downloads
- Quantization: `bitsandbytes` for 4-bit quantization
- Store checksums in `models/manifest.json` for integrity verification
- Consider using `ollama` for local model serving in dev environment
- For production: `vLLM` with GPU acceleration

**GPU Orchestration:**
- Enforce **sequential judge execution** in Temporal workflows to avoid concurrent OOM errors
- Configure vLLM concurrency limits: `max_model_len`, `num-gpus`
- Model swapping strategy: Load judge model only when needed, unload after completion
- Dev environment: Single GPU (24GB) with 8B models only; prod environment: Multi-GPU (2x48GB+) for 35B+ models

#### Definition of Done
- [x] Model download script with checksum verification
- [x] MinIO integration for model storage
- [x] Local model loading from filesystem/MinIO
- [x] Documentation in `docs/01-initial/model-setup.md`
- [x] Air-gapped deployment procedure documented
- [x] GPU routing and sequential execution strategy documented

#### Dependencies
- Blocked by: INFRA-3 (MinIO)
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

#### Dependencies
- Blocked by: INFRA-1
- Blocks: CROSSWALK-4, EXTRACT-4

---

### INFRA-10: Cross-Store Reconciliation and Replay Strategy

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Lead  
**Labels**: infrastructure, reliability, replay  

#### User Story
> As a **system architect**, I want a defined cross-store reconciliation and replay strategy, so that we can recover from partial failures across PostgreSQL, Memgraph, Qdrant, and MinIO without data corruption or ghost records.

#### Context and Background
The CTO review identified a critical gap: no reconciliation strategy exists for the 5 sources of truth (PostgreSQL, Memgraph, Qdrant, MinIO, Kafka). Without this, a failure like "Kafka emits event ✅, Extraction writes to Postgres ❌, Qdrant write succeeds ✅" leaves ghost embeddings with no source truth.

This story defines:
1. **Idempotent write patterns** for all stores
2. **Replay mechanism** from Bronze layer
3. **Consistency checks** between stores
4. **Checkpoint-based recovery** for workflows

#### Acceptance Criteria
1. Given a partial failure occurs, when the replay script is executed with a `document_id`, then all stores are reconstructed to a consistent state
2. Given a workflow fails, when the Temporal workflow is replayed, then it resumes from the last checkpoint without re-executing completed activities
3. Given a cross-store consistency check is run, when discrepancies are found, then they are logged to `reconciliation_dlq` for manual review
4. All write operations are idempotent (running twice produces the same result as running once)
5. A `replay_from_bronhe.py` script exists that can reconstruct Silver, Gold, Qdrant, and Memgraph from Bronze layer data
6. Checkpoint metadata stored in PostgreSQL `workflow_checkpoints` table

#### Technical Notes
- Idempotent writes:
  ```python
  # Use UPSERT (ON CONFLICT DO UPDATE) for all database writes
  def write_control(control_data):
      INSERT INTO golden_controls VALUES (...)
      ON CONFLICT (control_id) DO UPDATE SET
          updated_at = NOW(),
          status = EXCLUDED.status
  ```
- Temporal replay:
  ```python
  # Temporal automatically supports replay via workflow history
  # Just re-run the workflow with the same workflow_id
  workflow_id = f"extraction-{document_id}"
  result = await client.execute_workflow(
      "extraction_workflow",
      args=[document_id],
      id=workflow_id,
      task_queue="extraction-task-queue"
  )
  ```
- Checkpoint schema:
  ```sql
  CREATE TABLE workflow_checkpoints (
      checkpoint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      workflow_id VARCHAR(255) NOT NULL,
      stage VARCHAR(50) NOT NULL,  -- 'extraction', 'validation', 'crosswalk'
      data_hash VARCHAR(64) NOT NULL,  -- SHA-256 of processed data
      created_at TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(workflow_id, stage)
  );
  ```
- Reconciliation script:
  ```bash
  python scripts/replay_from_bronze.py --document-id doc-123
  python scripts/check_consistency.py --daily-run
  ```

#### Definition of Done
- [x] Idempotent write patterns documented and implemented
- [x] Replay script working (tested with sample document)
- [x] Checkpoint table created and integrated with Temporal
- [x] Consistency check script with daily cron job
- [x] Documentation in `docs/01-initial/replay-strategy.md`

#### Dependencies
- Blocked by: INFRA-2, INFRA-4, INFRA-9 (all stores must exist)
- Blocks: None (runs in parallel with feature development)

---

## Sprint 2: Document Ingestion Pipeline Foundation

**Sprint Goal**: Implement the base document ingestion pipeline that can parse PDFs to Markdown and store them in the Bronze layer with SHA-256 deduplication.

**Rationale**: This sprint builds the foundation of the De Jure pipeline by implementing PDF parsing, metadata extraction, and Bronze layer storage. Without this, no data can flow into the system.

**Stories in this Sprint**: INGEST-1 through INGEST-5  
**Total Story Points**: 34

---

### INGEST-1: MinIO Document Upload API

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, api, minio  

#### User Story
> As a **compliance officer**, I want to upload regulatory PDFs via a REST API, so that they are stored in MinIO with SHA-256 deduplication and registered in the audit log.

#### Context and Background
Per TRD Section 7.1, the ingestion pipeline begins with document upload. The API must:
- Accept PDF files (up to 100MB)
- Calculate SHA-256 hash for deduplication
- Store in MinIO `source-regulations` bucket
- Register metadata in PostgreSQL audit_log table
- Trigger Kafka event `document.ingested`

#### Acceptance Criteria
1. Given a valid PDF file is uploaded via `POST /api/v1/documents/upload`, then the file is stored in MinIO with key `documents/{sha256_hash}/{filename}`
2. Given a duplicate file (same SHA-256) is uploaded, then the API returns HTTP 200 with message `{"status": "duplicate", "document_id": "doc-123"}` without re-uploading
3. Given a file is uploaded, when the audit_log table is queried, then a new row with `event_type='document.uploaded'` is created
4. Given a file is uploaded, when the Kafka topic `document.ingested` is consumed, then a message with `document_id`, `hash`, `source_path` is received
5. File size validation: files > 100MB are rejected with HTTP 413
6. Content-Type validation: only `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document` are accepted

#### Technical Notes
- Use FastAPI `UploadFile` for file handling
- SHA-256 calculation: `hashlib.sha256(file.read()).hexdigest()`
- MinIO client: `minio.Minio(endpoint, access_key, secret_key, secure=False)`
- Kafka producer: `kafka.KafkaProducer(bootstrap_servers='localhost:9092')`
- Include requestor_id in audit_log for traceability

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for file upload and deduplication
- [x] Integration tests for MinIO and Kafka
- [x] All acceptance criteria verified
- [x] OpenAPI documentation generated

#### Dependencies
- Blocked by: INFRA-1, INFRA-2, INFRA-3
- Blocks: INGEST-2

---

### INGEST-2: MinerU PDF-to-Markdown Conversion

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, pdf, mineru, nlp  

#### User Story
> As a **backend developer**, I want MinerU to convert uploaded PDFs to structured Markdown with preserved heading hierarchies and tables, so that downstream LLM extraction can operate on clean, semantically-rich text.

#### Context and Background
Per TRD Section 7.2, MinerU is the primary PDF parsing tool. It must preserve:
- Heading hierarchies (H1 through H6)
- Multi-column layouts and reading order
- Nested and borderless tables
- Footnotes associated with parent paragraphs

#### Acceptance Criteria
1. Given a PDF file is passed to `convert_pdf_to_markdown(pdf_path)`, then the output Markdown preserves the heading hierarchy (H1-H6)
2. Given a PDF contains tables, when converted to Markdown, then they are rendered in valid GitHub-Flavored Markdown table syntax
3. Given a PDF contains footnotes, when converted, then they are annotated inline or appended to their parent section
4. Given a complex PDF (multi-column, images), when Marker fallback is triggered (MinerU confidence < 0.85), then the output is semantically equivalent
5. Conversion time: < 30 seconds per document (< 100 pages)
6. Output stored in MinIO `markdown-conversions` bucket with key `conversions/{document_id}/{document_id}.md`

#### Technical Notes
- MinerU package: `mineru` (install via pip)
- Marker fallback: `marker_single(image_path, output_dir, do_ocr=True)`
- Confidence scoring: Use MinerU's internal confidence metric
- Create async task for conversion to avoid API blocking
- Log conversion metrics to Langfuse: `extraction_quality`, `confidence_score`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for PDF conversion with sample documents
- [x] Integration tests for MinerU and Marker
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/parsing-pipeline.md`

#### Dependencies
- Blocked by: INGEST-1
- Blocks: INGEST-3

---

### INGEST-3: Hybrid Chunking Strategy

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, nlp, chunking, ml  

#### User Story
> As a **ML engineer**, I want hybrid chunking that uses Markdown header hierarchies + semantic cosine distance threshold, so that chunks preserve semantic boundaries and avoid splitting related content.

#### Context and Background
Per TRD Section 7.3, the chunking strategy must implement:
1. **Markdown Header-Based Chunking**: Split at H1-H6 headings
2. **Semantic Chunking**: Use BGE-M3 embedding cosine distance; if > 0.75 threshold, force split

This ensures chunks are semantically coherent and preserve parent/child clause groupings.

#### Acceptance Criteria
1. Given Markdown text with headings, when `chunk_by_headers(markdown)` is called, then each chunk starts at a heading and includes all content until the next heading
2. Given a chunk > 2000 tokens, when `semantic_split(chunk)` is called, then it is split at semantic boundaries (cosine distance > 0.75)
3. Given two adjacent sentences, when their embedding cosine distance is 0.80, then they are split into separate chunks
4. Given two adjacent sentences, when their embedding cosine distance is 0.60, then they remain in the same chunk
5. Each chunk payload includes: `document_id`, `section` (heading path), `text`, `metadata` (page numbers if available)
6. Chunk output stored in Qdrant `document_chunks` collection

#### Technical Notes
- BGE-M3 embedding model: `BAAI/bge-m3` via `sentence_transformers`
- Cosine distance calculation: `1 - cosine_similarity(vec1, vec2)`
- Max chunk size: 2000 tokens (use `tiktoken` for counting)
- Overlap between chunks: 100 tokens for context continuity
- Qdrant upload: `qdrant_client.upsert(collection_name="document_chunks", points=...)`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for chunking with sample Markdown
- [x] Integration tests for BGE-M3 embeddings and Qdrant
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INGEST-2, INFRA-4
- Blocks: INGEST-4, EMBED-1

---

### INGEST-4: Bronze Layer Storage

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, database, bronze  

#### User Story
> As a **system**, I want parsed Markdown documents to be stored in the PostgreSQL Bronze layer, so that raw ingestion data is preserved immutably for audit and replay.

#### Context and Background
Per TRD Section 6.1, the Bronze layer (`staging_controls`) stores:
- Completely raw unstructured text from PDFs/Markdown
- Fields: `uuid`, `canonical_id`, `raw_file_content` (JSONB blob)

This is the source of truth for all downstream processing.

#### Acceptance Criteria
1. Given Markdown content is received, when `write_bronze_record(document_id, markdown)` is called, then a row is inserted into `staging_controls` table
2. Given a Bronze record is created, when the row is queried, then it has `uuid`, `canonical_id`, `raw_file_content` with `content` and `metadata` fields
3. Given a Bronze record is created, when the `created_at` timestamp is checked, then it is set to the current UTC time
4. Given the `canonical_id` is unique per document, when a duplicate `canonical_id` is attempted, then the insert is rejected with unique constraint violation
5. Bronze record includes reference to MinIO paths: `minio_raw_path` and `minio_markdown_path`
6. SQLAlchemy model in `/backend/app/models/bronze.py` with proper ORM definitions

#### Technical Notes
- `raw_file_content` JSONB schema:
  ```json
  {
    "document_id": "doc-123",
    "hash": "abc123...",
    "source_path": "/source-regulations/nist-csf.pdf",
    "content": "# Heading\n\nText...",
    "metadata": {
      "framework_id": "nist-csf",
      "version": "1.0",
      "language": "en"
    }
  }
  ```
- Use PostgreSQL `uuid_generate_v4()` for UUID generation
- Create index on `canonical_id` for deduplication checks

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Bronze layer insertion
- [x] Integration tests for database operations
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-2, INGEST-3
- Blocks: INGEST-5, DUALJUDGE-1

---

### INGEST-5: Kafka Event Publishing

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, kafka, event-driven  

#### User Story
> As a **system**, I want Kafka events to be published after each ingestion milestone, so that downstream pipelines (extraction, validation, embedding) can react asynchronously.

#### Context and Background
Per TRD Section 19.1, the Kafka topic registry includes:
- `document.ingested`: Published when a document is uploaded and parsed
- `extraction.completed`: Published when extraction finishes
- `validation.completed`: Published when dual-judge validation succeeds

This story implements the Kafka producer and topic configuration.

#### Acceptance Criteria
1. Given a document is uploaded, when the upload completes, then a message is published to `document.ingested` topic with fields: `document_id`, `hash`, `framework_id`, `source_path`
2. Given a message is published, when the Kafka topic is consumed, then the message is received with correct schema
3. Given the Kafka producer is configured, when the broker is unavailable, then the producer retries with exponential backoff (max 3 retries)
4. Kafka topic `document.ingested` is created automatically with 7-day retention
5. Kafka message key is the `document_id` for partitioning consistency
6. All messages are serialized as JSON with schema validation

#### Technical Notes
- Kafka producer config:
  ```python
  KafkaProducer(
      bootstrap_servers='localhost:9092',
      value_serializer=lambda v: json.dumps(v).encode('utf-8'),
      acks='all',
      retries=3,
      retry_backoff_ms=100
  )
  ```
- Message schema validation: Use `fastjsonschema` to validate before send
- Dead-letter queue: If message fails 3 times, send to `document.ingested.dlq` topic
- Langfuse tracing: Log message publish event with `trace_id`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Kafka producer
- [x] Integration tests for Kafka topic and message consumption
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-1
- Blocks: None

---

## Sprint 3: De Jure Extraction, Observability, and Baseline Validation

**Sprint Goal**: Implement the extraction pipeline with shift-left observability (Langfuse), DLQ metrics, and "Golden 50" local validation.

**Rationale**: The CTO review identified that leaving observability until Sprint 9 creates a black-box AI development risk. This sprint adds Langfuse for LLM traceability, SQL-based DLQ metrics for early warning, and the "Golden 50" SME-validated baseline before scaling to thousands of documents.

**Stories in this Sprint**: EXTRACT-1 through EXTRACT-5, OBSERV-1  
**Total Story Points**: 41

---

### EXTRACT-1: Semantic Decomposition Pipeline

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 13  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, llm, extraction, nlp  

#### User Story
> As a **ML engineer**, I want an LLM-driven semantic decomposition pipeline that extracts atomic rule units from regulatory text, so that each obligation can be represented as a discrete, structured node in the knowledge graph.

#### Context and Background
Per TRD Section 7.4, the extraction pipeline must:
1. Read from Bronze layer (Markdown content)
2. Use Mistral 8B (local LLM via Ollama/vLLM) for extraction
3. Output structured JSON with fields: `id`, `prose`, `action_verb`, `subject_noun`, `clause_ref`, `effective_date`
4. Follow De Jure canonical schema

#### Acceptance Criteria
1. Given Markdown content from Bronze layer, when `extract_obligations(markdown)` is called, then the output is a list of obligation objects
2. Given an obligation is extracted, when the object is validated, then it has all required fields: `id`, `prose`, `action_verb`, `subject_noun`, `clause_ref`
3. Given a complex regulation clause, when extraction is performed, then the output includes parent section reference and clause hierarchy
4. Extraction uses Mistral 8B model via vLLM API: `http://localhost:8000/v1/chat/completions` (dev: Ollama fallback at `localhost:11434`)
5. Output schema validated against Pydantic model in `/backend/app/schemas/obligation.py`
6. Extraction results stored in PostgreSQL `semantic_controls` (Silver layer)

#### Technical Notes
- LLM prompt template (in `/backend/app/prompts/extraction.md`):
  ```
  Extract atomic obligations from the following regulatory text.
  Each obligation must include: id, prose, action_verb, subject_noun, clause_ref.
  
  Text:
  {{markdown_content}}
  
  Output JSON:
  [
    {
      "id": "AC-1.a",
      "prose": "The organization must limit access...",
      "action_verb": "limit",
      "subject_noun": "information system access",
      "clause_ref": "Section 3.1"
    }
  ]
  ```
- **Production (vLLM)**: Use OpenAI-compatible client for vLLM endpoint
  ```python
  from openai import OpenAI
  
  # Production: vLLM endpoint (localhost:8000 or K8s service)
  client = OpenAI(
      base_url="http://localhost:8000/v1",
      api_key="not-required"  # vLLM doesn't require auth internally
  )
  
  response = client.chat.completions.create(
      model="mistralai/Mistral-7B-Instruct-v0.3",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.3,
      max_tokens=4000,
      response_format={"type": "json_object"}
  )
  ```
  
- **Development fallback (Ollama)**: For local dev without GPU
  ```python
  import ollama
  
  # Development: Ollama endpoint (localhost:11434)
  response = ollama.chat(
      model='mistral',
      messages=[{"role": "user", "content": prompt}],
      options={"temperature": 0.3}
  )
  ```
  
- Temperature: 0.3 for deterministic extraction
- Max tokens: 4000 per extraction

> **IMPORTANT**: The acceptance criteria state the primary implementation uses vLLM. The Ollama client shown in the original technical notes was incorrect for production. Developers should use the vLLM client as primary and only use Ollama as a development fallback when vLLM is not available.

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for extraction with sample Markdown
- [x] Integration tests for Ollama/Mistral API
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/extraction-pipeline.md`

#### Dependencies
- Blocked by: INGEST-4, INFRA-1
- Blocks: EXTRACT-2

---

### EXTRACT-2: LLM-as-Judge Extraction Quality Check

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, llm, validation, judge  

#### User Story
> As a **ML engineer**, I want an LLM-as-Judge quality check that scores extracted obligations across metadata accuracy, legal definition alignment, and rule semantics, so that low-confidence extractions can be repaired or rejected.

#### Context and Background
Per TRD Section 7.4 Stage 3 (Multi-Criteria Evaluation), the LLM-as-Judge must score:
1. **Metadata Accuracy**: Are `action_verb`, `subject_noun`, `clause_ref` correctly extracted?
2. **Legal Definition Alignment**: Does the obligation align with standard compliance terminology?
3. **Rule Semantics**: Is the intent of the obligation preserved without semantic loss?

Threshold: Score >= 0.80 passes; < 0.80 triggers iterative repair.

#### Acceptance Criteria
1. Given an extracted obligation, when `judge_extraction(obligation)` is called, then a score (0.0-1.0) is returned for each criterion
2. Given all criteria scores are >= 0.80, when the judgment is evaluated, then the obligation passes with status `approved`
3. Given any criterion score is < 0.80, when the judgment is evaluated, then the obligation is flagged for repair with `reason` field explaining the failure
4. LLM-as-Judge uses Llama 3.1 8B (local Ollama) for evaluation
5. Judge output includes detailed feedback: what was wrong and how to fix it
6. Scores logged to Langfuse with `trace_id` for audit trail

#### Technical Notes
- Judge prompt template:
  ```
  Evaluate the following extracted obligation for quality.
  Score each criterion from 0.0 to 1.0.
  
  Obligation: {{obligation_json}}
  Original Text: {{original_markdown}}
  
  Criteria:
  1. Metadata Accuracy: Are action_verb, subject_noun, clause_ref correct?
  2. Legal Definition Alignment: Does it align with compliance terminology?
  3. Rule Semantics: Is the intent preserved without loss?
  
  Output JSON:
  {
    "metadata_accuracy": 0.95,
    "legal_alignment": 0.90,
    "semantics": 0.88,
    "overall_score": 0.91,
    "status": "approved",
    "feedback": "Extraction is high quality."
  }
  ```
- Average the three criterion scores for `overall_score`
- Use Pydantic model for validation: `/backend/app/schemas/judge.py`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for judge with sample obligations
- [x] Integration tests for LLM judge API
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: EXTRACT-1
- Blocks: EXTRACT-3

---

### EXTRACT-3: Iterative Repair Loop

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 8  
**Priority**: Medium  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, llm, repair, extraction  

#### User Story
> As a **ML engineer**, I want an iterative repair loop that re-processes low-confidence extractions with upstream context corrections, so that the system can automatically fix most quality issues without human intervention.

#### Context and Background
Per TRD Section 7.4 Stage 4 (Iterative Repair), the repair loop must:
1. Receive feedback from LLM-as-Judge on failed extractions
2. Augment the extraction prompt with context from parent sections
3. Re-run extraction with corrected prompt
4. Repeat up to 3 times before escalating to dead-letter queue

#### Acceptance Criteria
1. Given a failed extraction (score < 0.80), when `repair_extraction(obligation, feedback)` is called, then the extraction is re-run with feedback incorporated into the prompt
2. Given the repaired extraction, when it is re-judged, then if score >= 0.80, the status is updated to `approved`
3. Given 3 repair attempts all fail, when the third judgment is received, then the obligation is moved to dead-letter queue with `reason: max_repair_attempts_exceeded`
4. Each repair attempt logs the feedback and new extraction to Langfuse
5. Context augmentation: Include parent section heading and 2 preceding paragraphs in the repair prompt
6. Maximum 3 repair attempts per obligation (configurable via environment variable)

#### Technical Notes
- Repair prompt augmentation:
  ```
  Context from parent section:
  {{parent_section_heading}}
  {{preceding_paragraphs}}
  
  Previous extraction failed because: {{judge_feedback}}
  
  Re-extract with this context.
  ```
- Dead-letter queue: Store in PostgreSQL `extraction_dlq` table with fields: `obligation_id`, `original_text`, `feedback`, `attempt_count`, `timestamp`
- Use Temporal workflow for repair loop: `extraction_validation_workflow` with signal for retry

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for repair loop with sample failures
- [x] Integration tests for iterative extraction
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: EXTRACT-2
- Blocks: EXTRACT-4

---

### EXTRACT-4: Silver Layer Storage

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, database, silver  

#### User Story
> As a **system**, I want validated extraction results to be stored in the PostgreSQL Silver layer, so that structured obligation data is preserved before dual-judge validation.

#### Context and Background
Per TRD Section 6.2, the Silver layer (`semantic_controls`) stores:
- AI-extracted structured data
- Fields: `framework_name`, `group_id`, `objective_text`, `statement_text`, `action_verb`, `subject_noun` (Facets)

This is the intermediate layer before Gold promotion.

#### Acceptance Criteria
1. Given a validated extraction passes LLM-as-Judge, when `write_silver_record(obligation)` is called, then a row is inserted into `semantic_controls` table
2. Given a Silver record is created, when the row is queried, then it has all facet fields: `framework_name`, `group_id`, `objective_text`, `statement_text`, `action_verb`, `subject_noun`
3. Given a Silver record is created, when the `status` field is checked, then it is set to `pending_validation`
4. Given a Silver record is created, when it is linked to a Bronze record, then the `bronze_record_id` FK is set correctly
5. Silver records are versioned: updates create new rows with `version` increment
6. SQLAlchemy model in `/backend/app/models/semantic.py` with proper ORM definitions

#### Technical Notes
- Silver schema:
  ```sql
  CREATE TABLE semantic_controls (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      bronze_record_id UUID REFERENCES staging_controls(id),
      framework_name VARCHAR(255),
      group_id VARCHAR(50),
      objective_text TEXT,
      statement_text TEXT,
      action_verb VARCHAR(100),
      subject_noun VARCHAR(255),
      status VARCHAR(50) DEFAULT 'pending_validation',
      version INTEGER DEFAULT 1,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  ```
- Index on `bronze_record_id` for fast lookup
- Create trigger to auto-increment `version` on update

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Silver layer insertion
- [x] Integration tests for database operations
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: EXTRACT-3, INFRA-2
- Blocks: DUALJUDGE-1

---

### EXTRACT-5: Extraction Kafka Event

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, kafka, event-driven  

#### User Story
> As a **system**, I want a Kafka event to be published after successful extraction, so that downstream pipelines (dual-judge validation, embedding) can react asynchronously.

#### Context and Background
Per TRD Section 19.1, the `extraction.completed` topic is published when:
- Extraction finishes successfully
- Contains: `obligation_ids[]`, `document_id`, `extraction_scores[]`

This event triggers the dual-judge validation workflow.

#### Acceptance Criteria
1. Given extraction completes successfully, when `publish_extraction_completed(document_id, obligation_ids, scores)` is called, then a message is published to `extraction.completed` topic
2. Given a message is published, when the Kafka topic is consumed, then the message has fields: `obligation_ids[]`, `document_id`, `extraction_scores[]`
3. Given the message is published, when Langfuse tracing is checked, then a trace with `event_type='extraction.completed'` is created
4. Message key is the `document_id` for partitioning
5. If extraction has any obligations in dead-letter queue, include `dlq_count` in the message
6. Message schema validated before publish

#### Technical Notes
- Kafka message schema:
  ```json
  {
    "document_id": "doc-123",
    "obligation_ids": ["obl-1", "obl-2", "obl-3"],
    "extraction_scores": [0.92, 0.88, 0.95],
    "dlq_count": 0,
    "timestamp": "2026-04-13T10:00:00Z"
  }
  ```
- Use the same Kafka producer configured in INGEST-5
- Add Langfuse trace: `langfuse.trace(name="extraction.completed", ...)`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Kafka event publishing
- [x] Integration tests for message consumption
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: EXTRACT-4
- Blocks: DUALJUDGE-1

---

### OBSERV-1: Langfuse Tracing Integration

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 3  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: observability, llm, tracing  

#### User Story
> As a **ML engineer**, I want Langfuse tracing integrated into the extraction pipeline, so that I can see exactly what prompts went in, what came out, and debug hallucinations with `trace_id`.

#### Context and Background
The CTO review identified that leaving observability until Sprint 9 creates a black-box AI development risk. This story shifts Langfuse integration forward to Sprint 3, right alongside extraction.

Langfuse takes less than an hour to integrate via their Python SDK. When accuracy drops, ML engineers need the `trace_id` to see the exact prompt version that caused the hallucination.

#### Acceptance Criteria
1. Given the Langfuse client is initialized, when an extraction prompt is sent, then a trace is created with `trace_id`
2. Given a trace exists, when the extraction output is logged, then the span includes the full prompt, completion, and token usage
3. Given an extraction fails (score < 0.80), when the failure is logged, then the trace includes the judge feedback and repair attempts
4. Langfuse dashboard accessible at `http://localhost:3000` with documented credentials
5. All LLM calls (extraction, judge, repair) are traced with consistent `trace_id` linkage
6. Production Langfuse instance configured with project scoping for `dev` and `prod` environments

#### Technical Notes
- Langfuse Python SDK integration:
  ```python
  from langfuse import Langfuse
  from langfuse.decorators import observe
  
  langfuse = Langfuse()
  
  @observe()
  def extract_obligations(markdown_content):
      trace = langfuse.trace(name="extraction", metadata={"document_id": doc_id})
      # ... extraction logic
      return output
  
  @observe()
  def judge_extraction(obligation):
      trace = langfuse.trace(name="judge", parent_observation_id=extraction_span.id)
      # ... judge logic
      return score
  ```
- Traced events:
  - `extraction.started` / `extraction.completed`
  - `judge.started` / `judge.completed`
  - `repair.started` / `repair.completed`
  - `extraction.completed` (Kafka event)
- Cost tracking: Log token usage and estimated cost per trace
- Retention: 30 days for development, 1 year for production

#### Definition of Done
- [x] Langfuse SDK integrated into extraction pipeline
- [x] All LLM calls traced with `trace_id`
- [x] Langfuse dashboard running and accessible
- [x] Documentation in `docs/01-initial/observability.md`
- [x] Unit tests for trace creation

#### Dependencies
- Blocked by: INFRA-1 (Langfuse service running)
- Blocks: EXTRACT-2 (judge scoring)

---

### DLQ Metrics: SQL-Based Early Warning System

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 3  
**Priority**: Medium  
**Assigned To**: Backend Engineer  
**Labels**: backend, database, metrics, dlq  

#### User Story
> As a **team lead**, I want SQL queries against dead-letter queues that surface accuracy metrics without a dashboard, so that I can detect when to "stop the line" and fix prompts.

#### Context and Background
The CTO review identified that DLQs exist but no metrics are defined. Until Prometheus/Grafana is built in Sprint 9, these SQL queries serve as the "poor man's dashboard" for accuracy tracking.

**DLQ Tables:**
- `extraction_dlq`: Failed extractions (score < 0.80 after 3 repair attempts)
- `validation_dlq`: Failed dual-judge validations (Logic < 0.95 or Technical < 1.0)
- `crosswalk_dlq`: Failed crosswalk mappings (low confidence)

**Three Essential SQL Queries:**
```sql
-- 1. Gold vs. DLQ ratio (overall accuracy indicator)
SELECT 
    COUNT(*) as gold_count,
    (SELECT COUNT(*) FROM extraction_dlq) as dlq_count,
    COUNT(*)::FLOAT / (COUNT(*) + (SELECT COUNT(*) FROM extraction_dlq)) as accuracy_ratio
FROM semantic_controls WHERE status = 'approved';

-- 2. Framework with most failures
SELECT 
    framework_name,
    COUNT(*) as failure_count
FROM extraction_dlq edq
JOIN semantic_controls sc ON edq.bronze_record_id = sc.id
GROUP BY framework_name
ORDER BY failure_count DESC
LIMIT 10;

-- 3. Common failure reason codes
SELECT 
    reason,
    COUNT(*) as count
FROM extraction_dlq
GROUP BY reason
ORDER BY count DESC
LIMIT 10;
```

#### Acceptance Criteria
1. Given the DLQ tables exist, when the SQL queries are executed, then accurate metrics are returned
2. Given a query shows DLQ count > 10% of Gold count, when the metric is reported, then an alert is sent to the team
3. SQL queries saved in `scripts/dlq_metrics.sql` with documentation
4. Metrics logged to Langfuse for trend tracking
5. Daily automated run of DLQ metrics via cron/job scheduler
6. Metrics displayed in team standup dashboard (simple text output or email)

#### Technical Notes
- Save queries in `/backend/scripts/dlq_metrics.sql`
- Cron job runs at 9am and 5pm daily: `python scripts/run_dlq_metrics.py`
- Email alert if: `dlq_count / (gold_count + dlq_count) > 0.10`
- Integration with Temporal: Failed DLQ inserts trigger `accuracy.alert` Kafka event

#### Definition of Done
- [x] SQL queries written and tested
- [x] Automated daily run configured
- [x] Alert thresholds defined
- [x] Documentation in `docs/01-initial/dlq-metrics.md`
- [x] Team trained on interpreting metrics

#### Dependencies
- Blocked by: INFRA-2 (DLQ tables exist)
- Blocks: None (runs in parallel with other sprints)

---

### "Golden 50" Local Validation Test

**Type**: Story  
**Sprint**: Sprint 3  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: ML/AI Engineer + SME  
**Labels**: testing, benchmark, validation  

#### User Story
> As a **ML engineer**, I want a "Golden 50" SME-validated baseline that I can test against locally, so that I know if my prompts are working before scaling to thousands of documents.

#### Context and Background
The CTO review identified that leaving TEST-3 (accuracy benchmarks) until Sprint 10 is too late. If the baseline accuracy is only 65%, you don't want to find that out five sprints later after building dashboards and OSCAL exporters on top of flawed data.

**This Story:**
- By end of Sprint 2, SMEs manually annotate **50 critical paragraphs** (the "Golden 50")
- ML engineer runs extraction script locally against those 50 paragraphs
- If 20 are wrong, they don't commit the code
- Iterate on the prompt until 45/50 pass
- This is the "shift-left" accuracy validation

#### Acceptance Criteria
1. Given the "Golden 50" dataset exists, when the extraction script is run, then 50 extraction results are produced
2. Given the results are evaluated, when accuracy < 90% (45/50 correct), then the ML engineer iterates on the prompt
3. Given accuracy >= 90%, when the code is committed, then a pass tag is recorded in `tests/fixtures/golden50_results.json`
4. The "Golden 50" dataset is stored in `tests/fixtures/golden_50.json` with:
   - `paragraph_text`: Original regulatory text
   - `expected_obligations`: SME-annotated obligation objects
   - `framework_id`: Source framework
5. Local test command: `pytest tests/test_golden50.py -v`
6. Failure threshold: < 45/50 correct fails the test and blocks commit

#### Technical Notes
- Golden 50 format:
  ```json
  [
    {
      "id": "golden-001",
      "paragraph_text": "Financial institutions shall maintain...",
      "expected_obligations": [
        {
          "prose": "Financial institutions shall maintain...",
          "action_verb": "maintain",
          "subject_noun": "ICT systems",
          "clause_ref": "DORA Article 11(2)(a)"
        }
      ],
      "framework_id": "dora",
      "annotated_by": "sme-001",
      "annotated_at": "2026-04-13"
    }
  ]
  ```
- Test script: `tests/test_golden50.py`
  ```python
  def test_golden_50():
      golden_data = load_golden_50()
      results = []
      for item in golden_data:
          extraction = extract_obligations(item["paragraph_text"])
          results.append(evaluate_extraction(extraction, item["expected_obligations"]))
      
      accuracy = sum(1 for r in results if r["correct"]) / len(results)
      assert accuracy >= 0.90, f"Golden 50 accuracy {accuracy} < 90%"
  ```
- SME coordination: Schedule 4-hour annotation session with 2 compliance officers

#### Definition of Done
- [x] "Golden 50" dataset annotated by SMEs
- [x] Local test script working
- [x] Accuracy >= 90% achieved before commit
- [x] Results recorded in `tests/fixtures/golden50_results.json`
- [x] Documentation in `docs/01-initial/golden50.md`

#### Dependencies
- Blocked by: INGEST-5 (SME available for annotation)
- Blocks: None (runs in parallel with EXTRACT-1)

---

## Sprint 4: Dual-Judge Validation Backend

**Sprint Goal**: Implement the dual-judge validation system that independently audits AI-generated mappings before they commit to the production graph.

**Rationale**: This sprint implements the critical quality gate that ensures no low-confidence AI determinations reach the production graph. The dual-judge model (Logic Judge + Technical Judge) is a core requirement from the TRD.

**CTO Fix**: Removed HITL-1/HITL-2 frontend stories (moved to Sprint 6) to reduce sprint load from 50 to ~29 points. The backend team can test workflows using simple cURL/Postman collections during development.

**Stories in this Sprint**: DUALJUDGE-1 through DUALJUDGE-4  
**Total Story Points**: 29

---

### DUALJUDGE-1: Logic Judge (Semantic Faithfulness)

**Type**: Story  
**Sprint**: Sprint 4  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, llm, judge, semantic  

#### User Story
> As a **ML engineer**, I want a Logic Judge (Llama 3.1 70B) that evaluates semantic faithfulness of extracted obligations, so that obligations that lose intent during extraction are caught before graph commit.

#### Context and Background
Per TRD Section 7.2 and Section 19.3, the Logic Judge must:
- Use Llama 3.1 70B (quantized, via vLLM)
- Evaluate: "Did the mapper lose the actual intent of the control?"
- Threshold: Score < 0.95 triggers human review
- Output: Semantic faithfulness score (0.0-1.0) + detailed feedback

#### Acceptance Criteria
1. Given an obligation from Silver layer, when `logic_judge(obligation, original_text)` is called, then a semantic faithfulness score is returned
2. Given the obligation preserves the original intent, when judged, then the score is >= 0.95 and status is `approved`
3. Given the obligation loses intent, when judged, then the score is < 0.95 and status is `requires_human_review`
4. Logic Judge uses Llama 3.1 70B quantized model via vLLM API: `http://localhost:8000/v1/chat/completions`
5. Judge output includes detailed feedback explaining what was lost or distorted
6. Scores logged to Langfuse with traceability to extraction ID

#### Technical Notes
- vLLM configuration:
  ```python
  vllm.LLM(
      model="/models/llama-3.1-70b-q4_0",
      tensor_parallel_size=1,
      gpu_memory_utilization=0.4
  )
  ```
- Judge prompt:
  ```
  Evaluate whether this extracted obligation preserves the semantic intent of the original regulatory text.
  
  Original Text:
  {{original_text}}
  
  Extracted Obligation:
  {{obligation_json}}
  
  Question: Did the extraction lose, distort, or add any semantic content?
  
  Output JSON:
  {
    "semantic_faithfulness_score": 0.97,
    "status": "approved",
    "feedback": "The extraction accurately preserves the intent of the original text."
  }
  ```
- Temperature: 0.1 for consistent judgment
- Use Pydantic model for output validation: `/backend/app/schemas/logic_judge.py`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Logic Judge with sample obligations
- [x] Integration tests for vLLM/Llama API
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/dual-judge.md`

#### Dependencies
- Blocked by: EXTRACT-5, INFRA-1
- Blocks: DUALJUDGE-2

---

### DUALJUDGE-2: Technical Judge (Parameter Precision)

**Type**: Story  
**Sprint**: Sprint 4  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, llm, judge, technical  

#### User Story
> As a **ML engineer**, I want a Technical Judge (DeepSeek-R1 72B) that audits technical/mathematical accuracy of extracted parameters, so that incorrect numerical or parameter values are caught before graph commit.

#### Context and Background
Per TRD Section 7.2 and Section 19.3, the Technical Judge must:
- Use DeepSeek-R1 72B (quantized, via vLLM)
- Evaluate: "Does 'Hourly' properly reconcile to '3600 seconds' in OSCAL parameters?"
- Threshold: Score must be 1.0 (exact match) — any error triggers human review
- Output: Technical accuracy score (0.0-1.0) + detailed feedback

#### Acceptance Criteria
1. Given an obligation with parameters (e.g., time frequencies, numerical thresholds), when `technical_judge(obligation)` is called, then a technical accuracy score is returned
2. Given all parameters are technically correct, when judged, then the score is 1.0 and status is `approved`
3. Given any parameter is technically incorrect, when judged, then the score is < 1.0 and status is `requires_human_review`
4. Technical Judge uses DeepSeek-R1 72B quantized model via vLLM API
5. Judge output includes specific parameter errors and corrections
6. Scores logged to Langfuse with traceability to extraction ID

#### Technical Notes
- Technical Judge prompt:
  ```
  Evaluate whether all technical parameters in this obligation are accurate and properly formatted.
  
  Extracted Obligation:
  {{obligation_json}}
  
  Criteria:
  1. Time frequencies (e.g., "Hourly" = 3600 seconds)
  2. Numerical thresholds (e.g., "> 100" is properly formatted)
  3. Date formats (e.g., ISO 8601)
  4. OSCAL parameter compatibility
  
  Output JSON:
  {
    "technical_accuracy_score": 1.0,
    "status": "approved",
    "feedback": "All parameters are technically accurate.",
    "parameter_errors": []
  }
  ```
- Use strict JSON parsing with error handling
- If any parameter errors are found, set score to 0.0
- Log all parameter checks to Langfuse

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Technical Judge with sample obligations
- [x] Integration tests for vLLM/DeepSeek API
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: DUALJUDGE-1
- Blocks: DUALJUDGE-3

---

### DUALJUDGE-3: Aggregate Scoring and Gold Promotion

**Type**: Story  
**Sprint**: Sprint 4  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, validation, aggregation  

#### User Story
> As a **backend developer**, I want an aggregate scoring system that combines Logic Judge and Technical Judge results, so that obligations can be promoted to Gold tier or sent to dead-letter queue based on combined scores.

#### Context and Background
Per TRD Section 19.3, the aggregate scoring must:
- Combine Logic Judge score (weighted 0.6) and Technical Judge score (weighted 0.4)
- Threshold for Gold promotion: Weighted mean >= 0.95 AND Technical Judge = 1.0
- Failure: Send to dead-letter queue with `reason` field

#### Acceptance Criteria
1. Given Logic Judge score and Technical Judge score, when `aggregate_scores(logic_score, tech_score)` is called, then the weighted mean is calculated correctly
2. Given Logic Score = 0.97 and Technical Score = 1.0, when aggregated, then the status is `gold_promoted`
3. Given Logic Score = 0.93 and Technical Score = 1.0, when aggregated, then the status is `requires_human_review` (Logic < 0.95)
4. Given Technical Score = 0.95 (any value < 1.0), when aggregated, then the status is `requires_human_review` (Technical < 1.0)
5. Given a record is promoted to Gold, when it is written to `golden_controls` table, then it has all bitemporal tags (`valid_from`, `valid_to`, `ingested_at`)
6. Given a record fails, when it is written to `validation_dlq` table, then it has `logic_score`, `tech_score`, `reason` fields

#### Technical Notes
- Aggregation logic:
  ```python
  def aggregate_scores(logic_score: float, tech_score: float) -> Dict:
      weighted_mean = (logic_score * 0.6) + (tech_score * 0.4)
      
      if logic_score >= 0.95 and tech_score == 1.0:
          return {"status": "gold_promoted", "mean_confidence": weighted_mean}
      else:
          reason = []
          if logic_score < 0.95:
              reason.append("Logic score below threshold")
          if tech_score < 1.0:
              reason.append("Technical score below threshold")
          return {"status": "requires_human_review", "reason": "; ".join(reason)}
  ```
- Gold promotion: Write to PostgreSQL `golden_controls` table
- Dead-letter queue: Write to PostgreSQL `validation_dlq` table

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for score aggregation
- [x] Integration tests for Gold promotion and DLQ
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: DUALJUDGE-1, DUALJUDGE-2
- Blocks: DUALJUDGE-4

---

### DUALJUDGE-4: Human-in-the-Loop Approval Workflow

**Type**: Story  
**Sprint**: Sprint 4  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, temporal, workflow, hitl  

#### User Story
> As a **backend developer**, I want a Temporal workflow with human-in-the-loop approval gates, so that low-confidence dual-judge failures can be reviewed and corrected by SMEs.

#### Context and Background
Per TRD Section 19.3, the HITL workflow must:
- Pause at approval gates when dual-judge fails
- Await callback signals (approve/reject/modify)
- Resume workflow upon callback with decision applied
- Include timeout handling (48 hours for extraction, 72 hours for mapping)

#### Acceptance Criteria
1. Given a dual-judge failure, when `start_hitl_approval(obligation_id, request_type)` is called, then a Temporal workflow is started and paused at `approval_gate` signal
2. Given a workflow is paused, when the HITL UI submits a decision, then the callback signal is received and workflow resumes
3. Given a callback with `decision=approve`, when the workflow resumes, then the obligation is promoted to Gold
4. Given a callback with `decision=reject`, when the workflow resumes, then the obligation is sent to dead-letter queue
5. Given a callback with `decision=modify` and `corrected_text`, when the workflow resumes, then the corrected text is written to Silver layer and re-queued for dual-judge
6. Workflow timeout handling: If no callback within 48/72 hours, move to dead-letter queue with `reason: hitl_timeout`

#### Technical Notes
- Temporal workflow definition (in `/backend/app/workflows/dual_judge.py`):
  ```python
  @workflow.defn
  class DualJudgeValidationWorkflow:
      @workflow.run
      async def run(self, obligation_id: str) -> Dict:
          # Run Logic Judge
          logic_score = await workflow.execute_activity(
              "logic_judge_activity",
              args=[obligation_id],
              start_to_close_timeout=workflow.timedelta(minutes=30)
          )
          
          # Run Technical Judge
          tech_score = await workflow.execute_activity(
              "technical_judge_activity",
              args=[obligation_id],
              start_to_close_timeout=workflow.timedelta(minutes=30)
          )
          
          # Aggregate scores
          result = aggregate_scores(logic_score, tech_score)
          
          if result["status"] == "requires_human_review":
              # Pause for HITL
              await workflow.wait_condition(
                  lambda: signal_received("approval_callback"),
                  timeout=workflow.timedelta(hours=72)
              )
              # Get callback decision
              callback = workflow.get_signal("approval_callback")
              # Apply decision
              if callback["decision"] == "approve":
                  return promote_to_gold(obligation_id)
              elif callback["decision"] == "reject":
                  return send_to_dlq(obligation_id, "human_rejection")
              elif callback["decision"] == "modify":
                  return requeue_for_validation(callback["corrected_text"])
          
          return result
  ```
- Signal definition: `approval_callback` with fields: `decision`, `reviewer_id`, `timestamp`, `corrected_text?`
- Use Temporal Python SDK

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Temporal workflow
- [x] Integration tests for HITL callback simulation
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/hitl-workflows.md`

#### Dependencies
- Blocked by: DUALJUDGE-3, INFRA-6
- Blocks: None

---

## Sprint 5: ColBERT Crosswalk Engine

**Sprint Goal**: Implement the high-precision control-to-obligation mapping engine using ColBERT late-interaction retrieval and set-theory classification.

**Rationale**: This sprint implements the core crosswalk engine that maps controls to obligations with >90% accuracy. Without this, no compliance relationships can be established.

**Stories in this Sprint**: CROSSWALK-1 through CROSSWALK-4  
**Total Story Points**: 35

---

### CROSSWALK-1: ColBERT Token Embedding Indexing

**Type**: Story  
**Sprint**: Sprint 5  
**Story Points**: 13  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, ml, colbert, vector  

#### User Story
> As a **ML engineer**, I want ColBERTv2.0 token-level embeddings to be precomputed for all controls and stored in Qdrant with SQ8 quantization, so that high-precision MaxSim retrieval can be performed efficiently.

#### Context and Background
Per TRD Section 8.1 and Section 4.3, ColBERT must:
- Create contextualized embeddings for every token in control text
- Store in Qdrant with SQ8 quantization (4x storage reduction)
- Support MaxSim scoring for token-level semantic matching
- Enable retrieval of top-20 candidates for any obligation query

#### Acceptance Criteria
1. Given a control text is received, when `compute_colbert_embeddings(control_text)` is called, then token-level embeddings are generated
2. Given embeddings are computed, when they are stored in Qdrant, then they are indexed with SQ8 quantization
3. Given an obligation query is performed, when ColBERT MaxSim retrieval is executed, then the top-20 candidate controls are returned
4. Retrieval time: < 1 second for top-20 candidates
5. Each Qdrant point includes payload: `control_id`, `control_name`, `framework_id`
6. ColBERT model: `colbert-ir/colbertv2.0-adept/ir` via HuggingFace

#### Technical Notes
- **CRITICAL FIX**: The CTO review identified that `Retriever.query()` performs retrieval against an index and does not return raw token embeddings. Use RAGatouille for correct API access:
  ```python
  from RAGatouille import RAGPretrainedModel
  
  # Initialize ColBERT model for embedding generation
  colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0-adept/ir")
  colbert.index(
      collection=control_texts,
      index_name="controls_colbert",
      max_length=500,
      doc_len=300,
      nbits=8,
      kmeans_niters=4
  )
  
  # To get embeddings for a single text:
  from colbert.modeling.checkpoint import Checkpoint
  cp = Checkpoint("colbert-ir/colbertv2.0-adept/ir", fast_load=True)
  token_embeddings = cp.message_conversion(query=control_text)  # Shape: [num_tokens, embedding_dim]
  ```
  
  OR use direct HuggingFace transformers:
  ```python
  from transformers import AutoModel, AutoTokenizer
  
  tokenizer = AutoTokenizer.from_pretrained("colbert-ir/colbertv2.0-adept/ir")
  model = AutoModel.from_pretrained("colbert-ir/colbertv2.0-adept/ir")
  
  inputs = tokenizer(control_text, return_tensors="pt", truncation=True, max_length=500)
  outputs = model(**inputs)
  token_embeddings = outputs.last_hidden_state  # Shape: [batch, num_tokens, dim]
  ```
- Qdrant upload:
  ```python
  qdrant_client.upsert(
      collection_name="control_embeddings",
      points=[
          {
              "id": control_id,
              "vector": embeddings.flatten(),
              "payload": {"control_id": control_id, "control_name": name, "framework_id": fid}
          }
      ]
  )
  ```
- SQ8 quantization:
  ```python
  qdrant_client.update_collection(
      collection_name="control_embeddings",
      optimizer_config=OptimizerConfigDiff(
          indexing_threshold=1000,
          quantization_config=ScalarQuantization(
              quantile=0.95,
              always_ram=True
          )
      )
  )
  ```
- Use background task for indexing to avoid API blocking

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for ColBERT embedding computation
- [x] Integration tests for Qdrant storage and retrieval
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/colbert-indexing.md`

#### Dependencies
- Blocked by: INFRA-4, DUALJUDGE-4
- Blocks: CROSSWALK-2

---

### CROSSWALK-2: BGE-M3 Dense Embedding Reranking

**Type**: Story  
**Sprint**: Sprint 5  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, ml, bge-m3, reranking  

#### User Story
> As a **ML engineer**, I want BGE-Reranker-V2-M3 to re-rank the top-20 ColBERT candidates to top-5, so that cross-encoder semantics can further refine the candidate pool before LLM classification.

#### Context and Background
Per TRD Section 8.2, the reranking pipeline must:
- Accept top-20 ColBERT candidates
- Apply BGE-Reranker-V2-M3 cross-encoder
- Return top-5 re-ranked candidates with confidence scores
- Re-rank time: < 2 seconds

#### Acceptance Criteria
1. Given top-20 ColBERT candidates, when `rerank_with_bge(obligation_text, candidates)` is called, then re-ranked top-5 are returned
2. Given re-ranking is complete, when the results are sorted, then they are ordered by BGE reranker score (descending)
3. Given an obligation-control pair, when reranked, then the score reflects semantic similarity (higher = more similar)
4. BGE reranker model: `BAAI/bge-reranker-v2-m3` via HuggingFace
5. Output includes: `control_id`, `rerank_score`, `rank` (1-5)
6. Reranking output stored temporarily in Redis with TTL 300 seconds

#### Technical Notes
- BGE reranking:
  ```python
  from FlagEmbedding import FlagReranker
  
  reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)
  
  pairs = [[obligation_text, candidate["text"]] for candidate in colbert_candidates]
  scores = reranker.compute_score(pairs)
  
  ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:5]
  ```
- Redis caching:
  ```python
  cache_key = f"rckg:rerank:{obligation_id}"
  redis_client.setex(cache_key, 300, json.dumps(ranked))
  ```
- Use GPU if available for faster reranking

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for BGE reranking with sample data
- [x] Integration tests for reranker model
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: CROSSWALK-1
- Blocks: CROSSWALK-3

---

### CROSSWALK-3: LLM Set-Theory Classification

**Type**: Story  
**Sprint**: Sprint 5  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, llm, classification, crosswalk  

#### User Story
> As a **ML engineer**, I want an LLM classifier to assign set-theory relationship types (EQUIVALENT_TO, SUPERSET_OF, SUBSET_OF, INTERSECTS_WITH, NO_RELATIONSHIP) to control-obligation pairs, so that compliance mappings can be established with formal mathematical semantics.

#### Context and Background
Per TRD Section 8.3, the LLM classifier must:
- Accept top-5 BGE-reranked candidates
- Classify each pair into one of 5 set-theory categories
- Output confidence score (0.0-1.0)
- Trigger dual-judge verification for all classifications

#### Acceptance Criteria
1. Given a control-obligation pair, when `classify_relationship(control_text, obligation_text)` is called, then a relationship type is assigned
2. Given the classification, when confidence is evaluated, then it is output as a score (0.0-1.0)
3. Given the classification is SUPERSET_OF or EQUIVALENT_TO, then it is marked as "Requirement Met" with no gap
4. Given the classification is SUBSET_OF or INTERSECTS_WITH, then a gap is flagged for remediation
5. Given the classification is NO_RELATIONSHIP, then a critical gap is flagged for immediate action
6. Classification uses Mistral 8B (local Ollama) with temperature 0.2 for deterministic output

#### Technical Notes
- Classification prompt:
  ```
  Classify the relationship between this control and obligation using set-theory semantics.
  
  Control Text:
  {{control_text}}
  
  Obligation Text:
  {{obligation_text}}
  
  Options:
  - EQUIVALENT_TO: Full 1:1 coverage
  - SUPERSET_OF: Control exceeds requirement (Requirement Met)
  - SUBSET_OF: Partial coverage (Gap Flagged)
  - INTERSECTS_WITH: Partial overlap with distinct goals (Kicks to Human Review)
  - NO_RELATIONSHIP: Control completely misses the mark (Critical Gap Flagged)
  
  Output JSON:
  {
    "relationship_type": "SUPERSET_OF",
    "confidence": 0.92,
    "rationale": "The control covers all obligation requirements and adds additional safeguards..."
  }
  ```
- Use Pydantic model for validation: `/backend/app/schemas/crosswalk_classification.py`
- Store classification results in PostgreSQL `control_obligation_mappings` table

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for LLM classification with sample pairs
- [x] Integration tests for Ollama/Mistral API
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: CROSSWALK-2
- Blocks: CROSSWALK-4

---

### CROSSWALK-4: SATISFIES Edge Creation and Gap Node Generation

**Type**: Story  
**Sprint**: Sprint 5  
**Story Points**: 6  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, graph, memgraph, gaps  

#### User Story
> As a **backend developer**, I want SATISFIES edges to be created in Memgraph for successful control-obligation mappings and Gap nodes to be generated for SUBSET_OF/NO_RELATIONSHIP classifications, so that the knowledge graph accurately represents compliance relationships and deficiencies.

#### Context and Background
Per TRD Section 5.3, the system must:
- Create `[:SATISFIES]` edges with relationship attributes (relationship_type, confidence_score, mapping_date)
- Generate `Gap` nodes for SUBSET_OF and NO_RELATIONSHIP classifications
- Apply Gap lifecycle state machine: NEW -> IN_REMEDIATION -> REMEDIATED -> VERIFIED -> CLOSED
- All graph writes must pass SHACL validation before commit

#### Acceptance Criteria
1. Given a successful classification (EQUIVALENT_TO or SUPERSET_OF), when `create_satisfies_edge(control_id, obligation_id, relationship_type, confidence)` is called, then a SATISFIES edge is created in Memgraph with attributes
2. Given a classification is SUBSET_OF or NO_RELATIONSHIP, when `create_gap_node(obligation_id, relationship_type, severity)` is called, then a Gap node is created with `state=NEW` and `due_date` set to 30 days from now
3. Given a SATISFIES edge is created, when SHACL validation is run against the graph, then the edge passes all shape constraints
4. Given a Gold record exists in PostgreSQL, when the graph write is attempted, then the FK check passes and the commit succeeds
5. SATISFIES edge attributes: `relationship_type`, `confidence_score`, `logic_judge_score`, `technical_judge_score`, `mapping_date`, `source_document_id`
6. Gap node attributes: `gap_id`, `obligation_id`, `severity` (high/medium/low), `state`, `due_date`, `created_at`, `reviewer_id`

#### Technical Notes
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
- SHACL validation before commit using **Memgraph's native MAGE SHACL extension** (consistent with INFRA-9):
  ```python
  # Approach 1: Execute SHACL validation directly via Memgraph Cypher
  # This is the recommended approach for production
  
  def validate_graph_with_memgraph_shacl():
      """
      Use Memgraph's native SHACL validation via MAGE library.
      SHACL shapes must be pre-loaded into Memgraph (see INFRA-9).
      """
      # Query to run SHACL validation
      validation_query = """
      CALL shacl.validate_shapes('shacl_shapes.ttl')
      YIELD result
      RETURN result
      """
      
      results = memgraph.query(validation_query)
      
      for row in results:
          if not row['result'].get('is_valid', False):
              errors = row['result'].get('errors', [])
              raise SHACLValidationFailed(f"Graph validation failed: {errors}")
      
      return {"is_valid": True}
  
  # Approach 2: Validate via Memgraph REST API (alternative)
  def validate_graph_via_rest(shape_file_path: str):
      """
      Alternative: use Memgraph's SHACL REST endpoint if available.
      """
      import requests
      response = requests.post(
          "http://localhost:7447/shacl/validate",
          files={"shapes": open(shape_file_path, "rb")},
          auth=("memgraph_user", "memgraph_password")
      )
      result = response.json()
      if not result.get("valid"):
          raise SHACLValidationFailed(f"Graph validation failed: {result.get('errors', [])}")
      return result
  ```

> **IMPORTANT**: The original implementation incorrectly attempted to use `pySHACL` + `rdflib` with `format="cypher"`, which does not exist. `rdflib` does not have a Cypher parser. The correct approach is to use Memgraph's native SHACL extension (MAGE library), which is already loaded in INFRA-9 via `CALL shacl.load_shapes_from_file()`.
- Use PostgreSQL `golden_controls` as source of truth before Memgraph write

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Cypher query generation
- [x] Integration tests for Memgraph write operations
- [x] SHACL validation tests
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/graph-schema.md`

#### Dependencies
- Blocked by: CROSSWALK-3, INFRA-1
- Blocks: COVERAGE-1

---

## Sprint 6: Coverage Score and Gap Lifecycle

**Sprint Goal**: Implement framework-level coverage scoring and the Gap lifecycle state machine for remediation tracking.

**Rationale**: This sprint adds the visibility and governance layer that allows compliance officers to understand overall compliance posture and track remediation progress.

**Stories in this Sprint**: COVERAGE-1 through COVERAGE-3  
**Total Story Points**: 19

---

### COVERAGE-1: Coverage Score Model

**Type**: Story  
**Sprint**: Sprint 6  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, metrics, coverage  

#### User Story
> As a **compliance officer**, I want a Coverage Score Model that calculates per-framework and aggregate compliance coverage, so that I can understand the organization's compliance posture at a glance.

#### Context and Background
Per TRD Section 8.5, the Coverage Score Model must:
- Calculate coverage percentage per framework (e.g., "NIST CSF: 87% covered")
- Calculate aggregate coverage across all frameworks
- Track coverage changes over time (coverage_delta)
- Generate alerts when coverage drops below threshold (e.g., < 80%)

#### Acceptance Criteria
1. Given all control-obligation mappings exist, when `calculate_framework_coverage(framework_id)` is called, then a coverage percentage is returned
2. Given the coverage is calculated, when the result is compared to the previous snapshot, then coverage_delta is computed correctly
3. Given coverage drops below 80%, when the calculation is performed, then a `coverage.alert` event is published to Kafka
4. Coverage calculation includes: total_obligations, mapped_obligations, equivalent_count, superset_count, subset_count, no_relationship_count
5. Coverage breakdown by control type: automated_count, manual_count, preventive_count, detective_count
6. Results cached in Redis with TTL 300 seconds

#### Technical Notes
- Coverage calculation query:
  ```sql
  SELECT 
      COUNT(DISTINCT o.id) AS total_obligations,
      COUNT(DISTINCT CASE WHEN m.relationship_type IN ('EQUIVALENT_TO', 'SUPERSET_OF') THEN m.id END) AS mapped_obligations,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'EQUIVALENT_TO' THEN m.id END) AS equivalent_count,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'SUPERSET_OF' THEN m.id END) AS superset_count,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'SUBSET_OF' THEN m.id END) AS subset_count,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'NO_RELATIONSHIP' THEN m.id END) AS no_relationship_count
  FROM obligations o
  LEFT JOIN control_obligation_mappings m ON o.id = m.obligation_id
  WHERE o.framework_id = $framework_id
  ```
- Coverage percentage formula:
  ```python
  coverage_percentage = (equivalent_count + superset_count) / total_obligations * 100
  ```
- Kafka alert:
  ```python
  kafka_producer.send(
      "coverage.alert",
      value={
          "framework_id": framework_id,
          "metric_name": "coverage_percentage",
          "current_value": coverage_percentage,
          "threshold": 80.0,
          "coverage_delta": delta,
          "timestamp": datetime.utcnow().isoformat()
      }
  )
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for coverage calculation
- [x] Integration tests for Kafka alerting
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: CROSSWALK-4
- Blocks: COVERAGE-2

---

### COVERAGE-2: Gap Lifecycle State Machine

**Type**: Story  
**Sprint**: Sprint 6  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, gap, state-machine  

#### User Story
> As a **risk manager**, I want a Gap lifecycle state machine that tracks remediation progress from NEW to CLOSED, so that I can assign owners, set due dates, and track completion.

#### Context and Background
Per TRD Section 5.3, the Gap lifecycle must:
- States: NEW -> IN_REMEDIATION -> REMEDIATED -> VERIFIED -> CLOSED
- Transitions are triggered by user actions or automated events
- Each state transition is logged with `changed_by` and `changed_at`
- ACCEPTED gaps can have review date extensions

#### Acceptance Criteria
1. Given a Gap node is created, when it is queried, then its initial state is `NEW`
2. Given a Gap is in `NEW` state, when `assign_gap(gap_id, assignee_id)` is called, then the state transitions to `IN_REMEDIATION`
3. Given a Gap is in `IN_REMEDIATION` state, when `mark_remediated(gap_id)` is called, then the state transitions to `REMEDIATED`
4. Given a Gap is in `REMEDIATED` state, when `verify_remediation(gap_id, verified_by)` is called, then the state transitions to `VERIFIED`
5. Given a Gap is in `VERIFIED` state, when `close_gap(gap_id)` is called, then the state transitions to `CLOSED`
6. All state transitions are logged in the `gap_lifecycle_audit` table with `from_state`, `to_state`, `changed_by`, `changed_at`, `notes`

#### Technical Notes
- Gap state machine definition (in `/backend/app/models/gap.py`):
  ```python
  from enum import Enum
  from pydantic import BaseModel
  
  class GapState(str, Enum):
      NEW = "NEW"
      IN_REMEDIATION = "IN_REMEDIATION"
      REMEDIATED = "REMEDIATED"
      VERIFIED = "VERIFIED"
      CLOSED = "CLOSED"
      ACCEPTED = "ACCEPTED"  # For accepted exceptions
  
  class GapTransition(BaseModel):
      from_state: GapState
      to_state: GapState
      allowed: bool
  
  GAP_TRANSITIONS = [
      GapTransition(from_state=GapState.NEW, to_state=GapState.IN_REMEDIATION, allowed=True),
      GapTransition(from_state=GapState.IN_REMEDIATION, to_state=GapState.REMEDIATED, allowed=True),
      GapTransition(from_state=GapState.REMEDIATED, to_state=GapState.VERIFIED, allowed=True),
      GapTransition(from_state=GapState.VERIFIED, to_state=GapState.CLOSED, allowed=True),
      GapTransition(from_state=GapState.NEW, to_state=GapState.ACCEPTED, allowed=True),  # Exception
      GapTransition(from_state=GapState.ACCEPTED, to_state=GapState.IN_REMEDIATION, allowed=True),
  ]
  ```
- State transition validation:
  ```python
  def transition_gap(gap_id: str, to_state: GapState, user_id: str, notes: str = ""):
      gap = get_gap(gap_id)
      current_state = gap.state
      
      # Check if transition is allowed
      allowed = any(
          t.from_state == current_state and t.to_state == to_state 
          for t in GAP_TRANSITIONS
      )
      
      if not allowed:
          raise InvalidGapTransition(f"Cannot transition from {current_state} to {to_state}")
      
      # Update gap
      update_gap(gap_id, state=to_state)
      
      # Log transition
      create_lifecycle_audit(
          gap_id=gap_id,
          from_state=current_state,
          to_state=to_state,
          changed_by=user_id,
          changed_at=datetime.utcnow(),
          notes=notes
      )
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for state machine transitions
- [x] Integration tests for gap lifecycle API
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: CROSSWALK-4
- Blocks: None

---

### COVERAGE-3: Coverage Score Temporal Workflow

**Type**: Story  
**Sprint**: Sprint 6  
**Story Points**: 3  
**Priority**: Medium  
**Assigned To**: DevOps Engineer  
**Labels**: infrastructure, temporal, workflow  

#### User Story
> As a **system**, I want a daily scheduled Temporal workflow that recalculates coverage scores and publishes alerts, so that the coverage metrics remain current without manual intervention.

#### Context and Background
Per TRD Section 19.2, the `coverage_score_workflow` must:
- Run daily at 06:00 UTC via Cron trigger
- Calculate coverage for all registered frameworks
- Publish `coverage.alert` events when thresholds are breached
- Update dashboard cache with new scores

#### Acceptance Criteria
1. Given the Temporal workflow is configured with cron trigger `0 6 * * *`, when it runs, then coverage is calculated for all frameworks
2. Given coverage is breached, when the workflow task runs, then a `coverage.alert` Kafka message is published
3. Given coverage is not breached, when the workflow task runs, then only the coverage score is updated without alerting
4. Workflow includes error handling: if coverage calculation fails, the failure is logged and an alert is sent to Slack/Email
5. Workflow logs all coverage scores to PostgreSQL `coverage_scores_history` table for trend analysis
6. Workflow is idempotent and can be replayed without side effects

#### Technical Notes
- Temporal workflow definition (in `/backend/app/workflows/coverage_score_workflow.py`):
  ```python
  from temporalio import workflow
  from temporalio.activity import define as activity_def
  from datetime import timedelta
  
  @workflow.defn
  class CoverageScoreWorkflow:
      @workflow.run
      async def run(self) -> Dict:
          # Activity: Calculate coverage for all frameworks
          coverage_data = await workflow.execute_activity(
              "calculate_coverage_activity",
              start_to_close_timeout=workflow.timedelta(minutes=10)
          )
          
          # Activity: Publish alerts for breached thresholds
          await workflow.execute_activity(
              "publish_alerts_activity",
              args=[coverage_data],
              start_to_close_timeout=workflow.timedelta(minutes=5)
          )
          
          return coverage_data
  
  @activity_def
  async def calculate_coverage() -> Dict:
      from backend.app.metrics.coverage import calculate_all_frameworks
      return calculate_all_frameworks()
  
  @activity_def
  async def publish_alerts(coverage_data: Dict):
      from backend.app.metrics.alerting import publish_coverage_alerts
      publish_coverage_alerts(coverage_data)
  ```
  
  Cron trigger setup:
  ```python
  from temporalio.client import Client
  
  client = await Client.connect("localhost:7233")
  await client.start_workflow(
      "CoverageScoreWorkflow",
      id="coverage-score-daily",
      task_queue="ingestion-task-queue",
      cron_schedule="0 6 * * *",  # Daily at 06:00 UTC
  )
  ```
- PostgreSQL history table:
  ```sql
  CREATE TABLE coverage_scores_history (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      framework_id VARCHAR(255),
      coverage_percentage DECIMAL(5,2),
      total_obligations INTEGER,
      mapped_obligations INTEGER,
      snapshot_date DATE,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for coverage calculation
- [x] Integration tests for Temporal workflow execution
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: COVERAGE-1
- Blocks: None

---

## Sprint 7: GraphRAG Query Interface

**Sprint Goal**: Implement the GraphRAG query interface that answers compliance questions using hybrid retrieval (vector + graph traversal).

**Rationale**: This sprint provides the user-facing query interface that makes the knowledge graph queryable and useful for compliance officers.

**Stories in this Sprint**: GRAG-1 through GRAG-4  
**Total Story Points**: 26

---

### GRAG-1: Hybrid Retrieval Pipeline

**Type**: Story  
**Sprint**: Sprint 7  
**Story Points**: 10  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, rag, retrieval, graph  

#### User Story
> As a **compliance officer**, I want a hybrid retrieval pipeline that combines dense vector search with graph traversal, so that I can get comprehensive answers to compliance questions.

#### Context and Background
Per TRD Section 10.1, GraphRAG must:
- Stage 1: Dense vector search (BGE-M3) to identify top-K candidate nodes
- Stage 2: One-hop graph traversal from candidate nodes to extract semantic subgraph
- Stage 3: Combined result passed to LLM for grounded synthesis
- Query response time: < 5 seconds p95

#### Acceptance Criteria
1. Given a natural language query, when `graphrag_query(query)` is called, then dense vector search returns top-10 candidate nodes from Qdrant
2. Given candidates are retrieved, when graph traversal is executed, then one-hop neighbors are fetched from Memgraph
3. Given the subgraph is extracted, when it is combined with vector results, then the LLM receives both raw text and structured graph context
4. Query response time: < 5 seconds p95 for queries against active graph
5. Context includes: retrieved chunks, graph nodes, graph edges, relationship types
6. Results cached in Redis with TTL 300 seconds

#### Technical Notes
- Dense vector search:
  ```python
  from qdrant_client import QdrantClient
  
  client = QdrantClient("localhost", port=6333)
  
  query_embedding = embedding_model.encode(query)
  
  search_results = client.search(
      collection_name="document_chunks",
      query_vector=query_embedding,
      limit=10,
      query_filter=Filter(must=[
        FieldCondition(key="ai-input", match=MatchValue(value="yes"))
      ])
  )
  ```
- Graph traversal (using `gremlin` or `memgraph` client):
  ```python
  from memgraph import Memgraph
  
  mg = Memgraph()
  
  query = """
  MATCH (n)-[r]->(neighbor)
  WHERE n.id IN $candidate_ids
  RETURN n, r, neighbor
  LIMIT 50
  """
  
  results = mg.execute(query, {"candidate_ids": candidate_ids})
  ```
- Context assembly:
  ```python
  def assemble_context(vector_results, graph_results, query):
      return {
          "query": query,
          "retrieved_chunks": [r.text for r in vector_results],
          "graph_nodes": [node.to_dict() for node in graph_results],
          "graph_edges": [edge.to_dict() for edge in graph_results],
          "context_window": "10000 tokens"
      }
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for retrieval pipeline
- [x] Integration tests for Qdrant + Memgraph
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/graphrag.md`

#### Dependencies
- Blocked by: INFRA-4, INFRA-1
- Blocks: GRAG-2

---

### GRAG-2: LLM Synthesis with Grounding

**Type**: Story  
**Sprint**: Sprint 7  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: backend, llm, synthesis, rag  

#### User Story
> As a **ML engineer**, I want an LLM synthesizer that generates answers grounded exclusively in graph context, so that hallucinations are eliminated and all answers are traceable to source nodes.

#### Context and Background
Per TRD Section 10.2, the LLM synthesizer must:
- Accept structured context (chunks + subgraph)
- Generate answers grounded in the context
- Include citations for all claims (node IDs, edge paths)
- Reject queries where context is insufficient (return "I don't have enough information")

#### Acceptance Criteria
1. Given graph context is provided, when `synthesize_answer(context)` is called, then the LLM generates an answer with citations
2. Given the answer includes a claim, when the claim is verified, then it is linked to a specific node ID or edge path in the context
3. Given the context is insufficient, when `synthesize_answer(context)` is called, then the LLM returns "I don't have enough information to answer this question"
4. LLM output format: `{ "answer": "...", "citations": [{"node_id": "...", "text": "..."}, ...] }`
5. Answer generation uses local Mistral 8B via Ollama with temperature 0.3
6. All synthesis traces are logged to Langfuse with `trace_id`

#### Technical Notes
- Synthesis prompt:
  ```
  You are a compliance assistant. Answer the following question using ONLY the provided context.
  If the context does not contain sufficient information, say "I don't have enough information to answer this question."
  
  Question: {{query}}
  
  Context:
  {{context_chunks}}
  
  Graph Context:
  {{graph_nodes}}
  {{graph_edges}}
  
  Requirements:
  1. All claims must be backed by citations
  2. Cite using the format: [Node: node_id]
  3. Do not make claims that cannot be verified from the context
  
  Output JSON:
  {
    "answer": "...",
    "citations": [
      {"node_id": "node-123", "text": "excerpt from context"}
    ]
  }
  ```
- Output validation with Pydantic:
  ```python
  class AnswerWithCitations(BaseModel):
      answer: str
      citations: List[dict]
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for synthesis with sample context
- [x] Integration tests for Ollama/Mistral API
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: GRAG-1
- Blocks: GRAG-3

---

### GRAG-3: Temporal Compliance Query Support

**Type**: Story  
**Sprint**: Sprint 7  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, temporal, query  

#### User Story
> As a **compliance officer**, I want temporal query support so that I can query the compliance posture as of any historical date, so that auditors can verify historical compliance states.

#### Context and Background
Per TRD Section 4.2 and Section 6.1, temporal queries must:
- Accept `as_of_date` parameter on any query
- Return compliance posture that existed at that point in time
- Respect bitemporal tags (`valid_from`, `valid_to`, `ingested_at`)
- Exclude superseded obligations from active queries

#### Acceptance Criteria
1. Given an `as_of_date` parameter, when a query is executed, then only obligations with `valid_from <= as_of_date AND (valid_to IS NULL OR valid_to > as_of_date)` are returned
2. Given a temporal query, when the result is verified, then superseded regulations are excluded from the result
3. Given a historical query for a date before any data was ingested, when the query is executed, then an empty result is returned with message "No data exists for this date"
4. Temporal query API endpoint: `GET /api/v1/query?as_of_date=2024-01-01&q=...`
5. Temporal queries use PostgreSQL cold store for dates > 90 days ago (hot/cold separation)
6. Query result includes `query_date` in the response metadata

#### Technical Notes
- Temporal filter in SQL:
  ```sql
  WHERE valid_from <= :as_of_date
    AND (valid_to IS NULL OR valid_to > :as_of_date)
  ```
- Hot/cold routing logic:
  ```python
  def route_temporal_query(as_of_date: datetime) -> str:
      today = datetime.utcnow()
      days_ago = (today - as_of_date).days
      
      if days_ago > 90:
          return "cold_store"  # PostgreSQL
      else:
          return "hot_store"  # Memgraph
  ```
- PostgreSQL cold store query:
  ```sql
  SELECT * FROM golden_controls
  WHERE valid_from <= $as_of_date
    AND (valid_to IS NULL OR valid_to > $as_of_date)
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for temporal query logic
- [x] Integration tests for hot/cold routing
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: GRAG-2
- Blocks: GRAG-4

---

### GRAG-4: Query API and Response Caching

**Type**: Story  
**Sprint**: Sprint 7  
**Story Points**: 3  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, api, cache  

#### User Story
> As a **compliance officer**, I want a REST API for GraphRAG queries with response caching, so that I can quickly query the system and repeated queries are served from cache.

#### Context and Background
Per TRD Section 4.2, the query API must:
- Expose `POST /api/v1/query` endpoint
- Accept query text and optional `as_of_date` parameter
- Cache responses in Redis with TTL 300 seconds
- Include rate limiting (max 10 queries/minute per user)

#### Acceptance Criteria
1. Given a valid query is submitted via `POST /api/v1/query`, then the response is returned in < 5 seconds
2. Given the same query is submitted twice within 300 seconds, when the second request is made, then the cached result is returned in < 100ms
3. Given a user exceeds 10 queries/minute, when the rate limit is breached, then HTTP 429 is returned with `{"error": "Rate limit exceeded"}`
4. Query response includes: `answer`, `citations[]`, `query_time_ms`, `context_size_tokens`
5. Query logs are written to PostgreSQL `query_logs` table for audit trail
6. Rate limiting uses Redis with key format: `rckg:rate_limit:{user_id}:{minute_window}`

#### Technical Notes
- API endpoint:
  ```python
  @router.post("/query")
  async def query_graph(
      request: QueryRequest,
      user: User = Depends(get_current_user),
      redis: Redis = Depends(get_redis)
  ):
      # Rate limiting
      rate_key = f"rckg:rate_limit:{user.id}:{int(time.time() // 60)}"
      count = await redis.incr(rate_key)
      if count == 1:
          await redis.expire(rate_key, 60)
      if count > 10:
          raise HTTPException(status_code=429, detail="Rate limit exceeded")
      
      # Check cache
      cache_key = f"rckg:query:{user.id}:{hash(request.query)}"
      cached = await redis.get(cache_key)
      if cached:
          return json.loads(cached)
      
      # Execute query
      result = await graphrag_query(request.query, request.as_of_date)
      
      # Cache result
      await redis.setex(cache_key, 300, json.dumps(result))
      
      # Log query
      await log_query(user.id, request.query, result)
      
      return result
  ```
- Query logging:
  ```sql
  CREATE TABLE query_logs (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID,
      query_text TEXT,
      response_time_ms INTEGER,
      cache_hit BOOLEAN,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for API endpoint
- [x] Integration tests for caching and rate limiting
- [x] All acceptance criteria verified
- [x] OpenAPI documentation generated

#### Dependencies
- Blocked by: GRAG-3
- Blocks: None

---

## Sprint 8: OSCAL Export Engine

**Sprint Goal**: Implement OSCAL 1.1.3 export functionality for compliance artifacts.

**Rationale**: This sprint provides the export capability that generates machine-readable compliance artifacts for GRC platforms and auditors.

**Stories in this Sprint**: OSCAL-1 through OSCAL-3  
**Total Story Points**: 22

---

### OSCAL-1: OSCAL Schema Mapping

**Type**: Story  
**Sprint**: Sprint 8  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, oscal, export  

#### User Story
> As a **backend developer**, I want OSCAL 1.1.3 schema mapping that translates graph nodes to OSCAL components, so that compliance artifacts can be exported in the NIST standard format.

#### Context and Background
Per TRD Section 13.1, OSCAL export must:
- Map Control nodes to OSCAL `control` components
- Map Obligation nodes to OSCAL `required` statements
- Include provenance metadata: confidence scores, mapping rationale, responsible_party
- Support JSON, XML, and YAML output formats

#### Acceptance Criteria
1. Given a control and its obligations exist in the graph, when `generate_oscal_ssp(control_id)` is called, then a valid OSCAL SSP JSON is generated
2. Given the OSCAL is generated, when it is validated against NIST OSCAL schema, then validation passes without errors
3. Given the export includes mapping metadata, when the JSON is inspected, then it includes `confidence_score`, `logic_judge_score`, `technical_judge_score` fields
4. Export includes `responsible_party` field for each mapping
5. Output formats: JSON (default), XML, YAML
6. OSCAL output stored in MinIO `oscal-exports` bucket

#### Technical Notes
- OSCAL SSP structure:
  ```json
  {
    "oscal-version": "1.1.3",
    "uuid": "export-uuid",
    "metadata": {
      "title": "System Security Plan",
      "last-modified": "2026-04-13T00:00:00Z",
      "version": "1.0",
      "organization": {
        "name": "RCKG Organization"
      }
    },
    "profile": {
      "uuid": "nist-sp-800-53-rev5",
      "title": "NIST SP 800-53 Rev 5",
      " parties": [...]
    },
    "implementation": {
      "system": {
        "uuid": "system-uuid",
        "description": "RCKG Compliance System"
      },
      "validated": [
        {
          "control-id": "AC-1",
          "status": "implemented",
          "statement-id": "AC-1.stmt.a",
          "description": "Control implementation description",
          "props": [
            {
              "name": "confidence_score",
              "value": "0.95"
            },
            {
              "name": "logic_judge_score",
              "value": "0.97"
            },
            {
              "name": "technical_judge_score",
              "value": "1.0"
            },
            {
              "name": "responsible_party",
              "value": "compliance-team"
            }
          ]
        }
      ]
    }
  }
  ```
- Use `trestle` Python library (IBM's open-source OSCAL tool) or `jsonschema` directly:
  ```python
  from trestle.core.validator import Validator
  from trestle.oscal import SSP
  
  # Load OSCAL file
  ssp = SSP.oscal_read("ssp.json")
  
  # Validate against NIST OSCAL 1.1.3 schema
  validator = Validator()
  validation_results = validator.run(ssp)
  if not validation_results.is_valid:
      raise OSCALValidationError(f"Validation failed: {validation_results.message}")
  ```
  
  OR using jsonschema directly:
  ```python
  import jsonschema
  
  with open("oscal_1.1.3_schema.json") as f:
      schema = json.load(f)
  
  jsonschema.validate(instance=oscal_data, schema=schema)
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for OSCAL schema mapping
- [x] Integration tests for OSCAL validation
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/oscal-export.md`

#### Dependencies
- Blocked by: CROSSWALK-4
- Blocks: OSCAL-2

---

### OSCAL-2: POA&M and SAR Generation

**Type**: Story  
**Sprint**: Sprint 8  
**Story Points**: 7  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, oscal, export  

#### User Story
> As a **compliance officer**, I want Plan of Action and Milestones (POA&M) and Security Assessment Report (SAR) OSCAL exports, so that gaps and test results can be documented in the NIST standard format.

#### Context and Background
Per TRD Section 13.2, OSCAL exports must include:
- POA&M: Lists all gaps (SUBSET_OF, NO_RELATIONSHIP) with remediation plans
- SAR: Documents control testing results and effectiveness scores
- Both formats follow NIST OSCAL 1.1.3 specification

#### Acceptance Criteria
1. Given gaps exist in the system, when `generate_oscal_poam(framework_id)` is called, then a valid OSCAL POA&M JSON is generated
2. Given the POA&M is generated, when it is validated against NIST OSCAL schema, then validation passes
3. POA&M includes: gap_id, obligation_id, severity, state, due_date, responsible_party, remediation_plan
4. Given control tests exist, when `generate_oscal_sar(framework_id)` is called, then a valid OSCAL SAR JSON is generated
5. SAR includes: test_id, control_id, test_date, result, tester_id, evidence_references
6. Export includes provenance metadata for all fields

#### Technical Notes
- POA&M OSCAL structure:
  ```json
  {
    "oscal-version": "1.1.3",
    "uuid": "poam-uuid",
    "metadata": {
      "title": "Plan of Action and Milestones",
      "last-modified": "2026-04-13T00:00:00Z"
    },
    "plan-of-action-and-milestones": {
      "uuid": "poam-system-uuid",
      "gaps": [
        {
          "gap-id": "gap-123",
          "identified": "2026-04-01",
          "governance": "compliance-team",
          "remediation": {
            "description": "Implement additional access controls",
            "milestones": [
              {
                "milestone": {
                  "title": "Design phase",
                  "target": "2026-04-30"
                }
              }
            ]
          },
          "props": [
            {"name": "severity", "value": "high"},
            {"name": "status", "value": "IN_REMEDIATION"}
          ]
        }
      ]
    }
  }
  ```
- SAR OSCAL structure:
  ```json
  {
    "oscal-version": "1.1.3",
    "uuid": "sar-uuid",
    "metadata": {
      "title": "Security Assessment Report"
    },
    "assessment-results": {
      "uuid": "assessment-uuid",
      "assessed-controls": [
        {
          "control-id": "AC-1",
          "assessment-objects": [...],
          "findings": [
            {
              "title": "Control AC-1 assessment",
              "description": "Control was tested and found effective",
              "props": [
                {"name": "result", "value": "passed"},
                {"name": "test_date", "value": "2026-04-10"}
              ]
            }
          ]
        }
      ]
    }
  }
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for POA&M generation
- [x] Unit tests for SAR generation
- [x] Integration tests for OSCAL validation
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: OSCAL-1
- Blocks: OSCAL-3

---

### OSCAL-3: OSCAL Export API and Temporal Workflow

**Type**: Story  
**Sprint**: Sprint 8  
**Story Points**: 7  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, api, oscal, temporal  

#### User Story
> As a **compliance officer**, I want an OSCAL export API endpoint and scheduled Temporal workflow, so that I can generate and export compliance artifacts on demand or on a schedule.

#### Context and Background
Per TRD Section 19.1, OSCAL export must be accessible via:
- REST API: `POST /api/v1/oscal/export`
- Scheduled Temporal workflow: `oscal_export_workflow` with cron trigger running monthly at 00:00 UTC

#### Acceptance Criteria
1. Given a valid export request, when `POST /api/v1/oscal/export` is called, then the OSCAL file is generated and stored in MinIO
2. Given the export is complete, when the API responds, then it returns a download URL: `{"download_url": "https://minio.internal/oscal-exports/oscal-123.json"}`
3. Given the monthly Temporal workflow runs, when it executes, then OSCAL exports are generated for all registered frameworks
4. Export includes: `requested_by`, `requested_at`, `export_type` (SSP/POA&M/SAR)
5. Export files are versioned with timestamp: `oscal-{framework_id}-{timestamp}.json`
6. Export API includes authentication: requires valid API token or OAuth2 token

#### Technical Notes
- API endpoint:
  ```python
  @router.post("/oscal/export")
  async def export_oscal(
      request: OSCALExportRequest,
      user: User = Depends(get_current_user),
      s3: MinIO = Depends(get_minio)
  ):
      # Generate OSCAL
      oscal_data = await generate_oscal_export(
          framework_id=request.framework_id,
          export_type=request.export_type,
          requested_by=user.id
      )
      
      # Save to MinIO
      filename = f"oscal-{request.framework_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
      s3.put_object(
          bucket="oscal-exports",
          object_name=filename,
          data=oscal_data,
          length=len(oscal_data)
      )
      
      # Return download URL
      return {
          "download_url": f"/api/v1/oscal/download/{filename}",
          "filename": filename,
          "export_type": request.export_type
      }
  ```
- Temporal workflow (similar to COVERAGE-3, but for OSCAL exports):
  ```python
  @workflow.defn
  class OscalExportWorkflow:
      @workflow.run
      async def run(self, framework_ids: List[str]) -> Dict:
          # Activity: Generate OSCAL for each framework
          for fid in framework_ids:
              await workflow.execute_activity(
                  "generate_oscal_activity",
                  args=[fid],
                  start_to_close_timeout=workflow.timedelta(hours=1)
              )
          
          return {"status": "completed", "framework_count": len(framework_ids)}
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for OSCAL export API
- [x] Integration tests for Temporal workflow
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: OSCAL-1, OSCAL-2
- Blocks: None

---

## Sprint 9: Observability and Monitoring

**Sprint Goal**: Implement comprehensive observability including Langfuse tracing, Prometheus metrics, and Grafana dashboards.

**Rationale**: This sprint provides the visibility layer that allows operators to monitor system health, trace AI decisions, and debug issues.

**Stories in this Sprint**: OBSERV-1 through OBSERV-3  
**Total Story Points**: 18

---

### OBSERV-1: Langfuse Tracing Integration

**Type**: Story  
**Sprint**: Sprint 9  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, observability, langfuse, tracing  

#### User Story
> As a **developer**, I want Langfuse tracing integrated throughout the pipeline, so that I can trace AI decisions, prompt versions, and agent actions for debugging and audit.

#### Context and Background
Per TRD Section 7.3 and Section 16.1, Langfuse must:
- Trace all LLM interactions with prompt version tracking
- Log agent actions with context
- Enable search and filtering by trace_id, user_id, workflow_id
- Include latency metrics for each step

#### Acceptance Criteria
1. Given an LLM call is made, when Langfuse tracing is enabled, then a span is created with prompt, input, output, latency
2. Given the prompt is updated, when tracing is executed, then the prompt version is logged and the correct version is used
3. Given an agent action is performed, when it is traced, then the action, input, output, and context are logged
4. Langfuse dashboard shows: trace count, error rate, average latency, prompt usage
5. All traces include `trace_id` that can be used to follow the full pipeline execution
6. Traces are exported to PostgreSQL for long-term retention (90 days)

#### Technical Notes
- Langfuse initialization:
  ```python
  from langfuse import Langfuse
  
  langfuse = Langfuse(
      public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
      secret_key=os.environ["LANGFUSE_SECRET_KEY"],
      host="http://localhost:3000"  # Self-hosted Langfuse
  )
  ```
- Tracing an LLM call:
  ```python
  def trace_llm_call(prompt: str, input_data: dict, model: str):
      trace = langfuse.trace(
          name="llm_call",
          input=input_data,
          metadata={"model": model, "prompt_version": "v1.2"}
      )
      
      generation = trace.generation(
          name="llm_generation",
          model=model,
          prompt=prompt,
          input=input_data,
          start_time=datetime.utcnow()
      )
      
      try:
          output = ollama_chat(model, prompt)
          generation.update(output=output, end_time=datetime.utcnow())
          return output
      except Exception as e:
          generation.update(
              output={"error": str(e)},
              end_time=datetime.utcnow()
          )
          raise
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for Langfuse integration
- [x] Integration tests for trace creation and retrieval
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/observability.md`

#### Dependencies
- Blocked by: INFRA-1
- Blocks: OBSERV-2

---

### OBSERV-2: Prometheus Metrics and Grafana Dashboards

**Type**: Story  
**Sprint**: Sprint 9  
**Story Points**: 6  
**Priority**: High  
**Assigned To**: DevOps Engineer  
**Labels**: infrastructure, prometheus, grafana, metrics  

#### User Story
> As a **DevOps engineer**, I want Prometheus metrics and Grafana dashboards, so that I can monitor system health, pipeline performance, and AI model accuracy.

#### Context and Background
Per TRD Section 16.1, monitoring must include:
- Pipeline metrics: ingestion rate, extraction latency, validation pass rate
- Graph metrics: node count, edge count, query latency
- AI metrics: LLM confidence scores, judge agreement rates, mapping accuracy
- Dashboards: System Health, Pipeline Performance, AI Accuracy

#### Acceptance Criteria
1. Given the system is running, when Prometheus scrapes metrics, then all defined metrics are exposed
2. Given Grafana is configured, when dashboards are loaded, then the System Health, Pipeline Performance, and AI Accuracy dashboards display correctly
3. Pipeline metrics include: `ingestion_total`, `extraction_latency_seconds`, `validation_pass_rate`
4. Graph metrics include: `graph_node_count`, `graph_edge_count`, `query_latency_seconds`
5. AI metrics include: `llm_confidence_score`, `judge_agreement_rate`, `mapping_accuracy`
6. Alerts configured: High error rate (>5%), Low validation pass rate (<90%), High query latency (>5s)

#### Technical Notes
- Prometheus metrics definition (using `prometheus-client`):
  ```python
  from prometheus_client import Counter, Histogram, Gauge
  
  INGESTION_TOTAL = Counter(
      'rckg_ingestion_total',
      'Total number of documents ingested',
      ['status']  # status: success, failure, duplicate
  )
  
  EXTRACTION_LATENCY = Histogram(
      'rckg_extraction_latency_seconds',
      'Extraction pipeline latency',
      buckets=[0.5, 1, 2, 5, 10, 30, 60]
  )
  
  QUERY_LATENCY = Histogram(
      'rckg_query_latency_seconds',
      'Query latency',
      buckets=[0.1, 0.5, 1, 2, 5, 10]
  )
  
  GRAPH_NODE_COUNT = Gauge(
      'rckg_graph_node_count',
      'Total number of nodes in the graph',
      ['type']  # type: control, obligation, gap, etc.
  )
  ```
- Grafana dashboard JSON: Pre-configured dashboards stored in `grafana/dashboards/`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for metrics export
- [x] Integration tests for Prometheus scraping
- [x] All acceptance criteria verified
- [x] Grafana dashboards deployed and verified

#### Dependencies
- Blocked by: INFRA-1, OBSERV-1
- Blocks: OBSERV-3

---

### OBSERV-3: Audit Log Aggregation

**Type**: Story  
**Sprint**: Sprint 9  
**Story Points**: 4  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, audit, logging  

#### User Story
> As a **compliance officer**, I want an immutable audit log of all system actions, so that I can demonstrate audit trail compliance for regulatory examinations.

#### Context and Background
Per TRD Section 11.4 and Section 16.2, audit logging must:
- Log all agent actions, graph writes, user queries
- Be immutable and append-only
- Include: actor_id, action, resource_id, timestamp, ip_address, user_agent
- Retain logs for 10 years (regulatory requirement)

#### Acceptance Criteria
1. Given an action occurs, when audit logging is enabled, then a row is inserted into `audit_log` table
2. Given a log entry is created, when an attempt is made to modify or delete it, then the operation is rejected
3. Audit log includes: `id`, `event_type`, `actor_id`, `resource_type`, `resource_id`, `action`, `metadata` (JSONB), `timestamp`, `ip_address`, `user_agent`
4. Query audit logs via API: `GET /api/v1/audit?event_type=...&actor_id=...&from_date=...`
5. Audit log retention: 10 years (archival to cold storage after 1 year)
6. Audit logs are searchable and filterable via Grafana Loki or Elasticsearch

#### Technical Notes
- Audit log table:
  ```sql
  CREATE TABLE audit_log (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      event_type VARCHAR(100) NOT NULL,
      actor_id UUID NOT NULL,
      resource_type VARCHAR(100),
      resource_id UUID,
      action VARCHAR(100) NOT NULL,
      metadata JSONB,
      timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      ip_address INET,
      user_agent TEXT,
      CHECK (timestamp >= NOW() - INTERVAL '10 years')
  );
  
  CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
  CREATE INDEX idx_audit_log_actor_id ON audit_log(actor_id);
  CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
  ```
- Audit log decorator:
  ```python
  def audit_log(event_type: str, actor_id: UUID):
      def decorator(func):
          async def wrapper(*args, **kwargs):
              # Execute function
              result = await func(*args, **kwargs)
              
              # Log action
              await create_audit_log(
                  event_type=event_type,
                  actor_id=actor_id,
                  resource_type=...,
                  resource_id=...,
                  action=...,
                  metadata=...
              )
              
              return result
          return wrapper
      return decorator
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] Unit tests for audit logging
- [x] Integration tests for audit log queries
- [x] All acceptance criteria verified
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-2
- Blocks: None

---

## Sprint 10: Testing and Quality Assurance

**Sprint Goal**: Implement comprehensive testing pyramid including unit, integration, E2E, and adversarial tests.

**Rationale**: This sprint ensures the system meets the accuracy and quality requirements specified in the TRD before production deployment.

**Stories in this Sprint**: TEST-1 through TEST-3  
**Total Story Points**: 21

---

### TEST-1: Unit and Integration Test Suite

**Type**: Story  
**Sprint**: Sprint 10  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: QA Engineer  
**Labels**: testing, unit, integration  

#### User Story
> As a **QA engineer**, I want a comprehensive unit and integration test suite, so that code changes can be validated and regressions can be caught early.

#### Context and Background
Per TRD Section 15, the testing pyramid must include:
- Unit tests: All backend functions, models, schemas
- Integration tests: Database operations, Qdrant operations, Memgraph operations, Kafka message production/consumption
- Test coverage target: > 80% for critical paths
- All tests must pass before merge to main branch

#### Acceptance Criteria
1. Given a code change is made, when unit tests are run, then all unit tests pass
2. Given integration tests are configured, when they are executed, then all integration tests pass
3. Test coverage is > 80% for critical paths (ingestion, extraction, validation, crosswalk)
4. CI pipeline includes test execution: all tests must pass before merge
5. Test fixtures are defined for: mock LLM responses, mock database records, mock Kafka messages
6. Tests are organized in `/backend/tests/` directory with clear naming conventions

#### Technical Notes
- Test organization:
  ```
  backend/tests/
  ├── unit/
  │   ├── test_extraction.py
  │   ├── test_judge.py
  │   ├── test_classification.py
  │   └── ...
  ├── integration/
  │   ├── test_ingestion.py
  │   ├── test_database.py
  │   ├── test_qdrant.py
  │   ├── test_memgraph.py
  │   └── test_kafka.py
  ├── fixtures/
  │   ├── mock_llm_responses.py
  │   ├── mock_database.py
  │   └── mock_kafka.py
  └── conftest.py
  ```
- pytest configuration in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  python_files = ["test_*.py"]
  addopts = "-v --cov=backend --cov-report=html --cov-report=term-missing"
  ```

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] All acceptance criteria verified
- [x] CI pipeline configured
- [x] Documentation in `docs/01-initial/testing.md`

#### Dependencies
- Blocked by: None (can start early in parallel with other sprints)
- Blocks: TEST-2

---

### TEST-2: End-to-End Test Pipeline

**Type**: Story  
**Sprint**: Sprint 10  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: QA Engineer  
**Labels**: testing, e2e, pipeline  

#### User Story
> As a **QA engineer**, I want end-to-end test pipelines that simulate full document ingestion to OSCAL export, so that the complete system can be validated.

---

### HITL-1: Human-in-the-Loop Approval UI (Frontend)

**Type**: Story  
**Sprint**: Sprint 4  
**Story Points**: 13  
**Priority**: High  
**Assigned To**: Frontend Engineer  
**Labels**: frontend, ui, hitl, react  

#### User Story
> As a **compliance reviewer**, I want a web-based approval interface that presents low-confidence AI extractions and mappings for human review, so that I can approve or reject determinations before they commit to the production graph.

#### Context and Background
The CTO review identified that no sprint story existed for building the HITL approval UI. This is critical because:
- Temporal workflows pause at approval gates awaiting callback signals
- Without the UI, reviewers cannot send approval callbacks
- Every HITL gate becomes a dead end without this interface

The UI must support review of:
1. Extraction reviews (confidence < 0.70)
2. Logic Judge rejections (semantic faithfulness < 0.95)
3. Technical Judge rejections (parameter precision < 1.00)
4. SHACL validation failures

#### Acceptance Criteria
1. Given low-confidence items exist in the queue, when the reviewer navigates to `/reviews/extractions`, then the queue displays pending items with original text and extracted output
2. Given a review item is displayed, when the reviewer clicks "Approve", then the approval is submitted via Temporal signal and the item is removed from the queue
3. Given a review item is displayed, when the reviewer clicks "Reject", then they must provide feedback before submitting
4. Given a review item is displayed, when the reviewer clicks "Edit", then they can modify the extracted text before approval
5. Review dashboard shows: total pending, average wait time, SLA breach alerts (48hr extraction, 72hr mapping)
6. All review actions are logged to PostgreSQL `review_log` table with reviewer_id, timestamp, decision
7. Real-time updates via WebSockets when new items are added to queue

#### Technical Notes
- Frontend stack: React + TypeScript + TailwindCSS
- Temporal signal integration:
  ```typescript
  async function submitApproval(reviewId: string, decision: 'approve' | 'reject', notes?: string) {
    await api.post(`/api/v1/reviews/${reviewId}/submit`, { decision, notes });
    // Triggers Temporal signal: human_approval_workflow.resume()
  }
  ```
- WebSocket for real-time queue updates:
  ```typescript
  const ws = new WebSocket(`ws://localhost:8000/ws/reviews?user_id=${userId}`);
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    if (update.type === 'new_item') {
      setQueue([...queue, update.item]);
    }
  };
  ```
- UI components: `ReviewQueue`, `ReviewCard`, `ReviewForm`, `Dashboard`

#### Definition of Done
- [x] Frontend React component for review queue
- [x] Approval/rejection submission via Temporal signals
- [x] Edit mode for modifying extracted text
- [x] Review dashboard with SLA tracking
- [x] WebSocket integration for real-time updates
- [x] Integration tests for review workflow
- [x] Documentation in `docs/01-initial/hitl-ui.md`

#### Dependencies
- Blocked by: DUALJUDGE-4 (extraction workflow), INFRA-6 (Temporal)
- Blocks: DUALJUDGE-4 (completion), WORKFLOW-2

---

### HITL-2: Review API and Backend Integration

**Type**: Story  
**Sprint**: Sprint 4  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, api, hitl  

#### User Story
> As a **backend developer**, I want a REST API that serves review queue data and processes approval callbacks, so that the HITL UI can function properly.

#### Context and Background
This story implements the backend API endpoints that support the HITL UI. It works in tandem with HITL-1.

#### Acceptance Criteria
1. Given a request to `/api/v1/reviews/extractions?status=pending`, then the API returns a paginated list of pending extractions with original text, extracted output, and judge feedback
2. Given a POST to `/api/v1/reviews/{id}/submit` with `decision=approve`, then the approval is recorded in PostgreSQL `review_log` and a Temporal signal is sent
3. Given a POST to `/api/v1/reviews/{id}/submit` with `decision=reject` and `notes`, then the rejection is recorded and the item is returned to the dead-letter queue
4. Given a request to `/api/v1/reviews/stats`, then the API returns dashboard statistics: pending count, average wait time, SLA breaches
5. All endpoints include authentication and the reviewer_id is recorded in `review_log`
6. Review log schema includes: `review_id`, `item_type`, `item_id`, `reviewer_id`, `decision`, `notes`, `submitted_at`, `sla_breached`

#### Technical Notes
- PostgreSQL review_log schema:
  ```sql
  CREATE TABLE review_log (
      review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      item_type VARCHAR(50) NOT NULL,  -- 'extraction' | 'mapping' | 'validation'
      item_id UUID NOT NULL,
      reviewer_id VARCHAR(255) NOT NULL,
      decision VARCHAR(20) NOT NULL,   -- 'approve' | 'reject' | 'edit'
      notes TEXT,
      submitted_at TIMESTAMPTZ DEFAULT NOW(),
      sla_breached BOOLEAN DEFAULT FALSE
  );
  ```
- Temporal signal integration:
  ```python
  @workflow.signal
  def approval_callback(self, approval_id: str, decision: str, reviewer_id: str):
      # Update workflow state and resume
  ```

#### Definition of Done
- [x] REST API endpoints implemented
- [x] PostgreSQL integration
- [x] Temporal signal integration
- [x] Authentication and authorization
- [x] Unit and integration tests
- [x] API documentation

#### Dependencies
- Blocked by: INFRA-2 (PostgreSQL), INFRA-6 (Temporal)
- Blocks: HITL-1

---

# Sprint Plan Summary

## Backlog Health Check

| Metric | Count |
|---|---|
| **Total Sprints** | 10 |
| **Total Stories** | 51 |
| **Total Story Points** | ~308 |
| **Estimated Duration** | 20 weeks (10 sprints) |
| **Risk Stories (Spikes Needed)** | 1 (see Spike Recommendations below) |

## Sprint Distribution

| Sprint | Focus | Stories | Points |
|---|---|---|---|
| **Sprint 0** | **Spike: MinerU Validation** | **SPIKE-1** | **3** |
| Sprint 1 | Infrastructure Foundation | INFRA-1 through INFRA-9 | 41 |
| Sprint 2 | Document Ingestion Pipeline | INGEST-1 through INGEST-5 | 34 |
| Sprint 3 | De Jure Extraction + Observability | EXTRACT-1 through EXTRACT-5, OBSERV-1, DLQ-METRICS-1, GOLDEN50-1 | 52 |
| Sprint 4 | Dual-Judge Validation Backend | DUALJUDGE-1 through DUALJUDGE-4 | 29 |
| Sprint 5 | ColBERT Crosswalk | CROSSWALK-1 through CROSSWALK-4 | 35 |
| Sprint 6 | HITL UI + Accuracy Benchmarks | COVERAGE-1 through COVERAGE-3, HITL-1, HITL-2, TEST-3 | 40 |
| Sprint 7 | GraphRAG Query | GRAG-1 through GRAG-4 | 26 |
| Sprint 8 | OSCAL Export | OSCAL-1 through OSCAL-3 | 22 |
| Sprint 9 | Observability (System Health) | OBSERV-2, OBSERV-3 | 12 |
| Sprint 10 | E2E Testing | TEST-1, TEST-2 | 16 |

## Spike Recommendations

| Spike ID | Topic | Reason | Suggested Outcome |
|---|---|---|---|
| **SPIKE-1** | **MinerU Model Availability** | **MinerU model may not be readily available for local deployment** | **Decision: Confirm model availability and download process, or evaluate alternative parsers** |
| SPIKE-2 | ColBERT Performance on CPU | ColBERT inference may be slow without GPU | POC: Measure inference latency, determine if GPU is required for production |

## Risks to Delivery

| Risk | Impact | Mitigation |
|---|---|---|
| **LLM Model Availability** | Critical - Core AI functionality depends on local LLM models | **SPIKE-1 completed in Sprint 0**; maintain fallback prompts for smaller models |
| **GPU Requirements** | High - ColBERT and dual-judge may require significant GPU resources | SPIKE-2 to quantify requirements; plan for GPU worker pool in production (Sprint 8+) |
| **HITL UI Development** | High - No UI means no callback path for Temporal workflows | **HITL-1 and HITL-2 added to Sprint 4**; ensure frontend resource allocation |
| **Data Quality** | Medium - Extraction quality depends on clean regulatory PDFs | Start with curated sample documents; implement iterative repair loop (Sprint 3) |
| **Team Ramp-up** | Low - New team members may need time to learn the stack | Start with Sprint 1-2 infrastructure work; pair programming on complex stories |

---

#### Context and Background
Per TRD Section 15.3, E2E tests must:
- Simulate full pipeline: PDF upload -> parsing -> extraction -> validation -> crosswalk -> OSCAL export
- Use sample regulatory documents (NIST CSF, ISO 27001, DORA)
- Validate each stage's output
- Run on every PR and nightly

#### Acceptance Criteria
1. Given an E2E test is executed, when a sample PDF is uploaded, then the complete pipeline runs successfully
2. Given the pipeline completes, when the OSCAL export is generated, then it validates against NIST OSCAL schema
3. E2E tests include validation at each stage: parsing output, extraction quality, dual-judge scores, mapping accuracy
4. E2E tests run in isolated Docker Compose environment (fresh data on each run)
5. E2E test results are reported to GitHub Actions and stored as artifacts
6. Nightly E2E runs trigger full system health check

#### Technical Notes
- E2E test example (in `/backend/tests/e2e/test_full_pipeline.py`):
  ```python
  import pytest
  from tests.fixtures import sample_pdf_path
  
  @pytest.mark.e2e
  async def test_full_pipeline(sample_pdf_path):
      # 1. Upload document
      response = await client.post("/api/v1/documents/upload", files={"file": sample_pdf_path})
      assert response.status_code == 200
      document_id = response.json()["document_id"]
      
      # 2. Wait for extraction
      extraction = await wait_for_extraction(document_id)
      assert extraction["status"] == "completed"
      assert len(extraction["obligations"]) > 0
      
      # 3. Wait for validation
      validation = await wait_for_validation(extraction["obligation_ids"])
      assert validation["gold_count"] > 0
      
      # 4. Wait for crosswalk
      crosswalk = await wait_for_crosswalk(document_id)
      assert crosswalk["mapped_count"] > 0
      
      # 5. Generate OSCAL
      oscal = await generate_oscal_export("nist-csf")
      assert validate_oscal_schema(oscal)
  ```
- Use pytest fixtures for sample documents stored in `/tests/fixtures/sample_pdfs/`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] All acceptance criteria verified
- [x] CI pipeline configured
- [x] Documentation updated

#### Dependencies
- Blocked by: INFRA-1, TEST-1
- Blocks: TEST-3

---

### TEST-3: Adversarial Tests and Accuracy Benchmarks

**Type**: Story  
**Sprint**: Sprint 10  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: QA Engineer  
**Labels**: testing, adversarial, benchmark  

#### User Story
> As a **QA engineer**, I want adversarial tests and accuracy benchmarks, so that I can verify the system meets the > 90% mapping accuracy requirement.

#### Context and Background
Per TRD Section 14, accuracy benchmarks must:
- Hold-out validation set of 1000 manually annotated control-obligation pairs
- Measure: mapping classification accuracy, extraction precision, dual-judge agreement
- Run daily and report trends
- Adversarial tests: test edge cases (ambiguous text, contradictory clauses)

#### Acceptance Criteria
1. Given the validation set exists, when accuracy benchmarks are run, then mapping classification accuracy is calculated
2. Given accuracy is calculated, when it is < 90%, then an alert is sent to the ML team
3. Extraction precision is measured against ground truth: > 80% preferred rate required
4. Dual-judge agreement rate is tracked: Logic Judge > 95%, Technical Judge = 100%
5. Adversarial tests include: ambiguous clauses, contradictory requirements, complex nested structures
6. Benchmark results are stored in PostgreSQL and visualized in Grafana

#### Technical Notes
- Validation dataset structure (in `/tests/fixtures/validation_pairs.json`):
  ```json
  [
    {
      "control_id": "control-123",
      "obligation_id": "obl-456",
      "true_relationship": "SUPERSET_OF",
      "control_text": "The system shall...",
      "obligation_text": "The organization must..."
    }
  ]
  ```
- Benchmark calculation:
  ```python
  def calculate_accuracy(predictions, ground_truth):
      correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
      return correct / len(ground_truth)
  ```
- Grafana dashboard: `docs/01-initial/grafana_dashboards/accuracy_dashboard.json`

#### Definition of Done
- [x] Code written and peer-reviewed
- [x] All acceptance criteria verified
- [x] Benchmark pipeline configured
- [x] Documentation updated

#### Dependencies
- Blocked by: TEST-2
- Blocks: None

---

### SPIKE-1: MinerU Model Availability Validation

**Type**: Spike  
**Sprint**: Sprint 0  
**Story Points**: 3  
**Priority**: High  
**Assigned To**: ML/AI Engineer  
**Labels**: spike, research, pdf-parsing  

#### User Story
> As a **ML engineer**, I want to validate MinerU model availability for local deployment, so that the document ingestion pipeline can proceed with a confirmed parsing approach.

#### Context and Background
**SPIKE-1** is a time-boxed investigation to validate whether the MinerU PDF parsing model can be downloaded, installed, and run locally. If MinerU is unavailable or impractical, the spike must evaluate alternative parsers (Marker, pdfplumber, etc.) and recommend a fallback.

This spike must complete before Sprint 2 can begin, as INGEST-2 (MinerU PDF-to-Markdown Conversion) depends on this decision.

#### Investigation Questions
1. Can MinerU models be downloaded via pip/huggingface without external dependencies?
2. What are the GPU requirements for MinerU inference?
3. Are there licensing restrictions for MinerU models?
4. What is the fallback if MinerU fails (Marker confidence < 0.85)?
5. Can MinerU run on CPU for development environments?

#### Deliverables
1. **Decision Document** (`docs/01-initial/mineru-validation.md`) containing:
   - MinerU download/install instructions (or rejection with rationale)
   - Alternative parser recommendation (if MinerU not viable)
   - GPU requirements for production
   - CPU fallback option for development
2. **Proof of Concept** (working script that parses a sample PDF):
   - If MinerU is chosen: `/scripts/poc_mineru.py`
   - If Marker is chosen: `/scripts/poc_marker.py`
   - If alternative is chosen: `/scripts/poc_<parser>.py`
3. **Integration Recommendation**: How the chosen parser integrates with INGEST-2

#### Acceptance Criteria
1. Given the spike is complete, when the decision document is reviewed, then it contains a clear recommendation (MinerU or alternative) with supporting evidence
2. Given the POC is executed, when a sample PDF is passed through the parser, then valid Markdown output is produced
3. Given the decision is "MinerU", when `pip install mineru` is executed, then the installation completes without external API dependencies
4. Given the decision is "Marker", when `pip install marker-pdf` is executed, then the installation completes without external API dependencies
5. Given the spike output, the team can proceed to Sprint 2 without blockers

#### Timebox
**4 hours maximum**. If the investigation requires more time to complete, the spike extends by 4 hours with team consensus.

#### Definition of Done
- [x] Decision document written and peer-reviewed
- [x] POC script produced (working code)
- [x] Recommendation presented to team
- [x] Sprint 0 sign-off from Scrum Master

#### Dependencies
- Blocked by: None (can run in parallel with INFRA-1)
- Blocks: INGEST-2

---

# Sprint Plan Summary

## Backlog Health Check

| Metric | Count |
|---|---|
| **Total Sprints** | 10 |
| **Total Stories** | 51 |
| **Total Story Points** | ~308 |
| **Estimated Duration** | 20 weeks (10 sprints) |
| **Risk Stories (Spikes Needed)** | 1 (see Spike Recommendations below) |

## Sprint Distribution

| Sprint | Focus | Stories | Points |
|---|---|---|---|
| **Sprint 0** | **Spike: MinerU Validation** | **SPIKE-1** | **3** |
| Sprint 1 | Infrastructure Foundation | INFRA-1 through INFRA-9 | 41 |
| Sprint 2 | Document Ingestion Pipeline | INGEST-1 through INGEST-5 | 34 |
| Sprint 3 | De Jure Extraction + Observability | EXTRACT-1 through EXTRACT-5, OBSERV-1, DLQ-METRICS-1, GOLDEN50-1 | 52 |
| Sprint 4 | Dual-Judge Validation Backend | DUALJUDGE-1 through DUALJUDGE-4 | 29 |
| Sprint 5 | ColBERT Crosswalk | CROSSWALK-1 through CROSSWALK-4 | 35 |
| Sprint 6 | HITL UI + Accuracy Benchmarks | COVERAGE-1 through COVERAGE-3, HITL-1, HITL-2, TEST-3 | 40 |
| Sprint 7 | GraphRAG Query | GRAG-1 through GRAG-4 | 26 |
| Sprint 8 | OSCAL Export | OSCAL-1 through OSCAL-3 | 22 |
| Sprint 9 | Observability (System Health) | OBSERV-2, OBSERV-3 | 12 |
| Sprint 10 | E2E Testing | TEST-1, TEST-2 | 16 |

## Spike Recommendations

| Spike ID | Topic | Reason | Suggested Outcome |
|---|---|---|---|
| SPIKE-2 | ColBERT Performance on CPU | ColBERT inference may be slow without GPU | POC: Measure inference latency, determine if GPU is required for production |
| SPIKE-3 | Temporal + Kafka Integration | Ensuring Temporal workflows properly consume Kafka events | Decision document with integration pattern and error handling strategy |

## Risks to Delivery

| Risk | Impact | Mitigation |
|---|---|---|
| **LLM Model Availability** | Critical - Core AI functionality depends on local LLM models | SPIKE-1 completed in Sprint 0; maintain fallback prompts for smaller models |
| **GPU Requirements** | High - ColBERT and dual-judge may require significant GPU resources | SPIKE-2 to quantify requirements; plan for GPU worker pool in production (Sprint 8+) |
| **HITL UI Development** | High - No UI means no callback path for Temporal workflows | HITL-1 and HITL-2 added to Sprint 4; ensure frontend resource allocation |
| **Data Quality** | Medium - Extraction quality depends on clean regulatory PDFs | Start with curated sample documents; implement iterative repair loop (Sprint 3) |
| **Team Ramp-up** | Low - New team members may need time to learn the stack | Start with Sprint 1-2 infrastructure work; pair programming on complex stories |

---

**Document Version:** 1.1  
**Created:** 2026-04-13  
**Last Updated:** 2026-04-13 (CTO Review Revision 1)  
**Linked TRD:** `docs/01-initial/master_tech_req.md` v6.0  
**Linked BRD:** `docs/01-initial/business-requirement.md` v2.0  
**Linked PRD:** `docs/01-initial/product-requirement.md` v2.0

---

*RCKG Platform · Sprint Plan v1.1 · 2026-04-13 · CONFIDENTIAL — INTERNAL USE ONLY*
