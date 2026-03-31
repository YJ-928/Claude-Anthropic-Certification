# 02 — Anthropic API Basics

## Overview

The Anthropic Python SDK wraps the REST API. Authentication is via an API key loaded from the environment.

```
Your Code
    │
    ▼
Anthropic()          ← creates a client, reads ANTHROPIC_API_KEY from env
    │
    ▼
client.messages.create(...)   ← single API call
    │
    ▼
Message object       ← response.content[0].text = reply string
```

## Setup

```bash
pip install anthropic python-dotenv
```

```plaintext
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

## Code Example

```python
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()          # reads .env into os.environ
client = Anthropic()   # automatically uses ANTHROPIC_API_KEY

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=256,
    messages=[{"role": "user", "content": "What is 2 + 2?"}]
)

print(response.content[0].text)   # "4"
print(response.stop_reason)       # "end_turn" | "max_tokens" | "stop_sequence"
```

## Response Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique message ID |
| `model` | str | Model that was used |
| `content` | list | Array of content blocks |
| `content[0].text` | str | Text of first block |
| `stop_reason` | str | Why generation stopped |
| `usage.input_tokens` | int | Tokens in your prompt |
| `usage.output_tokens` | int | Tokens in the reply |

## Best Practices

- Never hardcode the API key — always use environment variables
- Check `stop_reason` — if it's `"max_tokens"` the response was truncated
- Use a single shared `Anthropic()` instance rather than creating new ones per call

## Common Mistakes

- Forgetting to call `load_dotenv()` before `Anthropic()`
- Setting `max_tokens` too low and getting truncated responses
- Accessing `response.content[0].text` when content might be empty

## Exercise

Write a function `safe_chat(prompt, max_tokens=512)` that calls the API, checks `stop_reason`, and raises a warning if the response was truncated.
