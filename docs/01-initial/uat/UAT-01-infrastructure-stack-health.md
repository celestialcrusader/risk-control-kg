# UAT-01: Infrastructure Stack Health Check

**Covers**: INFRA-1, INFRA-2, INFRA-3, INFRA-4, INFRA-5, INFRA-6, INFRA-7, INFRA-8, INFRA-9
**Type**: Infrastructure Smoke Test
**Effort**: ~5 minutes

## Objective

Verify that all 9 infrastructure services start, connect, and report healthy status after a `docker-compose up -d`.

## Steps

### Step 1: Start the Stack

```bash
cd .
docker-compose up -d
```

### Step 2: Wait for Services to Be Healthy

```bash
sleep 180  # Wait ~3 minutes for all services to initialize
```

### Step 3: Verify All Containers Are Running

```bash
docker-compose ps
```

### Step 4: Check Individual Service Health Endpoints

```bash
# PostgreSQL (INFRA-2)
PG_PID=$(docker exec $(docker-compose ps -q postgres) pg_isready 2>&1)
echo "PostgreSQL: $PG_PID"

# MinIO (INFRA-3)
MINIO_RESP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/minio/health/live)
echo "MinIO: $MINIO_RESP"

# Qdrant (INFRA-4)
QDRANT_RESP=$(curl -s http://localhost:6333/health | head -1)
echo "Qdrant: $QDRANT_RESP"

# Memgraph (INFRA-9)
MEMGRAPH_RESP=$(curl -s http://localhost:7444/version | head -1)
echo "Memgraph: $MEMGRAPH_RESP"

# Redis (INFRA-5)
REDIS_PING=$(docker exec $(docker-compose ps -q redis) redis-cli ping 2>/dev/null || redis-cli ping)
echo "Redis: $REDIS_PING"

# Temporal (INFRA-6)
TEMPORAL_NS=$(tctl namespace list 2>/dev/null || echo "tctl not available, skip")
echo "Temporal: $TEMPORAL_NS"

# Kafka (INFRA-7)
KAFKA_TOPIC=$(docker exec $(docker-compose ps -q kafka) kafka-topics.sh --list --bootstrap-server localhost:9092 2>/dev/null | head -5 || echo "kafka not available, skip")
echo "Kafka topics: $KAFKA_TOPIC"
```

### Step 5: Verify Database Schema

```bash
# Check that the three-layer vault tables exist
docker exec -it $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('public', 'bronze', 'silver', 'gold')
ORDER BY table_schema, table_name;
"
```

### Step 6: Verify Qdrant Collection

```bash
curl http://localhost:6333/collections/document_chunks | python3 -m json.tool
```

### Step 7: Verify Memgraph Schema

```bash
curl http://localhost:8000/api/v1/graph/health | python3 -m json.tool
```

## Expected Results

| # | Check | Expected |
|---|-------|----------|
| 1 | `docker-compose ps` output | All containers show `healthy` or `running` |
| 2 | PostgreSQL health (`pg_isready`) | `accepting connections on port 5432` |
| 3 | MinIO health endpoint | HTTP 200 |
| 4 | Qdrant health endpoint | HTTP 200 with version info |
| 5 | Memgraph version endpoint | HTTP 200 with version JSON |
| 6 | Redis ping | `PONG` |
| 7 | Temporal namespace list | Shows `rckg-production` namespace |
| 8 | Kafka topics list | Shows default topics (at minimum: `document.ingested`, `dlq`) |
| 9 | Database tables | `staging_controls` (Bronze), `semantic_controls` (Silver), `golden_controls` (Gold), `audit_log` all exist |
| 10 | Qdrant collection | `document_chunks` collection with HNSW config, cosine distance |
| 11 | Memgraph schema health | Returns schema report with node labels, indexes, SHACL loaded status |

## Verification

- [ ] All 9 infrastructure services are running and healthy
- [ ] PostgreSQL has all 4 required tables
- [ ] Qdrant has the `document_chunks` collection configured correctly
- [ ] Redis responds to PING with PONG
- [ ] Temporal shows the `rckg-production` namespace
- [ ] Kafka is accepting connections and listing topics
- [ ] MinIO health endpoint returns HTTP 200
- [ ] Memgraph schema health returns valid report

## Pass/Fail Criteria

- **PASS**: All 11 checks above return expected results
- **FAIL**: Any single check does not match expected result — note the specific failure and report

## Rollback

If services fail to start:
```bash
docker-compose down -v
docker-compose up -d
docker logs $(docker-compose ps -q <service-name>)
```
