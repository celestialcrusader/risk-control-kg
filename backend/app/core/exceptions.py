"""
Custom exception classes for RCKG core components.
"""

class OperationNotPermitted(PermissionError):
    """Raised when an action is prohibited by safety rules or governance policies."""
    pass
