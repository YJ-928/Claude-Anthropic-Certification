"""
Exercise 05 — Prompt Templates

Demonstrates:
- Defining reusable prompt templates
- Using prompt arguments
- base.UserMessage for message construction
- Slash command workflow

Run with the MCP Inspector:
    mcp dev exercises/exercise_05_prompt_template.py
"""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

mcp = FastMCP("PromptServer", log_level="ERROR")

# ─── In-memory document store ─────────────────────────────

docs: dict[str, str] = {
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "plan.md": "The plan outlines the steps for implementation.",
    "spec.txt": "Technical requirements for the equipment.",
}

# ─── Tool: Read document (needed for prompts to work) ─────


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


# ─── Tool: Edit document (needed for format prompt) ───────


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string with a new string.",
)
def edit_document(
    doc_id: str = Field(description="ID of the document to edit"),
    old_str: str = Field(description="Text to replace (exact match)"),
    new_str: str = Field(description="New text to insert"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Document '{doc_id}' updated"


# ─── Prompt: Format document in Markdown ──────────────────


@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="ID of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary.
    Feel free to add in extra text, but don't change the meaning.
    Use the 'read_doc_contents' tool to read the document first.
    Use the 'edit_document' tool to save the reformatted version.
    After editing, respond with the final version of the document.
    Don't explain your changes.
    """
    return [base.UserMessage(prompt)]


# ─── Prompt: Summarize document ───────────────────────────


@mcp.prompt(
    name="summarize",
    description="Provide a concise summary of a document.",
)
def summarize_document(
    doc_id: str = Field(description="ID of the document to summarize"),
) -> list[base.Message]:
    prompt = f"""
    Read the document '{doc_id}' using the read_doc_contents tool.
    Then provide a concise summary in 2-3 sentences.
    Focus on the key points and main takeaways.
    """
    return [base.UserMessage(prompt)]


# ─── Prompt: Translate document ───────────────────────────


@mcp.prompt(
    name="translate",
    description="Translate a document to a specified language.",
)
def translate_document(
    doc_id: str = Field(description="ID of the document to translate"),
    language: str = Field(description="Target language (e.g., 'Spanish', 'French')"),
) -> list[base.Message]:
    prompt = f"""
    Read the document '{doc_id}' using the read_doc_contents tool.
    Translate its contents to {language}.
    Use the edit_document tool to replace the original text with the translation.
    Respond with the translated version.
    """
    return [base.UserMessage(prompt)]


# ─── Entry point ──────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
