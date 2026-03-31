# 05 — Tools

## What are MCP Tools?

Tools are **model-controlled** primitives — Claude decides when to execute them during a conversation. They add capabilities that Claude can invoke to perform actions in the real world.

---

## Tool Lifecycle

```
1. Client sends list_tools request → Server returns tool schemas
2. Application sends tool schemas to Claude
3. Claude decides to use a tool → returns tool_use block
4. Client sends call_tool request → Server executes the function
5. Server returns result → Application sends result back to Claude
6. Claude uses result to formulate response
```

---

## Defining Tools with FastMCP

### Basic Tool

```python
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("MyServer")

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
```

### What FastMCP Does Automatically

The `@mcp.tool` decorator:
1. **Generates JSON schema** from the function signature and type hints
2. **Extracts parameter descriptions** from `Field()` annotations
3. **Registers the tool** in the server's tool list
4. **Handles serialization** of inputs and outputs

The generated schema for the tool above looks like:

```json
{
  "name": "read_doc_contents",
  "description": "Read the contents of a document and return it as a string.",
  "input_schema": {
    "type": "object",
    "properties": {
      "doc_id": {
        "type": "string",
        "description": "Id of the document to read"
      }
    },
    "required": ["doc_id"]
  }
}
```

---

## Tool with Multiple Parameters

```python
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string with a new string",
)
def edit_document(
    doc_id: str = Field(description="Id of the document to edit"),
    old_str: str = Field(description="The text to replace. Must match exactly"),
    new_str: str = Field(description="The new text to insert"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Document {doc_id} updated successfully"
```

---

## Parameter Types

FastMCP supports standard Python types:

```python
@mcp.tool(name="search", description="Search documents")
def search(
    query: str = Field(description="Search query"),
    max_results: int = Field(description="Maximum results", default=10),
    include_archived: bool = Field(description="Include archived docs", default=False),
):
    ...
```

---

## Error Handling Pattern

```python
@mcp.tool(name="delete_doc", description="Delete a document")
def delete_doc(doc_id: str = Field(description="Document to delete")):
    # Validate existence
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")

    # Validate permissions (example)
    if doc_id.startswith("protected_"):
        raise ValueError(f"Cannot delete protected document '{doc_id}'")

    del docs[doc_id]
    return f"Document '{doc_id}' deleted"
```

---

## Implementation Pattern

```
@mcp.tool decorator
    → Function definition with typed parameters
        → Field() descriptions for each parameter
            → Input validation
                → Core logic
                    → Return result
```

---

## Best Practices

1. **Use descriptive names** — `read_doc_contents` not `read` or `get_data`
2. **Write clear descriptions** — Claude uses these to decide when to call the tool
3. **Always use `Field(description=...)`** — Helps Claude understand each parameter
4. **Validate inputs first** — Check existence, permissions before acting
5. **Return meaningful results** — Include success messages, not just side effects
6. **Raise `ValueError` for bad inputs** — MCP handles this as an error response

---

## Exercises

1. Create a tool that adds a new document to the in-memory store
2. Create a tool that searches documents by keyword
3. Create a tool that returns word count statistics for a document
