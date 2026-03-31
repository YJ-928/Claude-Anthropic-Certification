# 26 — Prompt Caching

## Overview

Prompt caching saves an expensive context (system prompt, long document) server-side. Subsequent requests that reuse the same context pay ~10% of normal input token cost.

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},   # <-- cache this
        }
    ],
    messages=[{"role": "user", "content": user_question}]
)

print(response.usage.cache_creation_input_tokens)  # first call: > 0
print(response.usage.cache_read_input_tokens)      # second call: > 0
```

## Cache Lifetime
- Ephemeral cache: **5 minutes** TTL
- Refreshed on each cache hit within the window

## Best Practices
- Cache system prompts, long documents, and tool schemas
- Cache is per account + model + context — changing any byte invalidates it
- Combine with contextual retrieval for maximum cost savings

## Exercise
Make 5 API calls with the same system prompt. Log `cache_creation_input_tokens` vs `cache_read_input_tokens` for each call and calculate effective cost savings.
