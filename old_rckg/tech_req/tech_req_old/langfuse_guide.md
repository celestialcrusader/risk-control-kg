# Langfuse Integration Guide

This guide documents the standard pattern for using Langfuse Prompt Management in the RCKG backend.

## 1. LLM Client Updates (`backend/app/core/llm.py`)

Ensure the `LLMClient` has the following:

- **Initialization**: `Langfuse` client initialized safely with env var checks.
- **Helper Method**: `get_prompt_object(name)` to fetch the raw Langfuse prompt object.
- **Trace Linking**: The `chat` (or `generate`) method must exit the observation context to update the generation.

### Standard `chat` Implementation:

```python
    @observe(as_type="generation")
    def chat(self, messages: List[Dict[str, str]], langfuse_prompt=None) -> str:
        # Link generation to specific prompt version if provided
        if langfuse_prompt and self.langfuse:
            try:
                # CRITICAL: Use the client instance method, NOT the context decorator import
                self.langfuse.update_current_generation(prompt=langfuse_prompt)
            except Exception as e:
                print(f"Warning: Failed to link prompt generation: {e}")

        # ... rest of logic ...
```

## 2. Usage Pattern (e.g., in `rag.py`)

When implementing a feature that uses a prompt:

1.  **Fetch Object**: Use `get_prompt_object` (don't just get the string).
2.  **Compile Locally**: Use `prompt.compile(**kwargs)` to get the string for the LLM.
3.  **Pass Object**: Pass the *original prompt object* to the `chat` method.

### Example:

```python
# 1. Fetch Object
try:
    lf_prompt = self.llm.get_prompt_object("my-prompt-name")
    # 2. Compile
    system_instruction = lf_prompt.compile(context=my_context)
except Exception:
    # Fallback to hardcoded string
    lf_prompt = None
    system_instruction = "Default system prompt..."

# Prepare Messages
messages = [
    {"role": "system", "content": system_instruction},
    {"role": "user", "content": user_input}
]

# 3. Pass Object for Linking
response = self.llm.chat(messages, langfuse_prompt=lf_prompt)
```

## 3. Environment Variables

Required in `.env` and `docker-compose.yml`:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com (or local host)
```
