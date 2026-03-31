# 10 — MCP Server Implementation

## Overview

This document covers building a complete MCP server with tools, resources, and prompts using the FastMCP Python SDK.

---

## Complete Server Implementation

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

# Create the server
mcp = FastMCP("DocumentMCP", log_level="ERROR")

# In-memory document store
docs = {
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "plan.md": "The plan outlines the steps for implementation.",
    "spec.txt": "Technical requirements for the equipment.",
}

# ─── Tools ────────────────────────────────────────────────

@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="Id of the document to read"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string with a new string.",
)
def edit_document(
    doc_id: str = Field(description="Id of the document to edit"),
    old_str: str = Field(description="Text to replace (must match exactly)"),
    new_str: str = Field(description="New text to insert"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Document '{doc_id}' updated successfully"


# ─── Resources ────────────────────────────────────────────

@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# ─── Prompts ──────────────────────────────────────────────

@mcp.prompt(
    name="format",
    description="Rewrites document contents in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    return [base.UserMessage(
        f"Reformat document '{doc_id}' using markdown syntax. "
        f"Use the read_doc_contents tool to read it, then edit_document to save. "
        f"Add headers, bullet points, and tables as appropriate."
    )]


# ─── Entry Point ──────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## Pattern: Separating Concerns

For larger servers, split into modules:

```
mcp_document_server/
├── server.py       # FastMCP instance + entry point
├── documents.py    # Data store
├── tools.py        # Tool definitions
├── resources.py    # Resource definitions
└── prompts.py      # Prompt definitions
```

### documents.py — Data Store

```python
docs: dict[str, str] = {
    "report.pdf": "The report details...",
}

def get_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]

def update_doc(doc_id: str, old_str: str, new_str: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return docs[doc_id]
```

### tools.py — Tool Definitions

```python
from pydantic import Field
from .documents import docs, get_doc, update_doc

def register_tools(mcp):
    @mcp.tool(name="read_doc_contents", description="Read document contents")
    def read_doc(doc_id: str = Field(description="Document ID")):
        return get_doc(doc_id)

    @mcp.tool(name="edit_document", description="Edit document via find/replace")
    def edit_doc(
        doc_id: str = Field(description="Document ID"),
        old_str: str = Field(description="Text to find"),
        new_str: str = Field(description="Replacement text"),
    ):
        update_doc(doc_id, old_str, new_str)
        return f"Document '{doc_id}' updated"
```

---

## Testing with the Inspector

```bash
# Test your server interactively
mcp dev server.py

# The inspector opens at http://localhost:5173
# Test each tool, resource, and prompt manually
```

---

## Schema Auto-Generation

FastMCP generates JSON schemas from your Python function signatures:

| Python Type | JSON Schema |
|-------------|-------------|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `list[str]` | `{"type": "array", "items": {"type": "string"}}` |

---

## Best Practices

1. **Separate data from tools** — keep the data store in its own module
2. **Validate all inputs** — check existence before operating
3. **Return descriptive messages** — include what changed, not just "success"
4. **Set `log_level="ERROR"`** — keeps stdio transport clean
5. **Test with inspector first** — before connecting any client

---

## Exercises

1. Add a `create_document` tool that adds new documents to the store
2. Add a `delete_document` tool with confirmation logic
3. Add a resource that returns document metadata (word count, etc.)
