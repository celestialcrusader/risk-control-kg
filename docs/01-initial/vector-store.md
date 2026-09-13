# INFRA-4: Qdrant Vector Database Configuration

This document describes the Qdrant vector database configuration for the RCKG platform.

## Overview

Qdrant is a vector similarity search engine used for:
- Storing BGE-M3 dense embeddings (1024-dimensional)
- Storing ColBERTv2.0 token-level embeddings (quantized)
- Semantic search over regulatory documents
- Retrieval-augmented generation (RAG) pipelines

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Qdrant Vector Database                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              document_chunks Collection               │   │
│  │                                                       │   │
│  │  Vector Config:                                       │   │
│  │  - Size: 1024 (BGE-M3)                                │   │
│  │  - Distance: Cosine                                   │   │
│  │  - HNSW Index: m=16, ef_construct=100                 │   │
│  │                                                       │   │
│  │  Payload Fields:                                      │   │
│  │  - document_id: string (filtered)                     │   │
│  │  - section: string                                    │   │
│  │  - text: string (display)                             │   │
│  │  - metadata: JSONB (file_name, page_number, etc.)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Collection Configuration

### document_chunks

| Property | Value |
|----------|-------|
| **Purpose** | Store document embedding chunks for semantic search |
| **Vector Size** | 1024 (BGE-M3) |
| **Distance Metric** | Cosine similarity |
| **HNSW Index** | m=16, ef_construct=100 |
| **Quantization** | Optional SQ8 for ColBERT |

### Payload Indexes

| Field | Type | Indexed | Purpose |
|-------|------|---------|---------|
| `document_id` | string | Yes | Filter by document |
| `section` | string | No | Hierarchy navigation |
| `text` | string | No | Display preview |
| `metadata` | JSONB | No | File metadata |

## Access Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant API port |
| `QDRANT_COLLECTION_NAME` | `document_chunks` | Collection name |
| `QDRANT_VECTOR_SIZE` | `1024` | Vector dimension size |

### API Endpoints

| Service | URL | Authentication |
|---------|-----|----------------|
| **gRPC API** | `http://localhost:6333` | None (local) |
| **REST API** | `http://localhost:6333` | None (local) |
| **Dashboard** | `http://localhost:6333` | None (local) |

### Dashboard Access

1. Navigate to `http://localhost:6333`
2. View collections, upload vectors, perform searches

## Collection Creation Script

### Using Python Client

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import VectorParams, Distance, HnswConfigDiff

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection with HNSW indexing and cosine distance
client.create_collection(
    collection_name="document_chunks",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
)

# Create payload index on document_id for fast filtering
client.create_payload_index(
    collection_name="document_chunks",
    field_name="document_id",
    field_schema="keyword",
)
```

### Using Docker Compose

Qdrant is already configured in `docker-compose.yml`:

```yaml
qdrant:
  image: qdrant/qdrant:latest
  container_name: rckg-qdrant
  ports:
    - "6333:6333"
  volumes:
    - qdrant_storage:/qdrant/storage  # Named volume for persistence
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:6333"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s
  mem_limit: 16G
```

## Python SDK Usage

### Basic Usage

```python
from backend.app.storage.qdrant import get_qdrant_vector_store, EmbeddingChunk

# Get vector store instance
vector_store = get_qdrant_vector_store()

# Create embedding chunk
chunk = EmbeddingChunk(
    id="chunk-001",
    vector=[0.1] * 1024,  # 1024-dimensional BGE-M3 embedding
    document_id="doc-123",
    section="section-4.2",
    text="This is the regulatory requirement text...",
    metadata={
        "file_name": "dora-regulation.pdf",
        "page_number": 42,
        "embedding_model": "BGE-M3",
    },
)

# Upload single embedding
vector_store.upload_embedding(chunk)

# Upload multiple embeddings
chunks = [
    EmbeddingChunk(id=f"chunk-{i}", vector=[0.1]*1024, ...)
    for i in range(100)
]
vector_store.upload_embeddings(chunks)
```

### Semantic Search

```python
# Search with top-K results
query_vector = [0.5] * 1024  # Embedding of query text
results = vector_store.search(
    query_vector=query_vector,
    top_k=10,
)

# Results format:
# [
#     {"id": "chunk-001", "score": 0.95, "payload": {...}},
#     {"id": "chunk-042", "score": 0.87, "payload": {...}},
#     ...
# ]
```

### Search with Payload Filters

```python
# Filter by document_id
results = vector_store.search(
    query_vector=query_vector,
    top_k=10,
    filter_by={"document_id": "doc-123"},
)

# Only chunks from doc-123 will be returned
```

### Get Chunk by ID

```python
# Get single chunk
chunk = vector_store.get("chunk-001")

# Get multiple chunks
chunks = vector_store.get(["chunk-001", "chunk-002", "chunk-003"])
```

### Collection Info

```python
# Get collection statistics
info = vector_store.get_collection_info()
print(f"Vector size: {info['vector_size']}")
print(f"Distance: {info['distance']}")
print(f"Point count: {info['point_count']}")
```

## Performance Characteristics

### Search Performance

- **< 500ms** for top-K=10 search with 100,000 vectors (HNSW indexed)
- **< 100ms** for top-K=10 search with 1,000 vectors
- Performance scales logarithmically with vector count due to HNSW indexing

### Memory Requirements

- **16GB** recommended for production with 1M+ vectors
- **4GB** minimum for development with 10,000 vectors

## HNSW Configuration

The HNSW (Hierarchical Navigable Small World) index configuration:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `m` | 16 | Number of connections per node (higher = better accuracy, more memory) |
| `ef_construct` | 100 | Construction parameter (higher = better index quality) |
| `ef_search` | Runtime parameter (default: 128) | Search parameter (higher = better accuracy, slower) |

### Tuning Recommendations

For better search accuracy:
```python
client.update_collection(
    collection_name="document_chunks",
    hnsw_config=models.HnswConfigDiff(
        ef_search=200,  # Increase for better accuracy
    ),
)
```

## Security Considerations

### Production Deployment

1. **Enable authentication**: Configure API key authentication
2. **Use TLS**: Enable HTTPS for all connections
3. **Network isolation**: Restrict access to internal networks
4. **Backup strategy**: Regular snapshots of `/qdrant/storage`

### API Key Authentication

```bash
# Start Qdrant with authentication
docker run -d \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  -e QDRANT__SERVICE__API_KEY="your-secret-api-key" \
  qdrant/qdrant:latest
```

## Testing

### Run Integration Tests

```bash
cd ./backend
pytest tests/test_infra_4_qdrant_vector_db.py -v
```

### Manual Verification

```bash
# Check Qdrant is running
curl http://localhost:6333

# Create collection via CLI
python -c "
from qdrant_client import QdrantClient
client = QdrantClient('localhost', 6333)
print(client.get_collections())
"
```

## See Also

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [TRD Section 4.3: Vector Database](./master_tech_req.md)
- [Docker Compose Configuration](../../docker-compose.yml)
- [INFRA-2: PostgreSQL Schema](./postgres-schema.md)
