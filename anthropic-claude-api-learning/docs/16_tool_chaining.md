# 16 — Tool Chaining

## Overview

Claude can call multiple tools in sequence, using the result of one tool as input to the next.

```
User: "What time will it be in 2 hours and 30 minutes?"
  → Call get_current_time()     → "2024-01-15 14:00"
  → Call add_duration("2h30m")  → "2024-01-15 16:30"
  → Final answer: "It will be 4:30 PM"
```

## Pattern

The same `while True` loop handles chaining automatically — as long as Claude keeps returning `stop_reason="tool_use"`, you keep executing tools.

```python
step = 0
while True:
    response = client.messages.create(...)
    step += 1
    print(f"Step {step}: stop_reason={response.stop_reason}")
    if response.stop_reason != "tool_use":
        break
    # ... execute tools and append results
```

## Best Practices
- Add a maximum step guard to prevent infinite loops
- Log each tool call for debugging
- Test chains where one tool fails mid-sequence

## Exercise
Build a chained tool flow: (1) get_current_date → (2) add_days(n) → (3) format_date(style). Test with "What date will it be in 90 days in long format?"
