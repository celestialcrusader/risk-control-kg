"""
Redis cache layer for RCKG.

Provides connection pooling, cache operations with TTL support, and
rate limiting via Redis INCR. All keys use the 'rckg:' prefix by default.

Per TRD Section 4.2:
- Query result caching (TTL 300 seconds)
- Rate-limit counters
- Session state for multi-step agent tasks
"""

import logging
import os

import redis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)

DEFAULT_KEY_PREFIX = "rckg"
DEFAULT_RATE_LIMIT_WINDOW = 300  # 5 minutes
REDIS_DEFAULTS = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "password": os.getenv("REDIS_PASSWORD", "rckg_secret_password"),
    "db": int(os.getenv("REDIS_DB", "0")),
    "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
}


class RedisCacheClient:
    """Redis client with connection pooling and key prefixing."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        password: str | None = None,
        db: int | None = None,
        max_connections: int | None = None,
        key_prefix: str = DEFAULT_KEY_PREFIX,
    ):
        self.host = host or REDIS_DEFAULTS["host"]
        self.port = port or REDIS_DEFAULTS["port"]
        self.password = password or REDIS_DEFAULTS["password"]
        self.db = db if db is not None else REDIS_DEFAULTS["db"]
        self.max_connections = max_connections or REDIS_DEFAULTS["max_connections"]
        self.key_prefix = key_prefix

        self.pool = self.create_pool(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            max_connections=self.max_connections,
        )
        self._client = redis.Redis(connection_pool=self.pool)

        # Verify connectivity
        try:
            self._client.ping()
        except redis.ConnectionError as e:
            logger.warning("Redis connection failed at init: %s", e)

    @staticmethod
    def create_pool(host: str, port: int, password: str, db: int, max_connections: int) -> ConnectionPool:
        """Create a Redis connection pool."""
        return ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=db,
            max_connections=max_connections,
            decode_responses=False,
        )

    def _key(self, key: str) -> str:
        """Prepend the key prefix."""
        if key.startswith(f"{self.key_prefix}:"):
            return key
        return f"{self.key_prefix}:{key}"

    def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Store a key-value pair with optional TTL (seconds)."""
        try:
            full_key = self._key(key)
            if ttl is not None:
                result = self._client.setex(full_key, ttl, value)
            else:
                result = self._client.set(full_key, value)
            return bool(result)
        except redis.RedisError as e:
            logger.error("Redis SET failed for key '%s': %s", key, e)
            raise
        except Exception as e:
            logger.error("Unexpected error on SET for key '%s': %s", key, e)
            raise

    def get(self, key: str) -> str | None:
        """Retrieve a value from cache. Returns None on miss or error."""
        try:
            full_key = self._key(key)
            value = self._client.get(full_key)
            if value is None:
                return None
            return value.decode("utf-8")
        except redis.RedisError:
            logger.error("Redis GET failed for key '%s'", key)
            return None
        except Exception:
            logger.error("Unexpected error on GET for key '%s'", key)
            return None

    def delete(self, key: str) -> int:
        """Delete a key from cache. Returns number of keys deleted."""
        try:
            full_key = self._key(key)
            return self._client.delete(full_key)
        except redis.RedisError:
            logger.error("Redis DELETE failed for key '%s'", key)
            return 0
        except Exception:
            logger.error("Unexpected error on DELETE for key '%s'", key)
            return 0

    def get_or_default(self, key: str, default: str) -> str:
        """Return cached value or default on miss/error."""
        value = self.get(key)
        if value is not None:
            return value
        return default

    # ---- Rate limiting via INCR ----

    def rate_limit_increment(self, endpoint: str, user_id: str, window: int = DEFAULT_RATE_LIMIT_WINDOW) -> int:
        """Increment a rate limit counter. Returns current count or 0 on failure."""
        try:
            key = f"rate_limit:{endpoint}:{user_id}"
            full_key = self._key(key)
            count = self._client.incr(full_key)
            if count == 1:
                self._client.expire(full_key, window)
            return count
        except redis.RedisError:
            logger.error("Rate limit INCR failed for '%s'", key)
            return 0
        except Exception:
            logger.error("Unexpected error on rate limit INCR for '%s'", key)
            return 0

    def rate_limit_check(
        self, endpoint: str, user_id: str, max_requests: int, window: int = DEFAULT_RATE_LIMIT_WINDOW
    ) -> bool:
        """Check if request is allowed under rate limit. Defaults to allowed on failure."""
        try:
            count = self.rate_limit_increment(endpoint, user_id, window)
            return count <= max_requests
        except redis.RedisError:
            logger.error("Rate limit check failed for '%s:%s'", endpoint, user_id)
            return True  # fail open
        except Exception:
            logger.error("Unexpected error on rate limit check for '%s:%s'", endpoint, user_id)
            return True  # fail open

    def rate_limit_reset(self, endpoint: str, user_id: str) -> int:
        """Reset a rate limit counter."""
        key = f"rate_limit:{endpoint}:{user_id}"
        try:
            full_key = self._key(key)
            return self._client.delete(full_key)
        except redis.RedisError:
            logger.error("Rate limit reset failed for '%s'", key)
            return 0
        except Exception:
            logger.error("Unexpected error on rate limit reset for '%s'", key)
            return 0

    def is_alive(self) -> bool:
        """Health check: True if Redis responds to PING."""
        try:
            return bool(self._client.ping())
        except Exception:
            return False
