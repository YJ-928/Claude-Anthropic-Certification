"""
Exercise 03 — Document Edit Tool

Demonstrates:
- Editing documents via find-and-replace
- Multi-parameter tool definitions
- Input validation (document exists, text found)
- Confirming changes in return value

Run with the MCP Inspector:
    mcp dev exercises/exercise_03_document_edit_tool.py
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentEditServer", log_level="ERROR")

# ─── In-memory document store ─────────────────────────────

docs: dict[str, str] = {
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "plan.md": "The plan outlines the steps for implementation.",
    "spec.txt": "Technical requirements for the equipment.",
    "financials.docx": "Budget and expenditure details for Q3.",
}

# ─── Tool: Read document ──────────────────────────────────


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_doc_contents(
    doc_id: str = Field(description="ID of the document to read"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]


# ─── Tool: Edit document (find/replace) ───────────────────


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing an exact string with a new string. "
    "The old_str must match exactly, including whitespace and punctuation.",
)
def edit_document(
    doc_id: str = Field(description="ID of the document to edit"),
    old_str: str = Field(
        description="The exact text to replace. Must match exactly, including whitespace"
    ),
    new_str: str = Field(description="The new text to insert in place of the old text"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")

    if old_str not in docs[doc_id]:
        raise ValueError(
            f"Text '{old_str}' not found in document '{doc_id}'. "
            f"Make sure the text matches exactly."
        )

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Document '{doc_id}' updated successfully. New content:\n{docs[doc_id]}"


# ─── Tool: Append to document ─────────────────────────────


@mcp.tool(
    name="append_to_document",
    description="Append text to the end of an existing document.",
)
def append_to_document(
    doc_id: str = Field(description="ID of the document to append to"),
    text: str = Field(description="Text to append to the end of the document"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")

    docs[doc_id] = docs[doc_id] + "\n" + text
    return f"Text appended to '{doc_id}'. Updated content:\n{docs[doc_id]}"


# ─── Tool: Create new document ────────────────────────────


@mcp.tool(
    name="create_document",
    description="Create a new document with the given ID and content.",
)
def create_document(
    doc_id: str = Field(description="ID for the new document (e.g., 'notes.md')"),
    content: str = Field(description="Initial content of the document"),
) -> str:
    if doc_id in docs:
        raise ValueError(
            f"Document '{doc_id}' already exists. Use edit_document to modify it."
        )

    docs[doc_id] = content
    return f"Document '{doc_id}' created successfully"


# ─── Entry point ──────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
