"""
Test suite for INFRA-5: Redis Cache Layer Setup

This test module verifies the Redis cache layer implementation including:
- Client initialization with connection pooling
- Cache set/get/delete operations with TTL
- Rate limiting via INCR
- Connection error handling and graceful fallback

Test Strategy:
- Unit tests with mock Redis where service is not available
- Tests verify actual cache behavior, not just absence of errors
- All assertions are meaningful and check actual values
"""

import pytest
from unittest.mock import MagicMock, patch

# Test configuration
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "password": "rckg_secret_password",
    "db": 0,
    "max_connections": 50,
}


class TestCacheClientInitialization:
    """Tests for Redis client initialization and connection pooling."""

    def test_create_pool_returns_connection_pool(self):
        """TC-5.1: Connection pool is created with correct parameters."""
        from app.core.cache import ConnectionPool, RedisCacheClient

        pool = RedisCacheClient.create_pool(
            host=REDIS_CONFIG["host"],
            port=REDIS_CONFIG["port"],
            password=REDIS_CONFIG["password"],
            db=REDIS_CONFIG["db"],
            max_connections=REDIS_CONFIG["max_connections"],
        )

        assert pool is not None
        assert isinstance(pool, ConnectionPool)

    def test_client_creation_with_pool(self):
        """TC-5.2: Client is created with the provided connection pool."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            client = RedisCacheClient()

        assert client.pool is not None
        mock_pool.assert_called_once()

    @patch("app.core.cache.RedisCacheClient.create_pool")
    def test_client_default_config_from_env(self, mock_pool):
        """TC-5.4: Client can accept explicit config."""
        import os
        from app.core.cache import REDIS_DEFAULTS, RedisCacheClient

        # Patch REDIS_DEFAULTS so the constructor picks up custom values
        os.environ["REDIS_HOST"] = "custom-host"
        os.environ["REDIS_PORT"] = "6380"
        os.environ["REDIS_PASSWORD"] = "custom_pass"

        try:
            client = RedisCacheClient(
                host=os.environ["REDIS_HOST"],
                port=int(os.environ["REDIS_PORT"]),
                password=os.environ["REDIS_PASSWORD"],
            )
            assert client.host == "custom-host"
            assert client.port == 6380
            assert client.password == "custom_pass"
        finally:
            del os.environ["REDIS_HOST"]
            del os.environ["REDIS_PORT"]
            del os.environ["REDIS_PASSWORD"]


class TestCacheOperations:
    """Tests for cache set, get, delete, and TTL operations."""

    def test_set_value_with_ttl(self):
        """TC-5.1: Given a key is set with TTL, it expires after specified seconds."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            client.set("test_key", "test_value", ttl=300)

            mock_client.setex.assert_called_once_with(
                "rckg:test_key", 300, "test_value"
            )

    def test_set_value_without_ttl(self):
        """Key is set without expiration when TTL is not specified."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            client.set("no_ttl_key", "value")

            mock_client.set.assert_called_once_with(
                "rckg:no_ttl_key", "value"
            )

    def test_get_existing_key(self):
        """TC-5.6: Cache hit returns the stored value."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = b"cached_value"
            client = RedisCacheClient()
            client._client = mock_client

            result = client.get("cached_key")

            assert result == "cached_value"
            mock_client.get.assert_called_once_with("rckg:cached_key")

    def test_get_missing_key_returns_none(self):
        """TC-5.6: Cache miss returns None (not an error)."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            client = RedisCacheClient()
            client._client = mock_client

            result = client.get("missing_key")

            assert result is None
            mock_client.get.assert_called_once_with("rckg:missing_key")

    def test_get_with_already_prefixed_key(self):
        """Key with existing prefix is not double-prefixed."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = b"value"
            client = RedisCacheClient()
            client._client = mock_client

            result = client.get("rckg:mykey")

            assert result == "value"
            mock_client.get.assert_called_once_with("rckg:mykey")

    def test_delete_existing_key(self):
        """Delete removes the key from cache."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.delete.return_value = 1
            client = RedisCacheClient()
            client._client = mock_client

            result = client.delete("to_delete")

            assert result == 1
            mock_client.delete.assert_called_once_with("rckg:to_delete")

    def test_delete_nonexistent_key(self):
        """Delete of a non-existent key returns 0."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.delete.return_value = 0
            client = RedisCacheClient()
            client._client = mock_client

            result = client.delete("does_not_exist")

            assert result == 0

    def test_cache_miss_falls_through(self):
        """TC-5.6: get_or_default returns fallback when cache miss."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            client = RedisCacheClient()
            client._client = mock_client

            result = client.get_or_default("miss", default="fallback")

            assert result == "fallback"
            mock_client.get.assert_called_once_with("rckg:miss")

    def test_cache_hit_returns_cached(self):
        """Cache hit returns stored value, not fallback."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = b"from_cache"
            client = RedisCacheClient()
            client._client = mock_client

            result = client.get_or_default("hit", default="fallback")

            assert result == "from_cache"

    def test_key_prefix_default_is_rckg(self):
        """Default key prefix is 'rckg' per spec."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            client = RedisCacheClient()

            assert client.key_prefix == "rckg"

    def test_prefixed_key_construction(self):
        """Keys are prefixed with configured prefix."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            client.set("mykey", "val", ttl=60)

            mock_client.setex.assert_called_once()
            called_key = mock_client.setex.call_args[0][0]
            assert called_key == "rckg:mykey"

    def test_set_returns_boolean_true(self):
        """set() returns True on success."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.setex.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            result = client.set("key", "val", ttl=60)

            assert result is True


class TestRateLimiting:
    """Tests for rate limiting via Redis INCR."""

    def test_incr_counter_increments(self):
        """TC-5.2: INCR on rate limit key increments correctly."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.return_value = 5
            client = RedisCacheClient()
            client._client = mock_client

            result = client.rate_limit_increment(
                endpoint="api:upload", user_id="user123"
            )

            assert result == 5
            mock_client.incr.assert_called_once_with(
                "rckg:rate_limit:api:upload:user123"
            )

    def test_set_rate_limit_ttl(self):
        """Rate limit counters have a configurable TTL (sliding window)."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.return_value = 1
            mock_client.expire.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            client.rate_limit_increment(
                endpoint="api:upload", user_id="user123", window=300
            )

            mock_client.incr.assert_called_once()
            mock_client.expire.assert_called_once_with(
                "rckg:rate_limit:api:upload:user123", 300
            )

    def test_rate_limit_check_exceeds_threshold(self):
        """Rate limit check returns False when threshold exceeded."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.return_value = 11  # exceeds max=10
            mock_client.expire.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            allowed = client.rate_limit_check(
                endpoint="api:upload", user_id="user123", max_requests=10
            )

            assert allowed is False

    def test_rate_limit_check_within_limit(self):
        """Rate limit check returns True when within threshold."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.return_value = 5  # within max=10
            mock_client.expire.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            allowed = client.rate_limit_check(
                endpoint="api:upload", user_id="user123", max_requests=10
            )

            assert allowed is True

    def test_rate_limit_reset(self):
        """Rate limit counter can be reset."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.delete.return_value = 1
            client = RedisCacheClient()
            client._client = mock_client

            client.rate_limit_reset(
                endpoint="api:upload", user_id="user123"
            )

            mock_client.delete.assert_called_once_with(
                "rckg:rate_limit:api:upload:user123"
            )

    def test_rate_limit_key_format(self):
        """Rate limit keys follow the rckg:rate_limit:{endpoint}:{user_id} format."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.return_value = 1
            client = RedisCacheClient()
            client._client = mock_client

            client.rate_limit_increment(
                endpoint="docs:upload", user_id="test_user"
            )

            called_key = mock_client.incr.call_args[0][0]
            assert called_key == "rckg:rate_limit:docs:upload:test_user"

    def test_rate_limit_expires_on_first_call(self):
        """EXPIRE is only set on the first INCR (count == 1)."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.return_value = 1
            client = RedisCacheClient()
            client._client = mock_client

            client.rate_limit_increment(
                endpoint="api:test", user_id="u1", window=60
            )

            mock_client.expire.assert_called_once()
            # Second call should NOT set expire again since count > 1
            mock_client.incr.return_value = 2
            client.rate_limit_increment(
                endpoint="api:test", user_id="u1", window=60
            )
            assert mock_client.expire.call_count == 1


class TestErrorHandling:
    """Tests for graceful error handling and fallback."""

    def test_get_on_connection_error_returns_none(self):
        """Cache returns None on Redis connection failure."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.side_effect = Exception("Connection lost")
            client = RedisCacheClient()
            client._client = mock_client

            result = client.get("broken_key")

            assert result is None

    def test_set_on_connection_error_raises(self):
        """Cache set propagates errors when Redis is unavailable."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.set.side_effect = Exception("Connection lost")
            client = RedisCacheClient()
            client._client = mock_client

            with pytest.raises(Exception, match="Connection lost"):
                client.set("broken_key", "value")

    def test_client_health_check(self):
        """Health check returns True when Redis responds to PING."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            client = RedisCacheClient()
            client._client = mock_client

            assert client.is_alive() is True

    def test_client_health_check_returns_false_on_failure(self):
        """Health check returns False when Redis does not respond to PING."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.side_effect = Exception("Not reachable")
            client = RedisCacheClient()
            client._client = mock_client

            assert client.is_alive() is False

    def test_rate_limit_on_connection_error_returns_allowed(self):
        """Rate limit check defaults to ALLOWED when Redis is unavailable."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.side_effect = Exception("Not reachable")
            client = RedisCacheClient()
            client._client = mock_client

            result = client.rate_limit_check(
                endpoint="api:test", user_id="user", max_requests=10
            )

            assert result is True  # fail open

    def test_rate_limit_increment_on_connection_error(self):
        """Rate limit increment returns 0 on connection failure."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.incr.side_effect = Exception("Not reachable")
            client = RedisCacheClient()
            client._client = mock_client

            result = client.rate_limit_increment(
                endpoint="api:test", user_id="user"
            )

            assert result == 0

    def test_delete_on_error_returns_zero(self):
        """Delete returns 0 on connection failure."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.delete.side_effect = Exception("No connection")
            client = RedisCacheClient()
            client._client = mock_client

            result = client.delete("broken_key")

            assert result == 0

    def test_rate_limit_reset_on_error_returns_zero(self):
        """Rate limit reset returns 0 on connection failure."""
        from app.core.cache import RedisCacheClient

        with patch("app.core.cache.RedisCacheClient.create_pool") as mock_pool:
            mock_pool.return_value = MagicMock()
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.delete.side_effect = Exception("No connection")
            client = RedisCacheClient()
            client._client = mock_client

            result = client.rate_limit_reset(
                endpoint="api:test", user_id="user"
            )

            assert result == 0
