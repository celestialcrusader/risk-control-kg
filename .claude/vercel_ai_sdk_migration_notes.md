# Vercel AI SDK Migration Notes (v3 to v4)

This document serves as a persistent technical reference for the Agent when working with `@ai-sdk/react` version 3.0.99 or higher (v4 architecture).

## Key Breaking Changes in `useChat`

During the upgrade from earlier versions to the cutting-edge versions of the Vercel AI SDK, several major architectural changes were introduced that break legacy React implementations.

### 1. Removal of Automatic Input State Management
Older versions of `useChat` returned `input`, `handleInputChange`, and `handleSubmit` directly. These have been **removed**.

**Old Approach (v2/Early v3):**
```tsx
const { messages, input, handleInputChange, handleSubmit } = useChat({ api: '/api/chat' });

<form onSubmit={handleSubmit}>
    <input value={input} onChange={handleInputChange} />
</form>
```

**New Approach (Current):**
The component must now manage its own React state for the draft input, and manually dispatch the message using the `sendMessage` function.

```tsx
import { useState } from 'react';
import { useChat } from '@ai-sdk/react';

const [input, setInput] = useState('');
const { messages, sendMessage } = useChat({ ...options });

const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage({ content: input, role: 'user' });
    setInput('');
};
```

### 2. Network Transport Decoupling (`api` and `headers`)
Older versions allowed you to specify `api` and `headers` directly in the `useChat` options. In the newer architecture, network requests have been decoupled into a dedicated `ChatTransport` layer.

If you pass `api` directly into `useChat`, it will be **silently ignored**, and the SDK will blindly default to POSTing to `/api/chat`. If your backend is on a different route, this will result in HTTP 404 or HTTP 405 (Not Allowed) errors from the reverse proxy (e.g., NGINX).

**Old Approach (v2/Early v3):**
```tsx
const chat = useChat({
    api: '/api/v1/agent/chat',
    headers: { 'X-Forwarded-User': 'test' }
});
```

**New Approach (Current):**
You must import `DefaultChatTransport` from the core `ai` package and configure the `transport` property.

```tsx
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';

const chat = useChat({
    transport: new DefaultChatTransport({
        api: '/api/v1/agent/chat',
        headers: {
            'X-Forwarded-User': 'test'
        }
    })
});
```

### 3. Telemetry Data Restructuring
If we intend to implement Telemetry and Tracing via OpenTelemetry/Langfuse for the AI SDK, beware that the telemetry data keys have been nested under a `response` object.

*   `ai.finishReason` ➡️ `ai.response.finishReason`
*   `ai.result.object` ➡️ `ai.response.object`
*   `ai.result.text` ➡️ `ai.response.text`
*   `ai.result.toolCalls` ➡️ `ai.response.toolCalls`
*   `ai.stream.msToFirstChunk` ➡️ `ai.response.msToFirstChunk`

### 4. Provider Changes (Anthropic)
The top-level Anthropic facade has been removed. You must now explicitly use the `anthropic` object or the `createAnthropic` factory function.
Additionally, model-specific `topK` settings for Anthropics and Google Generative AI have been removed in favor of a standardized, cross-provider `topK` parameter in request options.

### 5. Structured Data Strictness
In future updates (specifically v5), the default behavior for structured output schema strictness (for chat models) changes from `true` to `false`. When using `generateObject` or `streamObject`, we must explicitly ensure validation logic handles non-strict parsing or explicitly define strictness if the underlying model provider supports it.

### Required Package Versions
When updating, ensure the peer dependencies are strictly aligned to the v4 ecosystem:
*   `ai`: `^4.0.0`
*   `@ai-sdk/provider-utils`: `^2.0.0`
*   `@ai-sdk/react`: `^1.0.0` (Note: Vercel separated the React hooks versioning from the core `ai` versioning recently. `@ai-sdk/react` 1.x depends on `ai` 4.x).

## Summary for Agentic Implementation
When instructed to build a chat interface using the Vercel AI SDK:
1. **Always use custom state** (`useState`) for the text input.
2. **Always use `sendMessage`** to flush the text to the SDK messages array.
3. **Always use `DefaultChatTransport`** if a custom API route or custom HTTP headers (like authentication) are required.
