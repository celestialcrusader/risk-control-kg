"""
Structured Observability & Degradation Event Logging (CFIX-301).
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("rckg.observability")


def log_degradation_event(
    service: str,
    method_used: str,
    error: Any,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Emits a structured JSON degradation event log.

    Returns the payload dictionary for verification and telemetry forwarding.
    """
    payload = {
        "event": "LLM_DEGRADATION",
        "service": service,
        "method_used": method_used,
        "error": str(error),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context or {},
    }
    logger.warning("LLM_DEGRADATION_EVENT: %s", json.dumps(payload))
    return payload
