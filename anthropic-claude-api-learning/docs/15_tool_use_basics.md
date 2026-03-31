# 15 — Tool Use Basics

## Overview

Tool use lets Claude call external functions — databases, APIs, calculators — and incorporate the results into its response.

```
User message
     │
     ▼
Claude decides to call a tool  → stop_reason = "tool_use"
     │
     ▼
Your code executes the tool    → returns result string
     │
     ▼
Send tool_result back to Claude
     │
     ▼
Claude generates final answer  → stop_reason = "end_turn"
```

## Tool Schema

```python
get_weather_tool = {
    "name": "get_weather",
    "description": "Returns current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
        },
        "required": ["city"],
    },
}
```

## Tool Dispatcher Pattern

```python
def run_tool(name: str, input_: dict) -> str:
    if name == "get_weather":
        return get_weather(**input_)
    raise ValueError(f"Unknown tool: {name}")

def run_conversation(user_input: str, tools: list) -> str:
    messages = [{"role": "user", "content": user_input}]
    while True:
        response = client.messages.create(
            model=MODEL, max_tokens=1024,
            tools=tools, messages=messages
        )
        if response.stop_reason != "tool_use":
            return response.content[0].text
        # Execute all tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
```

## Best Practices
- Write clear, specific tool descriptions — Claude picks tools based on descriptions
- Always handle `stop_reason != "tool_use"` as the exit condition
- Return informative error strings from tools rather than raising exceptions

## Exercise
Build a `calculator` tool with `add`, `subtract`, `multiply`, `divide` operations. Test it with: "What is (42 + 8) * 3?"
