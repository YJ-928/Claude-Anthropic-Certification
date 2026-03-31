# 04 — MCP Servers

## What is an MCP Server?

An MCP Server is a standalone process that **defines and exposes tools, resources, and prompts** to MCP clients. It wraps external service functionality into pre-built capabilities that applications can discover and use automatically.

---

## Server Components

```
MCP Server
├── Tools      → Functions Claude can invoke (model-controlled)
├── Resources  → Data endpoints the app can read (app-controlled)
└── Prompts    → Template workflows users can trigger (user-controlled)
```

---

## Creating a Server with FastMCP

The Python MCP SDK provides `FastMCP` for rapid server creation:

```python
from mcp.server.fastmcp import FastMCP

# Create server with a name
mcp = FastMCP("MyServer", log_level="ERROR")

# Define tools, resources, prompts using decorators
# ... (see docs 05-07)

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

That's it — a single line to create the server instance, decorators to add capabilities, and one line to run.

---

## FastMCP Benefits

| Feature | Manual Approach | FastMCP |
|---------|----------------|---------|
| Tool schemas | Write JSON by hand | Auto-generated from type hints |
| Parameter validation | Manual checks | Pydantic validation |
| Server setup | Boilerplate code | Single `FastMCP()` call |
| Transport config | Manual protocol handling | `mcp.run(transport="stdio")` |

---

## Server Architecture Pattern

```python
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")

# In-memory data store
docs = {
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "plan.md": "The plan outlines the steps for implementation.",
}

# Tools
@mcp.tool(name="read_doc", description="Read document contents")
def read_doc(doc_id: str = Field(description="Document ID")):
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    return docs[doc_id]

# Resources
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())

# Prompts
@mcp.prompt(name="summarize", description="Summarize a document")
def summarize(doc_id: str = Field(description="Document ID")):
    from mcp.server.fastmcp.prompts import base
    return [base.UserMessage(f"Summarize the document: {doc_id}")]

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## Real-World MCP Servers

In production, MCP servers typically:

- Wrap a specific external API (GitHub, Slack, Jira)
- Are authored by the service provider or community
- Run as separate processes alongside your application
- Can be shared across many applications

---

## Server vs. Client: Who Builds What?

| Scenario | You Build |
|----------|-----------|
| Integrating an existing service | **Client only** — use existing MCP server |
| Wrapping your internal API | **Server only** — others connect via clients |
| Learning / prototyping | **Both** — build server and client together |

---

## Best Practices

1. **Name servers descriptively** — `FastMCP("GitHubMCP")` not `FastMCP("Server")`
2. **Set log_level="ERROR"** for production — reduce noise in stdio transport
3. **Validate inputs in tools** — raise `ValueError` for bad inputs
4. **Keep servers focused** — one server per service/domain
5. **Use type hints everywhere** — FastMCP generates schemas from them

---

## Exercises

1. Create a minimal MCP server with one tool that returns the current time
2. Add a resource that lists available timezone names
3. Test your server with `mcp dev server.py`
