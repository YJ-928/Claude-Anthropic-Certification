# 06 — Resources

## What are MCP Resources?

Resources are **application-controlled** primitives — your application code decides when to fetch data from them. They expose data to clients for read operations, serving the app rather than the model.

---

## Resource Types

### 1. Direct (Static) Resources

A fixed URI that always returns the same type of data:

```python
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())
```

- URI: `docs://documents`
- Always returns the full list of document IDs

### 2. Templated Resources

Parameterized URIs with placeholders:

```python
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
```

- URI pattern: `docs://documents/{doc_id}`
- `{doc_id}` becomes a function keyword argument
- Each unique URI returns different data

---

## Resource Communication Flow

```
1. Client sends read_resource request with URI
2. MCP Server matches URI to resource function
3. Server executes function, serializes return value
4. Client receives data via read_resource result
```

---

## URI Patterns

Resources use URI-like addresses (similar to web routes):

| URI | Type | Description |
|-----|------|-------------|
| `docs://documents` | Static | List all documents |
| `docs://documents/{doc_id}` | Templated | Get specific document |
| `config://settings` | Static | Application configuration |
| `users://profiles/{user_id}` | Templated | User profile data |

---

## MIME Types

MIME types hint to clients how to deserialize the response:

| MIME Type | Use Case | Client Handling |
|-----------|----------|-----------------|
| `application/json` | Structured data | `json.loads(resource.text)` |
| `text/plain` | Raw text content | `resource.text` |
| `text/markdown` | Markdown documents | `resource.text` |
| `text/html` | HTML content | `resource.text` |

---

## Reading Resources from Client

```python
from pydantic import AnyUrl
import json

async def read_resource(self, uri: str):
    result = await self.session.read_resource(AnyUrl(uri))
    resource = result.contents[0]

    if resource.mimeType == "application/json":
        return json.loads(resource.text)
    return resource.text
```

---

## Resources vs. Tools

| Aspect | Resources | Tools |
|--------|-----------|-------|
| Controlled by | Application | Model (Claude) |
| Purpose | Read data | Perform actions |
| Triggered by | App code explicitly | Claude's decision |
| Direction | Data retrieval | Action execution |
| Example | List documents | Edit a document |

**Rule of thumb**: If you're reading data to display or augment context → Resource. If Claude needs to perform an action → Tool.

---

## Auto-Serialization

The Python MCP SDK **automatically serializes** return values to strings:

```python
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())  # Python list → JSON string automatically
```

---

## Best Practices

1. **One resource per distinct read operation** — don't combine list + fetch in one
2. **Set appropriate MIME types** — helps clients deserialize correctly
3. **Use static resources for collections** — `docs://documents` for lists
4. **Use templated resources for individual items** — `docs://documents/{id}`
5. **Validate existence in templated resources** — raise `ValueError` for missing items
6. **Use resources for read-heavy data** — avoid tools for pure data retrieval

---

## Exercises

1. Create a static resource that returns server health/status information
2. Create a templated resource for fetching user profiles by ID
3. Write client code that reads a resource and parses the JSON response
