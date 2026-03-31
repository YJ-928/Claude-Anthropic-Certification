# 01 — Claude Models

## Overview

Anthropic offers a family of Claude models optimised for different speed/cost/capability tradeoffs.

```
Model Family
│
├── claude-opus-4          ← most capable, best for complex reasoning
├── claude-sonnet-4-5      ← balanced: capable + fast, best for production
└── claude-haiku-4-5       ← fastest + cheapest, best for high-volume tasks
```

## Model Comparison

| Model | Context Window | Relative Speed | Best Use Case |
|-------|---------------|---------------|---------------|
| `claude-opus-4` | 200K tokens | Slower | Complex reasoning, long documents |
| `claude-sonnet-4-5` | 200K tokens | Balanced | Production APIs, general use |
| `claude-haiku-4-5` | 200K tokens | Fastest | Exercises, grading, classification |

## Key Concepts

- **Context window**: total tokens Claude can process in one request (input + output combined)
- **Input tokens**: tokens in your messages + system prompt
- **Output tokens**: tokens in Claude's response
- **Billing**: input and output tokens are priced separately; cached tokens are discounted

## Code Example

```python
from anthropic import Anthropic

client = Anthropic()

# Cheaper/faster model for simple tasks
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.model)          # actual model used
print(response.usage)          # input/output token counts
```

## Best Practices

- Use `claude-haiku-4-5` for evaluation pipelines, batch processing, classification
- Use `claude-sonnet-4-5` for production user-facing features
- Use `claude-opus-4` only when maximum reasoning capability is required
- Always log `response.usage` to track costs

## Common Mistakes

- Using `claude-opus-4` for simple tasks (wastes money)
- Hardcoding model names (use a config constant so you can swap easily)
- Ignoring token counts (context window limits apply to the combined input+output)

## Exercise

Write a function `compare_models(prompt)` that sends the same prompt to all three models and prints the response and token usage for each.
