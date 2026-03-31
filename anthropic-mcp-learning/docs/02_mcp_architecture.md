# 02 — MCP Architecture

## High-Level Architecture

MCP follows a **client-server** architecture where your application communicates with external services through a standardized protocol layer.

```
┌──────────┐
│   User   │
└────┬─────┘
     │  (query)
     ▼
┌──────────────────┐
│ Application      │
│ Server           │
│ (your code)      │
└────┬─────────────┘
     │  (list_tools / call_tool)
     ▼
┌──────────────────┐
│ MCP Client       │
│ (SDK-provided)   │
└────┬─────────────┘
     │  (MCP protocol messages)
     ▼
┌──────────────────┐
│ MCP Server       │
│ (tools/resources │
│  /prompts)       │
└────┬─────────────┘
     │  (API calls, DB queries, etc.)
     ▼
┌──────────────────┐
│ External Services│
│ (GitHub, Slack,  │
│  databases, etc.)│
└──────────────────┘
```

---

## Component Breakdown

### 1. Application Server (Your Code)

Your code that:
- Receives user queries
- Sends queries + tool schemas to Claude
- Processes Claude's tool use requests
- Returns final responses to users

### 2. MCP Client

A **communication interface** between your application and the MCP server:
- **Transport agnostic** — can communicate via `stdin/stdout`, HTTP, WebSockets
- **Does not execute tools** — only facilitates communication
- Handles connection lifecycle (connect, initialize, cleanup)

### 3. MCP Server

A standalone process that:
- Defines and exposes tools, resources, and prompts
- Executes tool calls against external services
- Returns results back through the protocol

### 4. External Services

The actual APIs, databases, or systems the MCP server wraps.

---

## Communication Flow

```
User: "What issues are open in my repo?"
  │
  ▼
Application Server
  │
  ├─► MCP Client.list_tools()
  │     │
  │     ├─► MCP Server: "list_tools" request
  │     │◄── MCP Server: tools = [list_issues, create_issue, ...]
  │     │
  │◄────┘ tools available
  │
  ├─► Claude API: query + tool schemas
  │◄── Claude: "call list_issues(repo='my-repo', state='open')"
  │
  ├─► MCP Client.call_tool("list_issues", {...})
  │     │
  │     ├─► MCP Server: "call_tool" request
  │     │     │
  │     │     ├─► GitHub API: GET /repos/my-repo/issues?state=open
  │     │     │◄── GitHub: [issue1, issue2, ...]
  │     │     │
  │     │◄── MCP Server: tool result
  │     │
  │◄────┘ result
  │
  ├─► Claude API: query + tool result
  │◄── Claude: "You have 3 open issues: ..."
  │
  ▼
User: "You have 3 open issues: ..."
```

---

## Transport Mechanisms

MCP is **transport agnostic**. The client and server can communicate via:

| Transport | Use Case | Setup |
|-----------|----------|-------|
| **stdio** (stdin/stdout) | Both processes on same machine | Most common for local dev |
| **HTTP + SSE** | Client and server on different machines | Production deployments |
| **WebSockets** | Real-time bidirectional communication | Advanced use cases |

Common local setup: both client and server run on the same machine, communicating via `stdin/stdout`.

---

## Key Message Types

The MCP specification defines structured message types:

| Message | Direction | Purpose |
|---------|-----------|---------|
| `list_tools` request | Client → Server | Ask for available tools |
| `list_tools` result | Server → Client | Return tool schemas |
| `call_tool` request | Client → Server | Execute a tool with arguments |
| `call_tool` result | Server → Client | Return tool execution result |
| `list_resources` request | Client → Server | Ask for available resources |
| `read_resource` request | Client → Server | Fetch a specific resource |
| `list_prompts` request | Client → Server | Ask for available prompts |
| `get_prompt` request | Client → Server | Fetch a specific prompt template |

---

## Multiple Server Connections

An application can connect to **multiple MCP servers** simultaneously:

```
Application Server
├── MCP Client A → GitHub MCP Server
├── MCP Client B → Slack MCP Server
└── MCP Client C → Custom Document MCP Server
```

Tools from all servers are aggregated and sent to Claude together.

---

## Best Practices

1. **Use stdio for local development** — simplest setup, no network config needed
2. **One client per server** — each MCP server gets its own client connection
3. **Handle cleanup properly** — always close client sessions when shutting down
4. **Aggregate tools across clients** — send all available tools to Claude for maximum capability

---

## Exercises

1. Draw the message flow for a user asking Claude to "create a new GitHub issue titled Bug Report"
2. Explain why the MCP client does not execute tools itself
3. Describe a scenario where you would connect to three different MCP servers from one application
