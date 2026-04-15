"""
Test suite for INFRA-1: Docker Compose Infrastructure Stack

This test module verifies that the Docker Compose stack can be deployed
and all services are healthy and responding correctly.

Test Strategy:
- Integration tests that actually start Docker containers
- Tests verify service health, API endpoints, and connectivity
- All tests are marked as integration tests (requires Docker daemon)
"""

import os
import time
import subprocess
import pytest
from pathlib import Path

# Test configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
COMPOSE_ENV = PROJECT_ROOT / ".env"

# Service health check timeouts (in seconds)
COMPOSE_START_TIMEOUT = 300  # 5 minutes max for all services to start
SERVICE_READY_TIMEOUT = 60   # Max seconds to wait for each service to be ready

# Services that must be in the stack
REQUIRED_SERVICES = [
    "postgres",
    "memgraph",
    "qdrant",
    "minio",
    "redis",
    "temporal",
    "langfuse",
    "kafka",
    "zookeeper",
]


class TestDockerComposeStack:
    """Integration tests for the Docker Compose infrastructure stack."""

    @pytest.fixture(scope="class")
    def compose_up(self):
        """
        Fixture to start the Docker Compose stack before tests.

        This fixture:
        1. Checks if docker-compose.yml exists
        2. Starts all services with docker-compose up -d
        3. Waits for services to become healthy
        4. Tears down all services after tests complete
        """
        # Verify docker-compose.yml exists
        assert COMPOSE_FILE.exists(), f"docker-compose.yml not found at {COMPOSE_FILE}"

        # Start the stack (use docker compose v2)
        print(f"\nStarting Docker Compose stack from {COMPOSE_FILE}...")
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")

        assert result.returncode == 0, f"Failed to start docker-compose: {result.stderr}"

        # Wait for services to become healthy
        print("Waiting for services to become healthy...")
        start_time = time.time()
        while time.time() - start_time < COMPOSE_START_TIMEOUT:
            result = subprocess.run(
                ["docker", "compose", "ps"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                # Check if all services are running
                for service in REQUIRED_SERVICES:
                    if service not in result.stdout:
                        time.sleep(5)
                        break
                else:
                    # All services are in the status output
                    print("All services started successfully!")
                    break
            time.sleep(5)
        else:
            raise TimeoutError(
                f"Timeout waiting for services to start. Current status:\n{result.stdout}"
            )

        yield

        # Tear down after all tests
        print("\nTearing down Docker Compose stack...")
        subprocess.run(
            ["docker-compose", "down", "-v"],
            cwd=PROJECT_ROOT,
            capture_output=True,
        )

    @pytest.mark.integration
    def test_compose_file_exists(self):
        """TC-1.1: Verify docker-compose.yml exists in project root."""
        assert COMPOSE_FILE.exists(), "docker-compose.yml must exist in project root"

    @pytest.mark.integration
    def test_env_file_exists(self, compose_up):
        """TC-1.2: Verify .env or .env.example exists."""
        env_file = COMPOSE_ENV
        # Either .env or .env.example should exist
        assert (
            env_file.exists() or (COMPOSE_ENV.with_suffix(".example")).exists()
        ), ".env or .env.example must exist"

    @pytest.mark.integration
    def test_all_services_start(self, compose_up):
        """TC-1.3: All 9 infrastructure services must start successfully."""
        result = subprocess.run(
            ["docker", "compose", "ps"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "docker compose ps command failed"

        for service in REQUIRED_SERVICES:
            assert (
                service in result.stdout
            ), f"Service '{service}' is not running. Full output:\n{result.stdout}"

    @pytest.mark.integration
    def test_postgres_health(self, compose_up):
        """TC-1.4: PostgreSQL health check returns HTTP 200 with database connectivity."""
        # Wait for PostgreSQL to be ready
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                [
                    "docker", "compose", "exec", "-T", "postgres",
                    "pg_isready", "-U", "rckg", "-d", "rckg_db",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                break
            time.sleep(5)
        else:
            raise TimeoutError("PostgreSQL not ready after timeout")

        assert (
            "accepting connections" in result.stdout or result.returncode == 0
        ), f"PostgreSQL not accepting connections: {result.stderr}"

    @pytest.mark.integration
    def test_memgraph_status(self, compose_up):
        """TC-1.5: Memgraph REST API returns service status."""
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                ["curl", "-s", "http://localhost:7687"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "Memgraph" in result.text:
                break
            time.sleep(5)
        else:
            raise TimeoutError("Memgraph not responding after timeout")

        assert result.returncode == 0, f"Memgraph health check failed: {result.stderr}"
        assert "Memgraph" in result.text, f"Memgraph version not in response: {result.text}"

    @pytest.mark.integration
    def test_qdrant_version(self, compose_up):
        """TC-1.6: Qdrant REST API returns the service version."""
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                ["curl", "-s", "http://localhost:6333/version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "version" in result.text.lower():
                break
            time.sleep(5)
        else:
            raise TimeoutError("Qdrant version endpoint not responding after timeout")

        assert result.returncode == 0, f"Qdrant version check failed: {result.stderr}"
        assert "version" in result.text.lower(), f"Qdrant version not in response: {result.text}"

    @pytest.mark.integration
    def test_minio_console_accessible(self, compose_up):
        """TC-1.7: MinIO console is accessible at localhost:9001."""
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:9001"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.text.startswith("2"):
                break
            time.sleep(5)
        else:
            raise TimeoutError("MinIO console not accessible after timeout")

        assert result.returncode == 0, f"MinIO console connection failed: {result.stderr}"
        assert result.text.startswith("2"), f"MinIO console returned HTTP {result.text}"

    @pytest.mark.integration
    def test_redis_ping(self, compose_up):
        """TC-1.8: Redis responds to PING command."""
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                ["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "PONG" in result.stdout:
                break
            time.sleep(5)
        else:
            raise TimeoutError("Redis not responding after timeout")

        assert "PONG" in result.stdout, f"Redis PING failed: {result.stderr}"

    @pytest.mark.integration
    def test_temporal_web_ui(self, compose_up):
        """TC-1.9: Temporal Web UI is accessible at localhost:8233."""
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8233"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.text.startswith("2"):
                break
            time.sleep(5)
        else:
            raise TimeoutError("Temporal Web UI not accessible after timeout")

        assert result.returncode == 0, f"Temporal Web UI connection failed: {result.stderr}"
        assert result.text.startswith("2"), f"Temporal Web UI returned HTTP {result.text}"

    @pytest.mark.integration
    def test_langfuse_web_ui(self, compose_up):
        """TC-1.10: Langfuse Web UI is accessible at localhost:3000."""
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:3000"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.text.startswith("2"):
                break
            time.sleep(5)
        else:
            raise TimeoutError("Langfuse Web UI not accessible after timeout")

        assert result.returncode == 0, f"Langfuse Web UI connection failed: {result.stderr}"
        assert result.text.startswith("2"), f"Langfuse Web UI returned HTTP {result.text}"

    @pytest.mark.integration
    def test_kafka_zookeeper_running(self, compose_up):
        """TC-1.11: Kafka and Zookeeper are both running."""
        result = subprocess.run(
            ["docker", "compose", "ps"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "docker compose ps command failed"
        assert "kafka" in result.stdout, "Kafka service is not running"
        assert "zookeeper" in result.stdout, "Zookeeper service is not running"

    @pytest.mark.integration
    def test_docker_compose_ps(self, compose_up):
        """TC-1.12: docker-compose ps shows all containers as running."""
        result = subprocess.run(
            ["docker", "compose", "ps"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "docker compose ps command failed"
        # All services should appear in the output with running status
        for service in REQUIRED_SERVICES:
            assert service in result.stdout, f"Service '{service}' missing from docker-compose ps output"

    @pytest.mark.integration
    def test_minio_buckets_created(self, compose_up):
        """TC-1.13: MinIO buckets are created by minio-init service."""
        # Wait for minio-init to complete
        time.sleep(10)
        # Check buckets exist via mc client
        result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "minio",
                "mc", "ls", "rckg"
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"MinIO bucket list failed: {result.stderr}"
        # Verify expected buckets exist
        expected_buckets = ["source-regulations", "minio-data", "markdown-conversions", "evidence-artifacts"]
        for bucket in expected_buckets:
            assert bucket in result.stdout, f"Bucket '{bucket}' not found. Output: {result.stdout}"

    @pytest.mark.integration
    def test_postgres_sql_query(self, compose_up):
        """TC-1.14: PostgreSQL accepts SQL queries (not just TCP connections)."""
        # Wait for PostgreSQL to be ready
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                [
                    "docker", "compose", "exec", "-T", "postgres",
                    "psql", "-U", "rckg", "-d", "rckg_db", "-c", "SELECT 1 AS test"
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "1" in result.stdout:
                break
            time.sleep(5)
        else:
            raise TimeoutError("PostgreSQL SQL query failed after timeout")

        assert result.returncode == 0, f"PostgreSQL SQL query failed: {result.stderr}"
        assert "test" in result.stdout.lower() or "1" in result.stdout, \
            f"Expected query result not found: {result.stdout}"

    @pytest.mark.integration
    def test_temporal_namespace_exists(self, compose_up):
        """TC-1.15: Temporal rckg-production namespace exists."""
        # Wait for Temporal to be ready
        for _ in range(SERVICE_READY_TIMEOUT // 5):
            result = subprocess.run(
                [
                    "curl", "-s",
                    "http://localhost:8233/api/v1/namespaces/rckg-production"
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "namespaceInfo" in result.text.lower():
                break
            time.sleep(5)
        else:
            raise TimeoutError("Temporal namespace not found after timeout")

        assert result.returncode == 0, f"Temporal namespace check failed: {result.stderr}"
        assert "rckg-production" in result.text, \
            f"rckg-production namespace not found in response: {result.text}"

    @pytest.mark.integration
    def test_services_can_reach_each_other_via_hostname(self, compose_up):
        """TC-1.16: Services can communicate via Docker network hostnames."""
        # Test that postgres is reachable from a service that depends on it
        result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "temporal",
                "pg_isready", "-h", "postgres", "-U", "rckg", "-d", "rckg_db"
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, \
            f"Temporal cannot reach postgres via hostname: {result.stderr}"
        assert "accepting" in result.stdout.lower() or "accepting connections" in result.stdout.lower(), \
            f"PostgreSQL not accepting connections from temporal: {result.stdout}"

    @pytest.mark.integration
    def test_network_rckg_net_exists(self, compose_up):
        """TC-1.17: Dedicated rckg-net bridge network exists."""
        result = subprocess.run(
            ["docker", "network", "ls", "--filter", "name=rckg-net", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "docker network ls failed"
        assert "rckg-net" in result.stdout, \
            f"rckg-net network not found. Networks: {result.stdout}"


class TestComposeCommands:
    """Tests for docker-compose commands documented in setup-guide.md."""

    @pytest.fixture(scope="class")
    def compose_running(self):
        """Ensure compose stack is running for these tests."""
        if not COMPOSE_FILE.exists():
            pytest.skip("docker-compose.yml not found, skipping command tests")

        # Start if not already running
        result = subprocess.run(
            ["docker-compose", "ps"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if "No services" in result.stdout or result.returncode != 0:
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=PROJECT_ROOT,
                capture_output=True,
            )
        yield
        # Don't tear down - let other tests use the running stack

    @pytest.mark.integration
    def test_compose_logs_command(self, compose_running):
        """TC-2.1: docker compose logs command works."""
        result = subprocess.run(
            ["docker", "compose", "logs", "postgres"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"docker-compose logs failed: {result.stderr}"

    @pytest.mark.integration
    @pytest.mark.usefixtures("compose_running")
    def test_compose_stop_start(self):
        """TC-2.2: Services can be stopped and restarted successfully."""
        # Stop the stack
        result = subprocess.run(
            ["docker", "compose", "down"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"docker compose down failed: {result.stderr}"

        # Restart
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"docker compose up failed: {result.stderr}"

        # Verify services are running again
        time.sleep(10)
        result = subprocess.run(
            ["docker-compose", "ps"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "docker-compose ps failed after restart"
        for service in REQUIRED_SERVICES:
            assert service in result.stdout, f"Service '{service}' not running after restart"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
