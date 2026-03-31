# 02 — Claude Code Architecture

## Overview

Claude Code is Anthropic's AI-powered coding assistant that runs in your terminal. It combines Claude's language understanding with a tool execution layer to perform real development tasks — reading files, writing code, running commands, and interacting with version control.

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        Claude Code CLI                         │
│                                                                │
│  ┌──────────┐   ┌──────────────┐   ┌───────────────────────┐ │
│  │  User     │──→│  Conversation│──→│  Claude API           │ │
│  │  Input    │   │  Manager     │   │  (Language Model)     │ │
│  └──────────┘   └──────────────┘   └───────────┬───────────┘ │
│                                                  │             │
│                                     ┌────────────↓──────────┐ │
│                                     │  Tool Call Router     │ │
│                                     └────────────┬──────────┘ │
│                       ┌──────────────┬───────────┼──────────┐ │
│                       ↓              ↓           ↓          ↓ │
│                 ┌──────────┐  ┌──────────┐ ┌─────────┐ ┌────┐│
│                 │read_file │  │write_file│ │run_cmd  │ │grep││
│                 └──────────┘  └──────────┘ └─────────┘ └────┘│
│                       │              │           │          │ │
│                       ↓              ↓           ↓          ↓ │
│                 ┌──────────────────────────────────────────┐  │
│                 │        File System / Terminal             │  │
│                 └──────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌────────────┐ │
│  │ Hooks    │  │ Commands │  │ MCP Servers│  │ Git Layer  │ │
│  └──────────┘  └──────────┘  └────────────┘  └────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Conversation Manager

Maintains the multi-turn conversation between user and Claude. Manages:

- Message history
- Context injection (Claude.md files, @file mentions)
- Conversation compaction and clearing

### 2. Claude API Layer

Sends messages to the Claude language model via the Anthropic API. Handles:

- System prompt construction
- Tool definitions
- Streaming responses
- Token budget management

### 3. Tool Call Router

When Claude's response includes a `tool_use` block, the router:

1. Identifies the requested tool
2. Checks permissions and hooks
3. Dispatches to the appropriate executor
4. Returns results back to the conversation

### 4. Default Tools

| Tool | Description |
|------|-------------|
| `read` | Read file contents |
| `write` | Create or overwrite files |
| `edit` | Make targeted edits to existing files |
| `bash` | Execute shell commands |
| `grep` | Search file contents with patterns |
| `glob` | Find files matching patterns |
| `ls` | List directory contents |

### 5. Extension Points

- **Hooks** — Pre/post-tool scripts that intercept tool calls
- **Custom Commands** — User-defined slash commands
- **MCP Servers** — External tool providers
- **GitHub Actions** — CI/CD integration

---

## Execution Flow

```
User types request in terminal
         ↓
Claude Code constructs message with context
         ↓
Message sent to Claude API
         ↓
Claude responds with text and/or tool_use blocks
         ↓
For each tool_use block:
  ├── Run pre-tool-use hooks
  │     ├── exit 0 → proceed
  │     └── exit 2 → block, send error to Claude
  ├── Execute tool
  ├── Run post-tool-use hooks
  └── Collect result
         ↓
Tool results sent back to Claude
         ↓
Claude generates next response (may include more tool calls)
         ↓
Loop until Claude produces final text response
         ↓
Display result to user
```

---

## Real-World Demos

### Performance Optimization

Claude analyzed the Chalk JavaScript library (5th most downloaded JS package with 429M weekly downloads):
- Used benchmarks and profiling tools
- Created structured todo lists
- Identified bottlenecks
- Implemented fixes
- **Result: 3.9× throughput improvement**

### Data Analysis

Claude performed churn analysis on video streaming platform CSV data:
- Used Jupyter notebooks
- Executed code cells iteratively
- Viewed results and adjusted analysis
- Customized successive analyses based on findings

---

## Best Practices

1. **Trust the tool loop** — Let Claude iterate through read → plan → write → test cycles
2. **Provide context** — Use Claude.md files and @file mentions to give Claude the right information
3. **Use planning mode** — For complex multi-file changes, enable plan mode for better results
4. **Review changes** — Always review Claude's changes before committing

---

## Exercises

1. Trace the execution flow when a user asks Claude Code to "add input validation to the login function"
2. Identify which tools Claude would need to use for a task that involves reading a config file, modifying it, and running tests
3. Explain the role of the Tool Call Router in the architecture
