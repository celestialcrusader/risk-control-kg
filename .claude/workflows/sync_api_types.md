---
description: Sync Frontend and Backend Types
---

# Sync Frontend API Types

**Purpose:** Ensure type definition consistency across the Python/FastAPI backend and the TypeScript/React frontend.

**Trigger:** Run this whenever a Pydantic model (`backend/app/models/` or similar) or database schema is modified, added, or removed.

## Workflow Steps

1. **Analyze Backend Changes:**
   - Review the recent modifications to the backend Pydantic models or database schemas.
   - Identify the specific fields, types, or complete models that have changed.

2. **Locate Frontend Interfaces:**
   - Find the corresponding TypeScript interfaces or types in the frontend codebase (usually in `frontend/src/types/`, `frontend/src/api/`, or related component directories).

3. **Update TypeScript Definitions:**
   - Update the frontend API interface definitions to perfectly match the updated backend schema.
   - Pay special attention to:
     - Optional fields (`Optional[int]`) translating to optional properties (`field?: number`).
     - Enums mapping correctly to string literal types or TypeScript enums.
     - Date/Time strings.

4. **Verify API Client Routes:**
   - Check the frontend API client functions (e.g., Axios or Fetch calls).
   - Ensure the request payloads (POST/PUT data) and expected response types are updated to use the modified interfaces.

5. **Type Check:**
   - Run the frontend typescript compiler to ensure no type errors have been introduced:
// turbo
   `npm run typecheck` (or the equivalent command in the frontend directory).

6. **Fix Breakages:**
   - If the type check fails, go through the frontend codebase and fix any components or hooks that are using the outdated data structures.
