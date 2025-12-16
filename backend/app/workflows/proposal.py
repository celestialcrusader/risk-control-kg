from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END

# Define the state schema
class ProposalState(TypedDict):
    status: str
    content: str
    feedback: Optional[str]
    action: Optional[str]  # 'submit', 'approve', 'reject'

# Node: Submit Draft
def submit_draft(state: ProposalState) -> ProposalState:
    # Logic: If status is draft, move to pending_review
    # In real world, might call LLM to polish
    return {"status": "pending_review"}

# Node: Review Process
def review_proposal(state: ProposalState) -> ProposalState:
    # This node just decides where to go based on 'action'
    # Actually, we probably want a conditional edge, but for this simple test
    # let's have a node that processes the 'action' input if present
    
    action = state.get("action")
    if action == "reject":
        return {"status": "draft"}
    elif action == "approve":
        return {"status": "approved"}
    
    # default pass through if no action taken (still pending)
    return {"status": "pending_review"}

# Conditional Logic
def route_submission(state: ProposalState):
    if state["status"] == "draft":
        return "submit_draft"
    elif state["status"] == "pending_review":
        return "review_proposal"
    return END

def create_proposal_workflow():
    builder = StateGraph(ProposalState)
    
    builder.add_node("submit_draft", submit_draft)
    builder.add_node("review_proposal", review_proposal)
    
    # Basic logic:
    # Start -> Router -> Node
    
    # For this simple test, let's just make it linear based on input state
    # If input is 'draft', go to submit_draft
    # If input is 'pending_review', go to review_proposal
    
    def router(state: ProposalState):
        if state["status"] == "draft":
            return "submit_draft"
        if state["status"] == "pending_review":
            return "review_proposal"
        return END

    builder.add_conditional_edges(START, router)
    builder.add_edge("submit_draft", END)
    builder.add_edge("review_proposal", END)

    return builder.compile()
