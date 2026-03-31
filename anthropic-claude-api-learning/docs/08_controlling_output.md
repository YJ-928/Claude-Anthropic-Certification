# 08 — Controlling Output (Pre-filling & Stop Sequences)

## Overview

Two techniques give you precise control over the **format** of Claude's output without relying on prompt instructions alone.

```
Technique         How                         Use Case
──────────────    ─────────────────────────   ─────────────────────────
Pre-filling       Add partial assistant turn   Force a specific start format
Stop sequences    Tell Claude where to stop    Extract delimited content
```

## Pre-filling

Add a partial `assistant` message as the last item in `messages`. Claude continues from exactly where you left off.

```python
messages = [
    {"role": "user",      "content": "Sentiment of: 'I love Python'"},
    {"role": "assistant", "content": "Sentiment:"},   # Claude continues here
]
response = client.messages.create(model=MODEL, max_tokens=10, messages=messages)
# response.content[0].text = " positive"   (Claude appends to the pre-fill)
```

## Stop Sequences

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    stop_sequences=["</answer>"],   # stop before or at this token
    messages=[{
        "role": "user",
        "content": "Answer in XML: <answer>..."
    }],
    # Pre-fill forces the opening tag:
    # messages[-1] = {"role": "assistant", "content": "<answer>"}
)
# response.content[0].text = "Paris"   (without the closing tag)
```

## Combined Pattern: Clean JSON Extraction

```python
messages = [
    {"role": "user", "content": 'Extract name and age: "Alice is 30 years old."'},
    {"role": "assistant", "content": "{"},  # pre-fill opening brace
]
response = client.messages.create(
    model=MODEL,
    max_tokens=100,
    stop_sequences=["}"],     # stop after closing brace
    messages=messages,
)
json_str = "{" + response.content[0].text + "}"
import json
data = json.loads(json_str)  # {"name": "Alice", "age": 30}
```

## Best Practices

- Combine pre-filling + stop sequences for the most reliable structured extraction
- Keep pre-fill short — just enough to lock in the format
- Use `stop_reason == "stop_sequence"` to verify the sequence was hit

## Common Mistakes

- Using stop sequences without pre-filling (Claude may not open the expected format)
- Setting stop sequences that appear inside valid content
- Forgetting to prepend the pre-fill text when reconstructing the full output

## Exercise

Use pre-filling and stop sequences to reliably extract `{"city": "...", "country": "..."}` JSON from natural language location descriptions.
