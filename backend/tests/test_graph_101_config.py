"""
TDD Unit/Integration Test for STORY-GRAPH-101: Config & Consolidated Model Matrix (Qwen3.6-35B-A3B).
"""

import os
import pytest


def test_graph_101_langgraph_imports():
    """Verify langgraph and langchain_core can be imported."""
    import langgraph.graph
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.postgres import PostgresSaver
    
    assert StateGraph is not None
    assert END is not None
    assert PostgresSaver is not None


def test_graph_101_model_matrix_config():
    """Verify Qwen3.6-35B-A3B consolidated model environment configuration."""
    from app.services.extraction import LLM_MODEL, LLM_ENDPOINT
    from app.services.judge import JUDGE_MODEL, JUDGE_ENDPOINT

    assert LLM_MODEL == "Qwen/Qwen3.6-35B-A3B"
    assert JUDGE_MODEL == "Qwen/Qwen3.6-35B-A3B"
    assert LLM_ENDPOINT == "http://localhost:8000/v1"
    assert JUDGE_ENDPOINT == "http://localhost:8000/v1"
