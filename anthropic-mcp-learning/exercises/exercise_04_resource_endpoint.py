"""
Exercise 04 — Resource Endpoints

Demonstrates:
- Defining static resources
- Defining templated resources
- URI patterns
- MIME types (application/json, text/plain)

Run with the MCP Inspector:
    mcp dev exercises/exercise_04_resource_endpoint.py
"""

from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("ResourceServer", log_level="ERROR")

# ─── In-memory data store ─────────────────────────────────

docs: dict[str, str] = {
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "plan.md": "The plan outlines the steps for implementation.",
    "spec.txt": "Technical requirements for the equipment.",
    "financials.docx": "Budget and expenditure details for Q3.",
}

# ─── Static Resource: List all document IDs ───────────────


@mcp.resource("docs://documents", mime_type="application/json")
def list_documents() -> list[str]:
    """Return a list of all available document IDs."""
    return list(docs.keys())


# ─── Templated Resource: Get specific document ────────────


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def get_document(doc_id: str) -> str:
    """Return the contents of a specific document."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]


# ─── Static Resource: Server status ───────────────────────


@mcp.resource("status://health", mime_type="application/json")
def server_health() -> dict:
    """Return server health and statistics."""
    return {
        "status": "healthy",
        "document_count": len(docs),
        "total_characters": sum(len(content) for content in docs.values()),
    }


# ─── Templated Resource: Document metadata ────────────────


@mcp.resource("docs://metadata/{doc_id}", mime_type="application/json")
def document_metadata(doc_id: str) -> dict:
    """Return metadata about a specific document."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    content = docs[doc_id]
    return {
        "id": doc_id,
        "character_count": len(content),
        "word_count": len(content.split()),
    }


# ─── Entry point ──────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
