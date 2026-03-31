# 11 — MCP CLI Chatbot Project

## Overview

This project combines an MCP server, MCP client, and the Anthropic API into a **CLI chatbot** where:

1. User types a message
2. Claude receives the message along with available MCP tool schemas
3. Claude decides whether to call tools
4. The client executes tool calls on the MCP server
5. Results flow back to Claude for a final response

---

## Architecture

```
┌──────────────┐
│  User (CLI)  │
└──────┬───────┘
       │ input
       ▼
┌──────────────────────────────────┐
│  Conversation Runner             │
│  (agentic loop)                  │
│                                  │
│  1. Collect user input           │
│  2. Send to Claude + tool schemas│
│  3. If tool_use → execute tool   │
│  4. Send result back to Claude   │
│  5. Repeat until text response   │
│  6. Print response               │
└──────┬───────────────────────────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│ Anthropic    │   │ MCP Client   │
│ API (Claude) │   └──────┬───────┘
└──────────────┘          │
                          ▼
                   ┌──────────────┐
                   │ MCP Server   │
                   │ (tools,      │
                   │  resources,  │
                   │  prompts)    │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Document     │
                   │ Store        │
                   └──────────────┘
```

---

## Project Structure

```
cli_chatbot/
├── main.py                  # Entry point — starts server, client, and chat loop
├── config.py                # Environment configuration
└── conversation_runner.py   # Agentic conversation loop
```

---

## The Agentic Loop

The core of the chatbot is an **agentic loop** that continues until Claude provides a text response:

```python
async def run(self, user_message: str) -> str:
    self.messages.append({"role": "user", "content": user_message})

    while True:
        # Send to Claude with available tools
        response = self.claude.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=self.messages,
            tools=self.tool_schemas,
        )

        # Add Claude's response to history
        self.messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            # Execute tool calls and continue loop
            tool_results = await self._execute_tools(response)
            self.messages.append({"role": "user", "content": tool_results})
        else:
            # Text response — return to user
            return self._extract_text(response)
```

---

## Tool Execution Flow

```python
async def _execute_tools(self, response) -> list:
    results = []
    for block in response.content:
        if block.type == "tool_use":
            # Find which client has this tool
            client = await self._find_client(block.name)
            # Execute on MCP server
            result = await client.call_tool(block.name, block.input)
            # Format result for Claude
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps([item.text for item in result.content]),
            })
    return results
```

---

## Running the Chatbot

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python projects/cli_chatbot/main.py
```

### Example Session

```
You: What documents are available?
Claude: I'll check the available documents for you.
       The following documents are available:
       - report.pdf
       - plan.md
       - spec.txt

You: What's in the report?
Claude: The report details the state of a 20m condenser tower.

You: Rewrite the report in markdown format
Claude: I'll reformat that document for you...
       # Condenser Tower Report
       ## Overview
       The report details the state of a **20m condenser tower**.

You: quit
Goodbye!
```

---

## Key Implementation Details

### Tool Schema Aggregation

```python
# Collect tools from all connected MCP clients
tools = []
for client in clients.values():
    mcp_tools = await client.list_tools()
    tools.extend([
        {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
        for t in mcp_tools
    ])
```

### Multi-Client Tool Routing

When multiple MCP servers are connected, find the right client for each tool:

```python
async def _find_client(self, tool_name: str) -> MCPClient:
    for client in self.clients.values():
        tools = await client.list_tools()
        if any(t.name == tool_name for t in tools):
            return client
    raise ValueError(f"No client has tool '{tool_name}'")
```

---

## Best Practices

1. **Keep the agentic loop clean** — extract tool execution into a helper
2. **Handle errors gracefully** — return tool errors to Claude as `is_error: true`
3. **Log tool calls** — print when Claude calls a tool so the user sees progress
4. **Support quit/exit** — check for termination commands in the loop
5. **Use async context managers** — ensure cleanup of all MCP clients

---

## Exercises

1. Add support for the `/format` slash command in the chatbot
2. Add `@document_name` resource mentions that auto-include document content
3. Connect a second MCP server (e.g., a calculator) alongside the document server
