# 07 — Prompts

## What are MCP Prompts?

Prompts are **user-controlled** primitives — triggered by user actions like slash commands or button clicks. They provide pre-written, tested instructions that MCP servers expose to clients for specialized tasks.

---

## Why Server-Defined Prompts?

Instead of users writing their own prompts (which may be suboptimal), MCP servers can provide **expert-crafted prompt templates** tailored to their domain:

- A document server provides `/format` to rewrite content in Markdown
- A code analysis server provides `/review` to perform code reviews
- A data server provides `/summarize` to generate data summaries

---

## Defining Prompts

```python
from mcp.server.fastmcp.prompts import base
from pydantic import Field

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add headers, bullet points, tables, etc as necessary.
    Use the 'edit_document' tool to edit the document.
    After editing, respond with the final version.
    """
    return [base.UserMessage(prompt)]
```

---

## Prompt Structure

A prompt function:
1. Receives **arguments** (e.g., document ID, user preferences)
2. Returns a **list of messages** in user/assistant format
3. These messages are sent directly to Claude as conversation input

```python
@mcp.prompt(name="summarize", description="Summarize a document")
def summarize_doc(
    doc_id: str = Field(description="Document to summarize"),
) -> list[base.Message]:
    return [
        base.UserMessage(
            f"Read document '{doc_id}' using the read_doc_contents tool "
            f"and provide a concise summary."
        )
    ]
```

---

## Using Prompts from Client

### Listing Available Prompts

```python
async def list_prompts(self):
    result = await self.session.list_prompts()
    return result.prompts
```

### Getting a Specific Prompt

```python
async def get_prompt(self, prompt_name: str, args: dict[str, str]):
    result = await self.session.get_prompt(prompt_name, args)
    return result.messages
```

### Arguments Flow

```
Client passes: get_prompt("format", {"doc_id": "report.pdf"})
    → Server receives: format_document(doc_id="report.pdf")
    → Server interpolates doc_id into prompt template
    → Server returns: formatted messages with "report.pdf" embedded
```

---

## Prompt Workflow Example

```
1. User types: /format report.pdf
2. Client identifies command "format" and argument "report.pdf"
3. Client calls: get_prompt("format", {"doc_id": "report.pdf"})
4. Server executes format_document("report.pdf")
5. Server returns message list with the formatting prompt
6. Client sends messages to Claude
7. Claude uses tools to read document, reformat, and save
8. Claude returns the formatted result
```

---

## Prompts vs. Tools vs. Resources

| Aspect | Tools | Resources | Prompts |
|--------|-------|-----------|---------|
| Controlled by | Model | Application | User |
| Triggered by | Claude's decision | App code | User action (slash command) |
| Purpose | Execute actions | Read data | Define workflows |
| Returns | Action result | Data | Message templates |
| Example | `edit_document()` | `docs://documents` | `/format` |

---

## Best Practices

1. **Name prompts as commands** — `format`, `summarize`, `review` (not `format_prompt`)
2. **Write expert-quality templates** — this is the whole point of server-defined prompts
3. **Include tool usage instructions** — tell Claude which tools to use in the prompt
4. **Use XML tags for structured input** — `<document_id>...</document_id>`
5. **Keep arguments minimal** — one or two parameters per prompt
6. **Provide clear descriptions** — users see these when browsing available commands

---

## Exercises

1. Create a prompt that asks Claude to generate a table of contents for a document
2. Create a prompt that asks Claude to translate a document to a specified language
3. Implement the client-side code to list and invoke prompts
