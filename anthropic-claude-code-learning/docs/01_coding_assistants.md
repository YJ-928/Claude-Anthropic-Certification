# 01 — Coding Assistants

## What Is a Coding Assistant?

A **coding assistant** is a tool that uses language models to write code and complete development tasks. It bridges the gap between natural language instructions and executable code changes.

### Core Process

```
1. Receives task (e.g., fix a bug, add a feature)
         ↓
2. Language model gathers context (reads files, understands codebase)
         ↓
3. Formulates a plan to solve the issue
         ↓
4. Takes action (updates files, runs tests, commits changes)
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│                User Request                  │
│  "Fix the authentication bug in login.py"   │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│            Language Model (Claude)           │
│  - Understands the request                  │
│  - Decides which tools to call              │
│  - Generates tool call instructions         │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│         Tool Execution Layer                 │
│  - read_file("login.py")                    │
│  - write_file("login.py", new_content)      │
│  - run_command("pytest tests/test_login.py")│
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│   File System / Terminal / External APIs     │
└─────────────────────────────────────────────┘
```

---

## Key Limitation: Text In, Text Out

Language models only process text input and produce text output. They **cannot** directly:

- Read files from disk
- Execute shell commands
- Access databases
- Interact with browsers or APIs

This is why the **tool use system** is essential.

---

## The Tool Use System

Tool use is the method that enables language models to perform real-world actions:

1. The assistant application appends instructions to the user request
2. Instructions specify a format for requesting actions (e.g., `read file: filename`)
3. The language model responds with a formatted action request
4. The assistant application executes the actual action
5. Results are sent back to the language model
6. The model produces a final response

```python
# Simplified tool use loop
def coding_assistant_loop(user_request: str) -> str:
    messages = [{"role": "user", "content": user_request}]

    while True:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            messages=messages,
            tools=AVAILABLE_TOOLS,
        )

        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use":
            tool_call = extract_tool_call(response)
            result = execute_tool(tool_call)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": tool_call.id, "content": result}],
            })
        else:
            return extract_text(response)
```

---

## Why Claude Excels at Tool Use

| Advantage | Description |
|-----------|-------------|
| Superior tool use | Better at understanding tool functions and combining them for complex tasks |
| Extensibility | Claude Code is designed to accept new tools easily |
| Security | Direct code search rather than indexing that sends codebase to external servers |
| Adaptability | Tool use quality makes Claude adaptable to development workflow changes |

---

## Best Practices

1. **Understand the loop** — All LM-based coding assistants follow the same request → tool call → execute → respond pattern
2. **Tool quality matters** — The quality of available tools directly impacts coding assistant effectiveness
3. **Context is king** — Providing the right context (files, error messages, screenshots) dramatically improves results

---

## Exercises

1. Draw the tool use loop for a coding assistant that fixes a failing test
2. List five tools a coding assistant would need to be effective in a Python project
3. Explain why a language model cannot directly read a file from disk
