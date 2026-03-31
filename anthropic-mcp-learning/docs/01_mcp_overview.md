# 01 — MCP Overview

## What is the Model Context Protocol?

The **Model Context Protocol (MCP)** is an open standard created by Anthropic that provides a communication layer between AI models (like Claude) and external tools, data sources, and services — without requiring developers to write tedious boilerplate code.

---

## The Problem MCP Solves

### Traditional Approach

When integrating Claude with external services (e.g., GitHub, Slack, a database), developers must:

1. **Author tool schemas** — Write JSON schema definitions for every tool parameter
2. **Implement tool functions** — Write Python/JS functions that call the external API
3. **Maintain both** — Update schemas and functions whenever the API changes
4. **Repeat for every service** — Each new integration requires the same manual work

```
Developer's Application
├── Tool Schema: create_issue (JSON)
├── Tool Function: create_issue() → GitHub API
├── Tool Schema: list_repos (JSON)
├── Tool Function: list_repos() → GitHub API
├── Tool Schema: send_message (JSON)
├── Tool Function: send_message() → Slack API
└── ... (dozens more for each service)
```

This creates a significant **maintenance burden**, especially for complex services with many features.

### MCP Solution

MCP shifts tool definition and execution from the developer's application to dedicated **MCP servers**:

```
Developer's Application
├── MCP Client → GitHub MCP Server (all GitHub tools pre-built)
├── MCP Client → Slack MCP Server (all Slack tools pre-built)
└── MCP Client → Database MCP Server (all DB tools pre-built)
```

The MCP server wraps external service functionality into **pre-built tools** that your application can discover and use automatically.

---

## Core Value Proposition

| Without MCP | With MCP |
|-------------|----------|
| Developer writes every tool schema | MCP server auto-generates schemas |
| Developer implements every tool function | MCP server provides implementations |
| Developer maintains code per service | Service provider maintains MCP server |
| Complex integration per service | One client interface for all services |

---

## Who Authors MCP Servers?

Anyone can create an MCP server, but commonly:

- **Service providers** create official MCP servers (e.g., GitHub, Slack)
- **Community contributors** build servers for popular APIs
- **Developers** create custom servers for internal services

---

## MCP vs. Direct Tool Use

MCP and tool use are **complementary**, not identical:

- **Tool use** is the underlying mechanism — Claude decides to call a tool, receives results
- **MCP** is about **who does the work** of creating, packaging, and maintaining those tools

Without MCP, developers handcraft each tool. With MCP, someone else packages tools into a server, and your application connects to it via a standard protocol.

---

## Three Server Primitives

MCP servers expose three types of capabilities:

| Primitive | Controlled By | Purpose | Example |
|-----------|--------------|---------|---------|
| **Tools** | Model (Claude) | Add capabilities Claude can invoke | `read_document`, `edit_document` |
| **Resources** | Application | Expose data for the app to consume | `docs://documents`, `docs://documents/{id}` |
| **Prompts** | User | Pre-built prompt templates for workflows | `/format`, `/summarize` |

---

## Best Practices

1. **Start with existing servers** — Check if an MCP server already exists for your service
2. **Build servers for reuse** — Design servers that others can consume, not just one app
3. **Keep tools focused** — Each tool should do one thing well
4. **Use resources for read-heavy operations** — Don't use tools when a resource suffices

---

## Exercises

1. List three external services you use and describe what tools an MCP server for each might expose
2. Compare the code required to integrate a GitHub tool manually vs. through an MCP server
3. Identify which MCP primitive (tool, resource, or prompt) fits each scenario:
   - Fetching a user's profile data for display → **Resource**
   - Running a SQL query chosen by Claude → **Tool**
   - A "rewrite in formal tone" button → **Prompt**
