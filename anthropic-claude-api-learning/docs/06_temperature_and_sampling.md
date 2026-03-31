# 06 — Temperature and Sampling

## Overview

Temperature controls how **random** Claude's output is by adjusting the probability distribution over possible next tokens.

```
Temperature 0.0                    Temperature 1.0
──────────────────────             ──────────────────────
Always picks the most              Gives more probability to
likely token → deterministic       lower-probability tokens → creative
```

## Range

| Value | Behaviour | Use Case |
|-------|-----------|---------- |
| `0.0` | Fully deterministic | Data extraction, fact lookup, code generation |
| `0.3` | Mostly consistent | Summarisation, classification |
| `0.7` | Balanced | General Q&A, documentation |
| `1.0` | Creative | Brainstorming, marketing copy, stories |

## Code Example

```python
for temperature in [0.0, 0.5, 1.0]:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        temperature=temperature,
        messages=[{"role": "user", "content": "Write a tagline for a coffee brand."}]
    )
    print(f"temp={temperature}: {response.content[0].text.strip()}")
```

## Best Practices

- Default to `temperature=1.0` (Anthropic SDK default) unless you need consistency
- Use `temperature=0.0` for any task where the correct answer is deterministic
- Run the same prompt 3–5 times at your chosen temperature to spot variance

## Common Mistakes

- Setting `temperature=0` for creative tasks (outputs become repetitive)
- Expecting temperature changes to always produce different outputs — at `1.0` you can still get similar outputs by chance
- Confusing temperature with `top_p` (top-p is an alternative sampling parameter, not used simultaneously)

## Exercise

Send the same extraction prompt ("What year was Python created? Reply with the year only.") at temperatures 0.0 and 1.0 ten times each. Count how many times each returns "1991" vs something else.
