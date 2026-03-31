# 14 — MCP Server Extensions

## What Are MCP Servers?

MCP (Model Context Protocol) servers are external tool providers that extend Claude Code's capabilities. They run locally or remotely and give Claude access to tools beyond the built-in set — browsers, databases, APIs, and more.

---

## How MCP Servers Work

```
┌─────────────────────────────────────────┐
│            Claude Code                   │
│                                         │
│  Built-in tools:                        │
│  read, write, edit, bash, grep, ...     │
│                                         │
│  + MCP Server tools:                    │
│  ┌───────────────────────────────┐      │
│  │ Playwright: navigate, click,  │      │
│  │   screenshot, fill, ...       │      │
│  └───────────────────────────────┘      │
│  ┌───────────────────────────────┐      │
│  │ Database: query, insert,      │      │
│  │   update, schema, ...         │      │
│  └───────────────────────────────┘      │
│  ┌───────────────────────────────┐      │
│  │ Custom: your-tool-1,          │      │
│  │   your-tool-2, ...            │      │
│  └───────────────────────────────┘      │
└─────────────────────────────────────────┘
```

---

## Installing MCP Servers

### CLI Installation

```bash
claude mcp add <name> <start-command>
```

### Example: Playwright (Browser Automation)

```bash
claude mcp add playwright npx @anthropic/mcp-playwright
```

This registers the Playwright MCP server with Claude Code. The server starts automatically when Claude needs its tools.

---

## Permission Management

When Claude first uses an MCP tool, it requires approval. To auto-approve:

**`.claude/settings.local.json`**:

```json
{
  "permissions": {
    "allow": [
      "MCP__playwright__navigate",
      "MCP__playwright__screenshot",
      "MCP__playwright__click",
      "MCP__playwright__fill"
    ]
  }
}
```

Or use the broader pattern:

```json
{
  "permissions": {
    "allow": [
      "MCP__playwright"
    ]
  }
}
```

---

## Playwright MCP Server — Practical Example

### Setup

```bash
# Install the Playwright MCP server
claude mcp add playwright npx @anthropic/mcp-playwright
```

### Usage

```
> Navigate to localhost:3000, take a screenshot, and check if
> the login form is rendered correctly.
```

Claude will:
1. Use `MCP__playwright__navigate` to open the page
2. Use `MCP__playwright__screenshot` to capture the render
3. Analyze the screenshot
4. Report findings

### Automated UI Refinement

```
> Generate a card component, then open it in the browser.
> Take a screenshot and improve the styling based on what you see.
> Repeat until the design looks professional.

Claude iterates:
1. Generate component code
2. Navigate to localhost
3. Screenshot the result
4. Analyze visual quality
5. Update code to improve styling
6. Repeat until satisfied
```

---

## Common MCP Servers

| Server | Purpose | Install Command |
|--------|---------|-----------------|
| Playwright | Browser automation | `claude mcp add playwright npx @anthropic/mcp-playwright` |
| PostgreSQL | Database access | `claude mcp add postgres npx @anthropic/mcp-postgres` |
| Filesystem | Extended file ops | `claude mcp add fs npx @anthropic/mcp-filesystem` |
| GitHub | GitHub API access | `claude mcp add github npx @anthropic/mcp-github` |

---

## Building Custom MCP Servers

You can create your own MCP server to expose custom tools to Claude Code:

```python
# Example: Simple custom MCP server (conceptual)
from mcp.server import Server

server = Server("my-custom-tools")

@server.tool("check_api_health")
async def check_api_health(url: str) -> str:
    """Check if an API endpoint is healthy."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return f"Status: {response.status_code}"

@server.tool("query_database")
async def query_database(sql: str) -> str:
    """Execute a read-only SQL query."""
    # ... database logic ...
    return results
```

---

## Key Principle

> Claude Code is a flexible assistant that grows with your team's needs through **tool expansion** rather than fixed functionality.

MCP servers are the primary mechanism for this expansion. Instead of waiting for Anthropic to add features, you can add any capability via MCP.

---

## Best Practices

1. **Start with official servers** — Playwright and GitHub are well-tested
2. **Limit permissions** — Only approve the tools Claude actually needs
3. **Use local servers for security** — Run MCP servers locally to avoid sending data externally
4. **Test tools individually** — Verify each MCP tool works before building workflows
5. **Document custom servers** — If you build custom MCP servers, document them in Claude.md

---

## Exercises

1. Install the Playwright MCP server and have Claude navigate to a website
2. Document the tools available from an MCP server you've installed
3. Design a custom MCP server that would be useful for your project
4. Configure auto-approve permissions for a specific MCP server
