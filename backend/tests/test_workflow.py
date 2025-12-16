import pytest
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Trying to import the workflow - will fail initially
try:
    from app.workflows.proposal import create_proposal_workflow, ProposalState
except ImportError:
    create_proposal_workflow = None
    ProposalState = None

def test_workflow_state_transition():
    """
    TDD Mandate: Test for a state machine transition to verify state and flow control.
    We want a simple 'Review' workflow: Draft -> (Review) -> Approved/Rejected.
    """
    if create_proposal_workflow is None:
        pytest.fail("Workflow module not implemented")

    # Initialize workflow
    app = create_proposal_workflow()
    
    # 1. Start with a draft
    initial_state = {"status": "draft", "content": "Risk 1", "feedback": ""}
    
    # Run the graph (simulating valid transition)
    # The workflow should move draft -> pending_review
    output = app.invoke(initial_state)
    
    assert output["status"] == "pending_review"
    assert output["content"] == "Risk 1"

def test_workflow_rejection_loop():
    """Test that rejection sends it back to draft"""
    if create_proposal_workflow is None:
        pytest.fail("Workflow module not implemented")

    app = create_proposal_workflow()
    
    # Start in pending_review with rejection feedback
    state = {"status": "pending_review", "content": "Risk 1", "feedback": "Too vague", "action": "reject"}
    
    output = app.invoke(state)
    
    assert output["status"] == "draft"
    assert "Too vague" in output["feedback"]
