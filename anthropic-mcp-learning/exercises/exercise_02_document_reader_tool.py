"""
Exercise 02 — Document Reader Tool

Demonstrates:
- Reading document contents from an in-memory store
- Multiple document types
- Error handling for missing documents
- Returning document metadata alongside content

Run with the MCP Inspector:
    mcp dev exercises/exercise_02_document_reader_tool.py
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import json

mcp = FastMCP("DocumentReaderServer", log_level="ERROR")

# ─── In-memory document store ─────────────────────────────

docs: dict[str, dict] = {
    "report.pdf": {
        "content": "The report details the state of a 20m condenser tower. "
        "Inspection was conducted on 2024-01-15. All systems operational.",
        "author": "Angela Smith, P.E.",
        "created": "2024-01-15",
    },
    "plan.md": {
        "content": "# Implementation Plan\n\n"
        "1. Requirements gathering\n"
        "2. Design phase\n"
        "3. Implementation\n"
        "4. Testing\n"
        "5. Deployment",
        "author": "Project Team",
        "created": "2024-02-01",
    },
    "spec.txt": {
        "content": "Technical specifications for the condenser system. "
        "Operating temperature: 150-200°C. Pressure rating: 15 bar.",
        "author": "Engineering Dept",
        "created": "2024-01-20",
    },
}

# ─── Tool: Read document contents ─────────────────────────


@mcp.tool(
    name="read_document",
    description="Read the full contents of a document by its ID.",
)
def read_document(
    doc_id: str = Field(description="ID of the document to read (e.g., 'report.pdf')"),
) -> str:
    if doc_id not in docs:
        available = ", ".join(docs.keys())
        raise ValueError(
            f"Document '{doc_id}' not found. Available documents: {available}"
        )
    return docs[doc_id]["content"]


# ─── Tool: Get document metadata ──────────────────────────


@mcp.tool(
    name="get_document_info",
    description="Get metadata about a document (author, creation date) without its full content.",
)
def get_document_info(
    doc_id: str = Field(description="ID of the document"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    doc = docs[doc_id]
    return json.dumps(
        {
            "id": doc_id,
            "author": doc["author"],
            "created": doc["created"],
            "content_length": len(doc["content"]),
        },
        indent=2,
    )


# ─── Tool: Search documents ───────────────────────────────


@mcp.tool(
    name="search_documents",
    description="Search all documents for a keyword. Returns matching document IDs and excerpts.",
)
def search_documents(
    query: str = Field(description="Keyword or phrase to search for"),
) -> str:
    matches = []
    for doc_id, doc in docs.items():
        content = doc["content"]
        if query.lower() in content.lower():
            # Find the position and extract a surrounding excerpt
            idx = content.lower().index(query.lower())
            start = max(0, idx - 30)
            end = min(len(content), idx + len(query) + 30)
            excerpt = content[start:end]
            if start > 0:
                excerpt = "..." + excerpt
            if end < len(content):
                excerpt = excerpt + "..."
            matches.append({"doc_id": doc_id, "excerpt": excerpt})

    if not matches:
        return f"No documents contain '{query}'"
    return json.dumps(matches, indent=2)


# ─── Entry point ──────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
