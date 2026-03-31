# 12 — MCP Best Practices

## Server Design

### 1. Single Responsibility

Each MCP server should wrap **one service or domain**:

```
✅ GitHubMCP — wraps GitHub API
✅ SlackMCP — wraps Slack API
✅ DocumentMCP — wraps document operations

❌ EverythingMCP — wraps GitHub + Slack + documents
```

### 2. Descriptive Naming

```python
# Good
mcp = FastMCP("DocumentMCP")
@mcp.tool(name="read_doc_contents", description="Read the contents of a document")

# Bad
mcp = FastMCP("Server")
@mcp.tool(name="read", description="Reads stuff")
```

### 3. Input Validation

Always validate inputs before performing operations:

```python
@mcp.tool(name="edit_document", description="Edit a document")
def edit_document(
    doc_id: str = Field(description="Document ID"),
    old_str: str = Field(description="Text to find"),
    new_str: str = Field(description="Replacement text"),
):
    # Validate document exists
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")

    # Validate old string exists in document
    if old_str not in docs[doc_id]:
        raise ValueError(f"Text '{old_str}' not found in document '{doc_id}'")

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Updated '{doc_id}' successfully"
```

---

## Client Design

### 4. Context Manager Pattern

Always use async context managers for cleanup:

```python
# Good
async with MCPClient(command="python", args=["server.py"]) as client:
    tools = await client.list_tools()

# Bad — cleanup might not happen on exception
client = MCPClient(command="python", args=["server.py"])
await client.connect()
tools = await client.list_tools()
# What if an exception occurs here? cleanup() never called
```

### 5. Error Handling in Tool Execution

Return errors to Claude rather than crashing:

```python
try:
    result = await client.call_tool(tool_name, tool_input)
    content = json.dumps([item.text for item in result.content])
    return {"tool_use_id": tool_id, "type": "tool_result", "content": content}
except Exception as e:
    return {
        "tool_use_id": tool_id,
        "type": "tool_result",
        "content": json.dumps({"error": str(e)}),
        "is_error": True,
    }
```

---

## Tool Design

### 6. Clear Descriptions

Claude uses tool descriptions to decide when to call them. Be specific:

```python
# Good — Claude knows exactly when to use this
@mcp.tool(
    name="edit_document",
    description="Edit a document by finding and replacing an exact string. "
                "The old_str must match exactly, including whitespace."
)

# Bad — vague, Claude might misuse it
@mcp.tool(name="edit", description="Edits things")
```

### 7. Field Descriptions

Every parameter should have a description:

```python
@mcp.tool(name="search_docs", description="Search documents by keyword")
def search(
    query: str = Field(description="Keyword or phrase to search for"),
    max_results: int = Field(description="Max number of results to return", default=10),
):
    ...
```

### 8. Return Meaningful Results

```python
# Good
return f"Document '{doc_id}' updated: replaced '{old_str}' with '{new_str}'"

# Bad
return "OK"
```

---

## Resource Design

### 9. Use Appropriate MIME Types

```python
# Structured data → application/json
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]: ...

# Plain text → text/plain
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str: ...
```

### 10. Separate List and Detail Resources

```python
# List endpoint
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())

# Detail endpoint
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    return docs[doc_id]
```

---

## Prompt Design

### 11. Expert-Quality Templates

Prompts should be well-tested and optimized:

```python
@mcp.prompt(name="format", description="Rewrite document in Markdown")
def format_document(doc_id: str = Field(description="Document to format")):
    return [base.UserMessage(
        f"Reformat document '{doc_id}' using markdown syntax. "
        f"Use read_doc_contents to read it, then edit_document to save. "
        f"Add headers, bullet points, and tables as appropriate. "
        f"Don't change the meaning. Respond with the final version."
    )]
```

### 12. Include Tool Instructions

Tell Claude which tools to use in prompt templates:

```python
# Good — tells Claude what tools to use
"Use the 'edit_document' tool to save your changes."

# Bad — Claude has to guess
"Save the reformatted text."
```

---

## Architecture

### 13. Choose the Right Primitive

| Need | Primitive | Why |
|------|-----------|-----|
| Claude should perform an action | **Tool** | Model-controlled |
| App needs to display data | **Resource** | App-controlled |
| User triggers a workflow | **Prompt** | User-controlled |

### 14. Don't Use Tools for Read-Only Data

```python
# Bad — using a tool for data the app should control
@mcp.tool(name="list_documents", description="List all documents")
def list_docs():
    return list(docs.keys())

# Good — use a resource instead
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())
```

### 15. Test with Inspector Before Connecting Clients

Always verify server functionality with `mcp dev server.py` before writing client code.

---

## Summary Checklist

- [ ] Server has a descriptive name
- [ ] All tools have clear names and descriptions
- [ ] All parameters use `Field(description=...)`
- [ ] Inputs are validated before operations
- [ ] Errors are returned to Claude, not swallowed
- [ ] Resources use correct MIME types
- [ ] Prompts include tool usage instructions
- [ ] Client uses context managers for cleanup
- [ ] Server tested with inspector
- [ ] Multi-tool responses handled correctly
