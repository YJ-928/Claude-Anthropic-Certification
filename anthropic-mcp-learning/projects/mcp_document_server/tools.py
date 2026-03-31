"""
Tool definitions for the MCP Document Server.

Tools are model-controlled primitives — Claude decides when to invoke them.
"""

from pydantic import Field
from .documents import docs, get_doc, update_doc, create_doc


def register_tools(mcp):
    """Register all tools with the MCP server instance."""

    @mcp.tool(
        name="read_doc_contents",
        description="Read the contents of a document and return it as a string.",
    )
    def read_document(
        doc_id: str = Field(description="Id of the document to read"),
    ) -> str:
        return get_doc(doc_id)

    @mcp.tool(
        name="edit_document",
        description="Edit a document by replacing a string in the document's content "
        "with a new string. The old_str must match exactly, including whitespace.",
    )
    def edit_document(
        doc_id: str = Field(description="Id of the document that will be edited"),
        old_str: str = Field(
            description="The text to replace. Must match exactly, including whitespace"
        ),
        new_str: str = Field(
            description="The new text to insert in place of the old text"
        ),
    ) -> str:
        updated = update_doc(doc_id, old_str, new_str)
        return f"Document '{doc_id}' updated successfully. New content:\n{updated}"

    @mcp.tool(
        name="create_document",
        description="Create a new document with the given ID and content.",
    )
    def create_new_document(
        doc_id: str = Field(description="ID for the new document (e.g., 'notes.md')"),
        content: str = Field(description="Initial content of the document"),
    ) -> str:
        create_doc(doc_id, content)
        return f"Document '{doc_id}' created successfully"
