"""
Unit tests for FIX-102 (3-Tier Document-Type Prompt Templates).
"""

from pathlib import Path
import pytest

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "app" / "prompts"


def test_extraction_prompt_tier1_statutory_exists():
    """
    QA Test: Verify Tier 1 statutory extraction prompt remains intact.
    """
    prompt_file = PROMPTS_DIR / "extraction.md"
    assert prompt_file.exists(), "prompts/extraction.md does not exist"

    content = prompt_file.read_text()
    assert "{{markdown_content}}" in content
    assert "atomic obligations" in content.lower()


def test_extraction_control_objective_prompt_exists():
    """
    Test that prompts/extraction_control_objective.md exists and contains required fields.
    """
    prompt_file = PROMPTS_DIR / "extraction_control_objective.md"
    assert prompt_file.exists(), "prompts/extraction_control_objective.md does not exist"

    content = prompt_file.read_text()
    assert "{{markdown_content}}" in content
    assert "control_objectives" in content
    assert "domain_facet" in content
    assert "action_verb" in content
    assert "subject_noun" in content


def test_extraction_control_activity_prompt_exists():
    """
    Test that prompts/extraction_control_activity.md exists and contains required fields.
    """
    prompt_file = PROMPTS_DIR / "extraction_control_activity.md"
    assert prompt_file.exists(), "prompts/extraction_control_activity.md does not exist"

    content = prompt_file.read_text()
    assert "{{markdown_content}}" in content
    assert "control_activities" in content
    assert "execution_type" in content
    assert "frequency" in content
    assert "action_verb" in content
    assert "subject_noun" in content
