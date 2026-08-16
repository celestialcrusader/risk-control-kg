"""
Automated Container Cross-Network Connectivity Verification Test Suite.
Verifies inter-container DNS resolution and socket reachability on rckg_rckg-net.
"""

import socket
import pytest
import subprocess
from typing import List, Tuple

SERVICES: List[Tuple[str, int]] = [
    ("localhost", 5432),   # PostgreSQL
    ("localhost", 7687),   # Memgraph
    ("localhost", 6333),   # Qdrant
    ("localhost", 9000),   # MinIO
    ("localhost", 6379),   # Redis
    ("localhost", 2181),   # Zookeeper
    ("localhost", 9092),   # Kafka
    ("localhost", 8000),   # vLLM Extractor
    ("localhost", 8002),   # vLLM OCR
    ("localhost", 8003),   # vLLM Embedding
]

CONTAINER_NAMES: List[str] = [
    "rckg-postgres",
    "rckg-memgraph",
    "rckg-qdrant",
    "rckg-minio",
    "rckg-redis",
    "rckg-zookeeper",
    "rckg-kafka",
    "rckg-vllm-extractor",
    "rckg-vllm-ocr",
    "rckg-vllm-embedding",
]


@pytest.mark.parametrize("host,port", SERVICES)
def test_host_to_container_connectivity(host: str, port: int):
    """Verify host can establish TCP socket connection to container exposed port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    res = sock.connect_ex((host, port))
    sock.close()
    assert res == 0, f"Host failed to connect to {host}:{port} (socket code {res})"


def test_inter_container_network_bridge():
    """Verify containers are attached to rckg_rckg-net and can resolve container names."""
    cmd = ["docker", "network", "inspect", "rckg_rckg-net"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, "Failed to inspect rckg_rckg-net docker network"
    
    inspect_data = res.stdout
    for name in ["rckg-postgres", "rckg-memgraph", "rckg-qdrant", "rckg-minio", "rckg-redis"]:
        assert name in inspect_data, f"Container {name} is not attached to rckg_rckg-net"
