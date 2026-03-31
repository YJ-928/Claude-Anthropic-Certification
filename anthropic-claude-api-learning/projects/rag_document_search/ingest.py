"""
ingest.py — Load files from disk, chunk them, embed, and store in the VectorStore.

Supports: .txt, .md  (extensible)
"""
import os
import re
import uuid
from pathlib import Path
from typing import Optional

from .embeddings import TFIDFEmbedder
from .vector_store import VectorStore, Document
from .retriever import BM25Index


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_by_paragraph(text: str, min_chars: int = 80) -> list[str]:
    """Split on blank lines; discard very short chunks."""
    raw = re.split(r"\n\s*\n", text)
    return [p.strip() for p in raw if len(p.strip()) >= min_chars]


def chunk_by_size(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Fixed-size character chunks with optional overlap."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# ── File loading ──────────────────────────────────────────────────────────────

def load_text_file(path: Path) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def ingest_directory(
    directory: str | Path,
    store: VectorStore,
    embedder: TFIDFEmbedder,
    bm25: Optional[BM25Index] = None,
    chunk_strategy: str = "paragraph",   # "paragraph" | "size"
    chunk_size: int = 500,
    overlap: int = 50,
) -> int:
    """
    Walk a directory, load all .txt and .md files, chunk + embed them,
    and populate the VectorStore (and optionally a BM25Index).

    Returns the number of chunks ingested.
    """
    directory = Path(directory)
    all_chunks: list[str]    = []
    chunk_meta: list[dict]   = []

    for file_path in sorted(directory.rglob("*")):
        if file_path.suffix not in (".txt", ".md"):
            continue
        text = load_text_file(file_path)

        if chunk_strategy == "paragraph":
            chunks = chunk_by_paragraph(text)
        else:
            chunks = chunk_by_size(text, chunk_size=chunk_size, overlap=overlap)

        for chunk in chunks:
            all_chunks.append(chunk)
            chunk_meta.append({"source": str(file_path)})

    if not all_chunks:
        return 0

    # Fit embedder on all chunks at once (better IDF estimates)
    if not embedder._fitted:
        embedder.fit(all_chunks)

    docs: list[Document] = []
    for chunk, meta in zip(all_chunks, chunk_meta):
        embedding = embedder.embed(chunk)
        docs.append(Document(
            chunk_id=str(uuid.uuid4()),
            text=chunk,
            source=meta["source"],
            embedding=embedding,
        ))

    store.add_many(docs)

    if bm25 is not None:
        # Rebuild BM25 index with all stored documents
        bm25.build(docs)

    return len(docs)


def ingest_text(
    text: str,
    source: str,
    store: VectorStore,
    embedder: TFIDFEmbedder,
    bm25: Optional[BM25Index] = None,
    chunk_strategy: str = "paragraph",
) -> int:
    """Ingest raw text directly (useful for testing)."""
    if chunk_strategy == "paragraph":
        chunks = chunk_by_paragraph(text)
    else:
        chunks = chunk_by_size(text)

    if not embedder._fitted:
        embedder.fit(chunks)

    docs: list[Document] = []
    for chunk in chunks:
        docs.append(Document(
            chunk_id=str(uuid.uuid4()),
            text=chunk,
            source=source,
            embedding=embedder.embed(chunk),
        ))

    store.add_many(docs)
    if bm25 is not None:
        bm25.build(store._docs)

    return len(docs)
