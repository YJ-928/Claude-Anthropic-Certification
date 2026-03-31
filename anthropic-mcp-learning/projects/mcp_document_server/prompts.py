"""
Prompt definitions for the MCP Document Server.

Prompts are user-controlled primitives — triggered by user actions like slash commands.
Server authors create optimized, tested prompts rather than leaving prompt quality to users.
"""

from mcp.server.fastmcp.prompts import base
from pydantic import Field


def register_prompts(mcp):
    """Register all prompts with the MCP server instance."""

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

        Add in headers, bullet points, tables, etc as necessary.
        Feel free to add in extra text, but don't change the meaning of the report.
        Use the 'read_doc_contents' tool to read the document first.
        Use the 'edit_document' tool to edit the document.
        After the document has been edited, respond with the final version.
        Don't explain your changes.
        """
        return [base.UserMessage(prompt)]

    @mcp.prompt(
        name="summarize",
        description="Provide a concise summary of a document.",
    )
    def summarize_document(
        doc_id: str = Field(description="Id of the document to summarize"),
    ) -> list[base.Message]:
        prompt = f"""
        Read the document '{doc_id}' using the read_doc_contents tool.
        Then provide a concise summary in 2-3 sentences.
        Focus on the key points and main takeaways.
        """
        return [base.UserMessage(prompt)]
