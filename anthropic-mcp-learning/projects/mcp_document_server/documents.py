"""
In-memory document store for the MCP Document Server.

Documents are stored as a simple dictionary mapping doc_id → content.
In a real application, this would connect to a database or file system.
"""

docs: dict[str, str] = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


def get_doc(doc_id: str) -> str:
    """Get a document's content by ID. Raises ValueError if not found."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    return docs[doc_id]


def update_doc(doc_id: str, old_str: str, new_str: str) -> str:
    """Update a document by replacing old_str with new_str. Returns updated content."""
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found")
    if old_str not in docs[doc_id]:
        raise ValueError(f"Text '{old_str}' not found in document '{doc_id}'")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return docs[doc_id]


def list_doc_ids() -> list[str]:
    """Return a list of all document IDs."""
    return list(docs.keys())


def create_doc(doc_id: str, content: str) -> None:
    """Create a new document. Raises ValueError if it already exists."""
    if doc_id in docs:
        raise ValueError(f"Document '{doc_id}' already exists")
    docs[doc_id] = content
