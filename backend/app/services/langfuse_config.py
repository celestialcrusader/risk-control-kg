"""
Langfuse environment configuration for OBSERV-1.

Provides centralized Langfuse configuration with environment-based project
scoping. Uses os.environ.get() with sensible defaults — no hardcoded
production keys.

Supported environment variables:
- LANGFUSE_SECRET_KEY    : Secret API key (from Langfuse dashboard)
- LANGFUSE_PUBLIC_KEY    : Public API key (from Langfuse dashboard)
- LANGFUSE_HOST          : Langfuse host URL (default: http://localhost:3000)
- LANGFUSE_RELEASE       : Release/version for trace scoping (default: development)
- LANGFUSE_USER_ID       : User ID for trace attribution
"""

import logging
import os

logger = logging.getLogger(__name__)

# Conditionally import langfuse; may not be installed
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None
    logger.debug("langfuse not installed, observability logging will be skipped")

# Default project name for all environments
DEFAULT_PROJECT_NAME = "rckg"

# Default host — local development Langfuse instance
DEFAULT_HOST = "http://localhost:3000"

# Default environment when LANGFUSE_RELEASE is not set
DEFAULT_ENVIRONMENT = "development"


def get_langfuse_config() -> dict | None:
    """
    Load Langfuse configuration from environment variables.

    Returns a dict with configuration keys if langfuse is installed and
    credentials are available. Returns None if langfuse is not installed.

    This function intentionally does NOT raise exceptions — it returns
    None on any failure so that downstream code can gracefully degrade.

    Returns:
        Dict with keys: secret_key, public_key, host, environment,
        project_name, dashboard_url, user_id, or None if unavailable.
    """
    if Langfuse is None:
        logger.debug("langfuse not installed, skipping configuration")
        return None

    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    host = os.environ.get("LANGFUSE_HOST", DEFAULT_HOST)
    release = os.environ.get("LANGFUSE_RELEASE", DEFAULT_ENVIRONMENT)
    user_id = os.environ.get("LANGFUSE_USER_ID")
    project_name = os.environ.get("LANGFUSE_PROJECT_NAME", DEFAULT_PROJECT_NAME)

    # Require both keys — cannot initialize without them
    if not secret_key or not public_key:
        logger.debug(
            "Langfuse credentials not fully configured "
            "(LANGFUSE_SECRET_KEY=%s, LANGFUSE_PUBLIC_KEY=%s)",
            bool(secret_key),
            bool(public_key),
        )
        return None

    dashboard_url = host.rstrip("/")

    return {
        "secret_key": secret_key,
        "public_key": public_key,
        "host": host,
        "environment": release,
        "project_name": project_name,
        "dashboard_url": dashboard_url,
        "user_id": user_id,
    }
