"""
main.py — Interactive CLI for the RAG Document Search project.

Usage:
    # Ingest a single text file then start Q&A:
    python -m projects.rag_document_search.main --file path/to/document.txt

    # Ingest all .txt/.md files in a directory:
    python -m projects.rag_document_search.main --dir path/to/docs/

    # No file → uses a built-in demo corpus
    python -m projects.rag_document_search.main
"""
import argparse
import sys
from pathlib import Path

from .embeddings import TFIDFEmbedder
from .vector_store import VectorStore
from .retriever import BM25Index, HybridRetriever
from .ingest import ingest_directory, ingest_text
from .rag_pipeline import rag_query


# ── Demo corpus (used when no file is provided) ───────────────────────────────

DEMO_CORPUS = """
Python was created by Guido van Rossum and first released in 1991.
It emphasises code readability and uses indentation as syntax.

Python 3.0, a major backwards-incompatible revision, was released in December 2008.
Python 2 reached end-of-life in April 2020.

Python supports object-oriented, imperative, functional and procedural programming paradigms.
It has a large standard library nicknamed "batteries included".

The Python Package Index (PyPI) hosts over 400,000 third-party packages.
Popular libraries include NumPy, Pandas, Django, Flask, and TensorFlow.

Python is widely used in web development, data science, machine learning, automation,
and scientific computing. It consistently ranks among the top 3 programming languages worldwide.
"""


def build_system(texts: list[str], sources: list[str]) -> HybridRetriever:
    """Build and return a HybridRetriever from a list of documents."""
    embedder = TFIDFEmbedder()
    store    = VectorStore()
    bm25     = BM25Index()

    print("Building retrieval system...")
    for text, source in zip(texts, sources):
        ingest_text(text, source, store, embedder, bm25)

    # Always rebuild BM25 after all ingestion
    bm25.build(store._docs)
    retriever = HybridRetriever(store, bm25, embedder)
    print(f"  Indexed {len(store)} chunks.\n")
    return retriever


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Document Search CLI")
    parser.add_argument("--file", help="Path to a .txt or .md file to ingest")
    parser.add_argument("--dir",  help="Directory of .txt / .md files to ingest")
    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        text = path.read_text(encoding="utf-8")
        retriever = build_system([text], [str(path)])
    elif args.dir:
        embedder = TFIDFEmbedder()
        store    = VectorStore()
        bm25     = BM25Index()
        print("Ingesting directory...")
        count = ingest_directory(args.dir, store, embedder, bm25)
        bm25.build(store._docs)
        retriever = HybridRetriever(store, bm25, embedder)
        print(f"  Indexed {count} chunks.\n")
    else:
        print("No file/dir specified — using built-in demo corpus.\n")
        retriever = build_system([DEMO_CORPUS], ["demo_corpus"])

    print("RAG Document Search ready. Type 'quit' to exit.\n")

    while True:
        query = input("Question: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        result = rag_query(query, retriever, top_k=3, use_rerank=True)
        print(f"\nAnswer:\n{result['answer']}")
        print("\nSources:")
        for score, source in result["sources"]:
            print(f"  [{score:.3f}] {source}")
        print()


if __name__ == "__main__":
    main()
