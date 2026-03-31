"""
vector_store.py — In-memory vector store for the RAG Document Search project.

Stores document chunks with their embedding vectors and supports top-k
cosine similarity search.
"""
from dataclasses import dataclass, field
from typing import Optional
from .embeddings import cosine_similarity


@dataclass
class Document:
    """A single text chunk with its metadata and embedding vector."""
    chunk_id:  str
    text:      str
    source:    str                  # file path or URL
    embedding: list[float]
    metadata:  dict = field(default_factory=dict)


class VectorStore:
    """
    Simple in-memory vector store.

    Usage:
        store = VectorStore()
        store.add(Document(...))
        results = store.search(query_vector, top_k=5)
    """

    def __init__(self) -> None:
        self._docs: list[Document] = []

    # ── Write ─────────────────────────────────────────────────────────────────

    def add(self, doc: Document) -> None:
        """Add a single document to the store."""
        self._docs.append(doc)

    def add_many(self, docs: list[Document]) -> None:
        """Bulk-add documents."""
        self._docs.extend(docs)

    def clear(self) -> None:
        """Remove all documents."""
        self._docs.clear()

    # ── Read ──────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._docs)

    def get_by_id(self, chunk_id: str) -> Optional[Document]:
        for doc in self._docs:
            if doc.chunk_id == chunk_id:
                return doc
        return None

    # ── Search ────────────────────────────────────────────────────────────────

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[tuple[float, Document]]:
        """
        Return the top_k documents most similar to query_vector.
        Results are (score, Document) tuples sorted descending by score.
        """
        scored = [
            (cosine_similarity(query_vector, doc.embedding), doc)
            for doc in self._docs
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(score, doc) for score, doc in scored[:top_k] if score >= min_score]
