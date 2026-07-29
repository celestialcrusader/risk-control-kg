# GRAG-4: Query API and Response Caching

**Type**: Story
**Sprint**: Sprint 7
**Story Points**: 3
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, api, cache

---

## User Story

> As a **compliance officer**, I want a REST API for GraphRAG queries with response caching, so that I can quickly query the system and repeated queries are served from cache.

---

## Context and Background

Per TRD Section 4.2, the query API must:
- Expose `POST /api/v1/query` endpoint
- Accept query text and optional `as_of_date` parameter
- Cache responses in Redis with TTL 300 seconds
- Include rate limiting (max 10 queries/minute per user)

---

## Acceptance Criteria

1. Given a valid query is submitted via `POST /api/v1/query`, then the response is returned in < 5 seconds
2. Given the same query is submitted twice within 300 seconds, when the second request is made, then the cached result is returned in < 100ms
3. Given a user exceeds 10 queries/minute, when the rate limit is breached, then HTTP 429 is returned with `{"error": "Rate limit exceeded"}`
4. Query response includes: `answer`, `citations[]`, `query_time_ms`, `context_size_tokens`
5. Query logs are written to PostgreSQL `query_logs` table for audit trail
6. Rate limiting uses Redis with key format: `rckg:rate_limit:{user_id}:{minute_window}`

---

## Technical Notes

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
- Query logging table:
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

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for API endpoint
- [ ] Integration tests for caching and rate limiting
- [ ] All acceptance criteria verified
- [ ] OpenAPI documentation generated

---

## Dependencies

- **Blocked by**: GRAG-3
- **Blocks**: None
