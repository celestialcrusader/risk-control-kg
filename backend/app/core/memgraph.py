"""
Memgraph connection factory (CFIX-101).

Provides a reusable neo4j Driver instance for Memgraph,
configurable via MEMGRAPH_URI environment variable.
"""

import os
import logging
from typing import Optional, Any


logger = logging.getLogger(__name__)

_driver = None

MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
MEMGRAPH_USER = os.getenv("MEMGRAPH_USER", "")
MEMGRAPH_PASSWORD = os.getenv("MEMGRAPH_PASSWORD", "")


def get_memgraph_driver():
    """
    Return a singleton neo4j Driver connected to Memgraph.
    Returns None if the connection cannot be established.
    """
    global _driver
    if _driver is not None:
        return _driver

    try:
        from neo4j import GraphDatabase
        _driver = GraphDatabase.driver(
            MEMGRAPH_URI,
            auth=(MEMGRAPH_USER, MEMGRAPH_PASSWORD) if MEMGRAPH_USER else ("", ""),
        )
        # Verify connectivity
        _driver.verify_connectivity()
        logger.info("Memgraph driver connected to %s", MEMGRAPH_URI)
        init_memgraph_schema(_driver)
        return _driver
    except Exception as e:
        logger.warning("Failed to connect to Memgraph at %s: %s", MEMGRAPH_URI, e)
        _driver = None
        return None


def init_memgraph_schema(driver: Any) -> None:
    """Ensures Memgraph index constraints on :Clause(clause_id) and :Document(id) exist."""
    if not driver:
        return
    try:
        with driver.session() as session:
            session.run("CREATE INDEX ON :Clause(clause_id);")
            session.run("CREATE INDEX ON :Document(id);")
            logger.info("Memgraph schema index constraints verified.")
    except Exception as err:
        logger.debug("Memgraph index initialization note: %s", err)



def close_memgraph_driver():
    """Close the singleton driver on application shutdown."""
    global _driver
    if _driver is not None:
        try:
            _driver.close()
        except Exception:
            pass
        _driver = None
