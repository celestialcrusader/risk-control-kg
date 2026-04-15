---
description: How to safely apply changes to the Docker stack (Frontend & Backend)
---
// turbo-all

# Deployment Protocol

Use this workflow whenever you change code in `frontend/` or `backend/` and need to apply it to the running stack.

**CRITICAL RULE**: Never use `docker-compose restart` after a build. It reuses the old container hash. ALWAYS use `up -d --force-recreate` to pick up the new image.

## 1. Frontend Changes (React/HTML/CSS)
Since the frontend uses a multi-stage build (Node -> Nginx), the source code changes in `/app` are NOT live-reloaded effectively for production builds.

1.  **Rebuild Image** (Force clean build):
    ```bash
    docker-compose build frontend --no-cache
    ```

2.  **Deploy Container** (Force recreation):
    ```bash
    docker-compose up -d --force-recreate frontend
    ```

## 2. Backend Changes (Python)
Dependencies or structural changes require a rebuild.

1.  **Rebuild Image**:
    ```bash
    docker-compose build backend --no-cache
    ```

2.  **Deploy Container**:
    ```bash
    docker-compose up -d --force-recreate backend
    ```

## 3. Full Stack Reset (When in doubt)
If strange bugs persist (e.g., stale schema, ghost deletion):

1.  **Nuke and Pave**:
    ```bash
    docker-compose down -v
    docker-compose build --no-cache
    docker-compose up -d --force-recreate
    ```
