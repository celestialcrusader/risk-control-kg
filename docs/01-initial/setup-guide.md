# RCKG Platform Setup Guide

This guide provides step-by-step instructions for setting up the RCKG development environment using Docker Compose.

## Prerequisites

- **Docker**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later (bundled with Docker Desktop)
- **Memory**: Minimum 128GB RAM recommended (64GB for PostgreSQL, 32GB for Memgraph, 16GB for Qdrant)
- **Storage**: Minimum 500GB free disk space for volumes

## Quick Start

### 1. Clone and Navigate to Project Directory

```bash
cd /home/zackchow/coding/rckg
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env to customize configuration (optional)
# Key variables to review:
# - POSTGRES_PASSWORD (change for production)
# - MINIO_ROOT_PASSWORD (change for production)
# - REDIS_PASSWORD (change for production)
```

### 3. Start the Infrastructure Stack

```bash
# Start all services in detached mode
docker compose up -d

# Expected services:
# - postgres (PostgreSQL 16)
# - memgraph (Graph database)
# - qdrant (Vector database)
# - minio (S3-compatible storage)
# - redis (Cache layer)
# - temporal (Workflow orchestration)
# - langfuse (Observability)
# - zookeeper (Kafka coordination)
# - kafka (Event bus)
```

### 4. Verify All Services Are Running

```bash
# Check service status
docker compose ps

# All services should show status "running" or "healthy"
```

### 5. Test Individual Services

```bash
# PostgreSQL
docker compose exec postgres pg_isready -U rckg -d rckg_db

# Memgraph
curl http://localhost:7688

# Qdrant
curl http://localhost:6333

# MinIO Health
curl http://localhost:9000/minio/health/live

# Redis
docker compose exec redis redis-cli -a rckg_secret_password ping

# Temporal
curl http://localhost:8233/api/v1/namespaces/rckg-production

# Langfuse
curl http://localhost:3000/api/health
```

## Accessing Web Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **MinIO Console** | http://localhost:9001 | rckg_admin / rckg_secret_password |
| **Memgraph Explorer** | http://localhost:7688 | rckg / rckg_secret_password |
| **Qdrant Dashboard** | http://localhost:6333 | No auth required |
| **Temporal Web UI** | http://localhost:8233 | No auth required |
| **Langfuse UI** | http://localhost:3000 | admin / admin (default) |

## Stopping the Stack

```bash
# Stop all services (keep volumes)
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v

# Remove all containers, networks, and images
docker compose down --rmi all -v
```

## Viewing Logs

```bash
# View all service logs
docker compose logs -f

# View logs for specific service
docker compose logs -f postgres
docker compose logs -f memgraph
docker compose logs -f kafka

# View logs from last 100 lines
docker compose logs --tail=100 postgres
```

## Common Issues

### PostgreSQL Connection Refused

```bash
# Wait for PostgreSQL to initialize (can take 30-60 seconds)
docker compose logs postgres

# Check PostgreSQL is ready
docker compose exec postgres pg_isready
```

### Memgraph Not Starting

```bash
# Check Memgraph logs
docker compose logs memgraph

# Ensure sufficient memory is available
# Memgraph requires 32GB mem_limit in docker-compose.yml
```

### MinIO Bucket Initialization Failed

```bash
# The minio-init service runs automatically after MinIO is healthy
# If it fails, manually initialize buckets:

docker compose exec minio-init mc config host add rckg http://minio:9000 rckg_admin rckg_secret_password
docker compose exec minio-init mc mb rckg/source-regulations
docker compose exec minio-init mc mb rckg/minio-data
docker compose exec minio-init mc mb rckg/markdown-conversions
docker compose exec minio-init mc mb rckg/evidence-artifacts
```

### Kafka Connection Issues

```bash
# Kafka requires Zookeeper to start first
docker compose logs zookeeper
docker compose logs kafka

# Verify Zookeeper is healthy
docker compose exec zookeeper echo ruok | nc localhost 2181
```

## Development Mode

For faster iteration during development, you can run services in foreground mode:

```bash
# Run all services in foreground (press Ctrl+C to stop)
docker compose up

# Run specific service in foreground
docker compose up postgres
```

## Environment-Specific Configurations

### Production Deployment

For production, you should:

1. Generate secure random passwords in `.env`:
```bash
# Generate secure passwords
openssl rand -base64 32 > POSTGRES_PASSWORD
openssl rand -base64 32 > MINIO_ROOT_PASSWORD
openssl rand -base64 32 > REDIS_PASSWORD
```

2. Use managed services instead of containers:
   - RDS Aurora for PostgreSQL
   - Managed Memgraph Cloud or Neo4j
   - Managed Qdrant Cloud or Elasticsearch
   - S3 for object storage

3. Enable TLS/SSL for all services

4. Configure proper network policies and firewall rules

## Next Steps

After verifying the infrastructure is running:

1. **INFRA-2**: Database schema migration will run automatically on first PostgreSQL startup
2. **INFRA-9**: Graph schema initialization (Memgraph)
3. **INGEST-1**: Document upload API development

## Troubleshooting Commands

```bash
# Check disk space usage by Docker
docker system df

# Clean up unused Docker resources
docker system prune -a

# Remove all volumes and start fresh
docker volume prune

# View all Docker logs
docker compose logs | grep -i error

# Restart specific service
docker compose restart postgres
```

## Resource Limits

The `docker-compose.yml` includes the following memory limits:

| Service | Memory Limit |
|---------|-------------|
| PostgreSQL | 64GB |
| Memgraph | 32GB |
| Qdrant | 16GB |
| Redis | 8GB |

Ensure your host machine has sufficient memory available. If you encounter OOM errors, reduce the limits or add more RAM.
