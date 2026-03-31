# 18 — Streaming with Tools

## Overview

You can stream Claude's thinking text while it calls tools. The stream yields text chunks until a tool_use block is emitted.

```python
with client.messages.stream(
    model=MODEL, max_tokens=1024,
    tools=my_tools,
    messages=messages
) as stream:
    for event in stream:
        if hasattr(event, "type"):
            if event.type == "content_block_delta":
                if hasattr(event.delta, "text"):
                    print(event.delta.text, end="", flush=True)

final = stream.get_final_message()
```

## Best Practices
- Use `stream.get_final_message()` to get the complete response after streaming
- Handle both `text` deltas and `input_json_delta` (tool argument streaming)

## Exercise
Stream a tool-using conversation and print "[THINKING]" prefix for text chunks and "[TOOL CALL]" when a tool_use block starts.
