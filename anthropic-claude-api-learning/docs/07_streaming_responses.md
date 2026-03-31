# 07 — Streaming Responses

## Overview

Instead of waiting for the full response, streaming delivers tokens to the client as they are generated — giving users immediate feedback.

```
Without Streaming             With Streaming
────────────────────          ────────────────────────────────
[.... 8 seconds ...]          H → He → Hel → Hell → Hello → ...
Full text appears             Token by token, instantly
```

## How It Works

```python
with client.messages.stream(
    model="claude-haiku-4-5",
    max_tokens=512,
    messages=[{"role": "user", "content": "Tell me a story."}]
) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
print()  # final newline
```

## Pattern: Collect Full Text

```python
full_text = ""
with client.messages.stream(...) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
        full_text += chunk
# full_text now has the complete response
```

## Pattern: Server-Sent Events (FastAPI)

```python
from fastapi.responses import StreamingResponse

async def chat_stream(prompt: str):
    async def generator():
        with client.messages.stream(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for chunk in stream.text_stream:
                yield f"data: {chunk}\n\n"
    return StreamingResponse(generator(), media_type="text/event-stream")
```

## Best Practices

- Always use streaming for user-facing applications
- Use `flush=True` when printing to terminal so tokens appear immediately
- Collect `full_text` alongside streaming so you can store the complete response

## Common Mistakes

- Forgetting the context manager (`with ... as stream:`)
- Not flushing stdout in terminal apps
- Opening multiple streams in parallel without rate limiting

## Exercise

Build a streaming chat loop where each response is also word-counted and the count is printed after the stream ends. Use `utils/streaming_helpers.py` as a reference.
