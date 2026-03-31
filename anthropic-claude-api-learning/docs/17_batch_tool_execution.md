# 17 — Batch Tool Execution

## Overview

A "batch tool" lets Claude call multiple sub-tools in a single tool_use block, reducing round-trips.

```python
batch_tool = {
    "name": "run_batch",
    "description": "Execute multiple tool calls in parallel",
    "input_schema": {
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string"},
                        "arguments": {"type": "object"},
                    },
                    "required": ["tool_name", "arguments"],
                },
            }
        },
        "required": ["invocations"],
    },
}

def run_batch(invocations: list) -> list:
    return [
        {"tool": inv["tool_name"], "result": run_tool(inv["tool_name"], inv["arguments"])}
        for inv in invocations
    ]
```

## Best Practices
- Use batch tools when Claude needs to gather multiple independent pieces of information
- Return results as a list so Claude can match them back to inputs

## Exercise
Implement a batch tool that can fetch weather for multiple cities simultaneously. Ask Claude "What's the weather in London, Tokyo, and New York?"
