# 09 — Structured Outputs

## Overview

Structured outputs turn Claude's free-form text into reliable data structures (JSON, dicts) that your code can consume directly.

```
Approach 1: Pre-fill + stop sequence   → lightweight, no tool overhead
Approach 2: Tool use with tool_choice  → most reliable, schema-validated
Approach 3: Prompt instruction only    → fragile, not recommended
```

## Approach 1 — Pre-fill + Stop Sequence

```python
def extract_json(prompt: str, schema_example: str) -> dict:
    messages = [
        {"role": "user",      "content": prompt},
        {"role": "assistant", "content": "{"},
    ]
    response = client.messages.create(
        model=MODEL, max_tokens=256,
        stop_sequences=["}"],
        messages=messages,
    )
    return json.loads("{" + response.content[0].text + "}")
```

## Approach 2 — Forced Tool Use (Recommended)

```python
import json

extract_tool = {
    "name": "extract_invoice",
    "description": "Extract structured invoice data",
    "input_schema": {
        "type": "object",
        "properties": {
            "vendor":   {"type": "string"},
            "amount":   {"type": "number"},
            "due_date": {"type": "string"},
        },
        "required": ["vendor", "amount"],
    },
}

response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    tools=[extract_tool],
    tool_choice={"type": "tool", "name": "extract_invoice"},  # force this tool
    messages=[{"role": "user", "content": "Invoice from Acme Corp, $450, due 2024-03-15"}],
)

data = response.content[0].input   # already a dict — no json.loads needed
print(data["vendor"])   # "Acme Corp"
print(data["amount"])   # 450.0
```

## Best Practices

- Use forced tool use (`tool_choice`) when you need schema guarantees
- Use pre-fill + stop for lightweight extraction of simple values
- Always have a fallback in case parsing fails

## Common Mistakes

- Calling `json.loads()` on `response.content[0].input` — it's already a dict
- Trusting prompt-only JSON output without validation
- Not specifying `"required"` fields in the tool schema (they can be omitted by Claude)

## Exercise

Build a function `extract_meeting(text)` that uses forced tool use to extract `{"title", "date", "attendees": [...], "location"}` from a natural language meeting description.
