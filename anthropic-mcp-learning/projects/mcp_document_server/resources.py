"""
Resource definitions for the MCP Document Server.

Resources are app-controlled primitives — application code decides when to fetch data.
"""

from .documents import docs, get_doc, list_doc_ids


def register_resources(mcp):
    """Register all resources with the MCP server instance."""

    @mcp.resource("docs://documents", mime_type="application/json")
    def list_docs() -> list[str]:
        """Return a list of all available document IDs."""
        return list_doc_ids()

    @mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
    def fetch_doc(doc_id: str) -> str:
        """Return the contents of a specific document."""
        return get_doc(doc_id)

    @mcp.resource("status://health", mime_type="application/json")
    def server_health() -> dict:
        """Return server health and document statistics."""
        return {
            "status": "healthy",
            "document_count": len(docs),
            "document_ids": list_doc_ids(),
        }
