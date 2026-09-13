# RCKG Infrastructure Directory

This directory contains infrastructure-related files for the RCKG platform.

## Structure

```
infra/
├── postgres/
│   └── init.sql              # PostgreSQL schema initialization script
├── temporal/
│   └── dynamicconfig/
│       └── development.yaml  # Temporal dynamic configuration
└── tests/
    ├── test_infra_1_docker_compose.py
    ├── pytest.ini
    └── README.md
```

## Components

### PostgreSQL

- **Purpose**: Cold store for archival data + Temporal backend
- **Port**: 5432
- **Init Script**: `infra/postgres/init.sql`
- **Schema**: Bronze/Silver/Gold three-layer vault with bitemporal support

### Memgraph

- **Purpose**: Hot graph database for active compliance data
- **Ports**: 7687 (Bolt), 7688 (HTTP)
- **Data Directory**: `/opt/memgraph/storage`

### Qdrant

- **Purpose**: Vector database for embeddings
- **Port**: 6333
- **Storage**: `/qdrant/storage`

### MinIO

- **Purpose**: S3-compatible object storage
- **Ports**: 9000 (API), 9001 (Console)
- **Buckets**:
  - `source-regulations` (WORM policy)
  - `minio-data` (temporary/unstructured)
  - `markdown-conversions`
  - `evidence-artifacts`

### Redis

- **Purpose**: Cache layer and rate limiting
- **Port**: 6379
- **Max Memory**: 8GB with LRU eviction

### Temporal

- **Purpose**: Workflow orchestration
- **Ports**: 7233 (gRPC), 8233 (Web UI)
- **Backend**: PostgreSQL

### Langfuse

- **Purpose**: Observability and AI tracing
- **Port**: 3000

### Kafka

- **Purpose**: Event bus for async workflows
- **Ports**: 9092 (broker), 2181 (Zookeeper)
- **Topics**: `document.ingested`, `extraction.completed`, `validation.completed`, `mapping.completed`, `coverage.alert`

## Running Tests

```bash
# Run all tests
cd .
pytest infra/tests/

# Run integration tests only
pytest infra/tests/ -m integration

# Run with coverage
pytest infra/tests/ --cov=infra
```

## See Also

- [Setup Guide](../docs/01-initial/setup-guide.md) - Complete setup instructions
- [docker-compose.yml](../docker-compose.yml) - Full service definitions
