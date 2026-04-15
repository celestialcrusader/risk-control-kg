# RCKG Infrastructure Tests

This directory contains integration tests for the RCKG infrastructure stack.

## Running Tests

### Prerequisites

- Docker and Docker Compose installed and running
- Minimum 128GB RAM recommended (for full stack)
- At least 500GB free disk space

### Test Commands

```bash
# Run all infrastructure tests
pytest infra/tests/ -v

# Run only INFRA-1 tests
pytest infra/tests/test_infra_1_docker_compose.py -v

# Run integration tests only
pytest infra/tests/ -m integration

# Run with coverage
pytest infra/tests/ --cov=infra --cov-report=html

# Run specific test
pytest infra/tests/test_infra_1_docker_compose.py::TestDockerComposeStack::test_all_services_start -v
```

### Test Categories

| Test Class | Tests | Description |
|------------|-------|-------------|
| `TestDockerComposeStack` | 17 | Core infrastructure service health checks |
| `TestComposeCommands` | 2 | docker-compose command documentation tests |

## Test Coverage

### INFRA-1 Acceptance Criteria Coverage

| AC | Test | Status |
|----|------|--------|
| AC-1: All services start within 5 min | `test_all_services_start` | ✅ |
| AC-2: All containers healthy/running | `test_all_services_start` | ✅ |
| AC-3: PostgreSQL health check | `test_postgres_health`, `test_postgres_sql_query` | ✅ |
| AC-4: Memgraph REST API | `test_memgraph_status` | ✅ |
| AC-5: Qdrant version endpoint | `test_qdrant_version` | ✅ |
| AC-6: Documentation exists | `setup-guide.md` | ✅ |

### Additional Tests Added

| Test | Description | Why Added |
|------|-------------|-----------|
| `test_minio_buckets_created` | Verifies 4 MinIO buckets exist | MinIO bucket initialization wasn't verified |
| `test_postgres_sql_query` | Executes actual SQL query | pg_isready only checks TCP, not SQL |
| `test_temporal_namespace_exists` | Verifies rckg-production namespace | Temporal namespace creation wasn't verified |
| `test_services_can_reach_each_other_via_hostname` | Tests inter-service DNS resolution | Verifies Docker network configuration |
| `test_network_rckg_net_exists` | Verifies rckg-net network exists | Network isolation wasn't tested |

## Test Fixtures

### `compose_up`

- Starts the entire Docker Compose stack
- Waits up to 300 seconds for all services to start
- Tears down all containers and volumes after tests complete
- Scope: class (all tests in a class share one stack)

### `compose_running`

- Ensures the Docker Compose stack is running
- Does NOT tear down after tests
- Used by tests that need the stack to persist

## Test Markers

```python
@pytest.mark.integration  # Requires Docker daemon
@pytest.mark.unit         # Isolated tests (not used in INFRA-1)
@pytest.mark.slow         # Tests > 10 seconds
```

## Troubleshooting

### Test Times Out Waiting for Services

```bash
# Check service health manually
docker compose ps

# Check service logs
docker compose logs postgres
docker compose logs memgraph
```

### Docker Compose Not Starting Services

```bash
# Verify docker-compose.yml is valid
docker compose config

# Check available system resources
free -h
df -h
```

### MinIO Buckets Not Created

```bash
# Check minio-init logs
docker compose logs minio-init

# Manually create buckets
docker compose exec minio-init mc config host add rckg http://minio:9000 rckg_admin rckg_secret_password
docker compose exec minio-init mc mb rckg/source-regulations
```

### PostgreSQL SQL Query Fails

```bash
# Check PostgreSQL is ready
docker compose exec postgres pg_isready

# Check PostgreSQL logs
docker compose logs postgres
```

## Test Configuration

See `pytest.ini` for pytest configuration options.
