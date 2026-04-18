# INFRA-5: Redis Cache Layer Setup

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 3
**Priority**: Medium
**Assigned To**: Backend Engineer
**Labels**: infrastructure, cache, redis

---

## User Story

> As a **backend developer**, I want Redis cache configured with appropriate TTL and eviction policies, so that frequent query results can be cached and rate limiting can be enforced.

---

## Context and Background

Per TRD Section 4.2, Redis is used for:
- Query result caching (TTL 300 seconds)
- Rate-limit counters
- Session state for multi-step agent tasks

This story follows INFRA-1 (Docker Compose) which brings up the Redis container. The actual cache layer code and configuration must be implemented in this story. Without caching, every query hits the database directly, defeating the purpose of the layered architecture. Without rate limiting, the system is vulnerable to abuse.

---

## Acceptance Criteria

1. Given Redis is running, when a key is set with `SET key value EX 300`, then the key expires after 300 seconds
2. Given rate limit data is stored, when `INCR rate_limit:api:key` is executed, then the counter increments correctly
3. Given Redis memory is full, when a new key is set with `allkeys-lru` eviction policy, then the least recently used key is evicted
4. Redis is accessible at `localhost:6379` with documented password
5. `/backend/app/core/cache.py` includes Redis client initialization with connection pool
6. Given an application request, when the cache layer is invoked, then cache hits return data within 10ms and cache misses fall through to the underlying data source
7. Given a rate limit key reaches its threshold, when a new request is made, then the API returns HTTP 429 with `Retry-After` header

---

## Technical Notes

- Redis configuration: `--maxmemory 8gb --maxmemory-policy allkeys-lru`
- Use Redis connection pooling (max 50 connections)
- Cache key prefix: `rckg:` for all keys
- Rate limit keys format: `rckg:rate_limit:{endpoint}:{user_id}`
- Connection pool configuration in `cache.py`:
  ```python
  redis_pool = aioredis.ConnectionPool.from_url(
      "redis://:password@localhost:6379/0",
      max_connections=50,
      decode_responses=False,
  )
  ```
- For rate limiting, use a token bucket or sliding window approach via Lua scripts
- Consider using `aioredis` for async support with FastAPI
- Cache invalidation strategy: delete keys on write operations (write-through with invalidation)
- Health check endpoint: `GET /api/v1/health/cache` returns Redis ping result

### Edge Cases
- Handle Redis connection failures gracefully: fall back to calling the underlying data source directly and log a warning
- Handle `ConnectionError`, `TimeoutError`, and `AuthenticationError` exceptions
- Implement circuit breaker pattern if Redis is consistently unreachable (after 3 consecutive failures, open circuit for 30 seconds)

---

## Definition of Done

- [ ] Code written and peer-reviewed (PR approved by at least 1 reviewer)
- [ ] Unit tests for cache operations (set, get, delete, TTL)
- [ ] Unit tests for rate limiting (increment, check threshold, reset)
- [ ] Integration tests with running Redis container
- [ ] All acceptance criteria verified by the developer
- [ ] Code merged to the main/development branch
- [ ] No new linting errors or warnings introduced
- [ ] Relevant documentation updated (API docs, README, inline comments)
- [ ] Story demoed or verified by Product Owner / Scrum Master
- [ ] **QA Checkpoint**: Verify all assertions are meaningful (not `or True`, not `is not None` alone). Check that test assertions verify actual behavior, not just absence of errors. See ARTIFACTS/qa_review_comments.md for recurring "weak assertion" patterns.

---

## Dependencies

- Blocked by: INFRA-1 (Docker Compose brings up Redis)
- Blocks: None
