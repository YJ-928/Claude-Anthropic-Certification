# 03 — Messages API

## Overview

The Messages API is the primary interface to Claude. Every request is a list of alternating `user` / `assistant` turns.

```
Request Structure
│
├── model          (required)
├── max_tokens     (required)
├── messages       (required) ─── [{"role": "user"|"assistant", "content": "..."}]
├── system         (optional) ─── plain string
├── temperature    (optional) ─── 0.0 – 1.0
└── stream         (optional) ─── True for streaming
```

## Message Format

```python
messages = [
    {"role": "user",      "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user",      "content": "What is Python?"},
]
```

Rules:
- Must start with `"user"`
- Must alternate `user` → `assistant` → `user` → ...
- Cannot have two consecutive messages from the same role

## Content Blocks

Each message's `content` can be a plain string **or** a list of typed blocks:

```python
# Simple string (most common)
{"role": "user", "content": "Hello"}

# Multi-block (text + image)
{"role": "user", "content": [
    {"type": "text",  "text": "What is in this image?"},
    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}},
]}
```

## Code Example

```python
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=512,
    system="You are a concise assistant. Always reply in one sentence.",
    messages=[
        {"role": "user",      "content": "What is machine learning?"},
        {"role": "assistant", "content": "Machine learning is"},  # pre-fill
    ]
)
```

## Best Practices

- Keep `max_tokens` realistic — 512 for short answers, 4096 for long-form content
- Put stable instructions in `system` rather than repeating them in every user message
- Store the full `messages` list and send it each turn for multi-turn conversations

## Common Mistakes

- Putting the system prompt inside `messages` instead of the `system` parameter
- Starting messages with `"assistant"` (API rejects this)
- Not appending Claude's reply to history before the next turn

## Exercise

Write a function that takes a list of `(role, text)` tuples and converts it to the messages format, then sends it to the API.
