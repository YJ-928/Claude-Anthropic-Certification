"""
rag_pipeline.py — End-to-end RAG query pipeline.

Provides:
  - rerank()    → Use Claude to re-order candidates by relevance
  - rag_query() → Full pipeline: retrieve → (rerank) → generate
"""
import json
import sys
import os
from pathlib import Path

# Allow running as a script from inside the project directory
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import anthropic
from .retriever import HybridRetriever
from .vector_store import Document

# ── Anthropic client factories ────────────────────────────────────────────────

def _load_env() -> None:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        env = parent / ".env"
        if env.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env)
            except ImportError:
                pass
            break


_load_env()
_client = anthropic.Anthropic()
FAST_MODEL = os.environ.get("DEFAULT_MODEL", "claude-haiku-4-5")
MAIN_MODEL = "claude-sonnet-4-5"


# ── LLM Reranker ──────────────────────────────────────────────────────────────

def rerank(
    query: str,
    candidates: list[tuple[float, Document]],
    top_k: int = 3,
) -> list[tuple[float, Document]]:
    """
    Ask Claude to score each candidate chunk for relevance to the query.
    Returns top_k candidates sorted by LLM relevance score.
    """
    if not candidates:
        return []

    numbered = "\n\n".join(
        f"[{i}] {doc.text[:300]}" for i, (_, doc) in enumerate(candidates)
    )

    prompt = (
        f"Rate the relevance of each passage for answering the query.\n"
        f"Query: {query}\n\n"
        f"Passages:\n{numbered}\n\n"
        f"Return a JSON array of objects like: "
        f'[{{"index": 0, "score": 0.9}}, ...]. '
        f"Scores range 0.0 (irrelevant) to 1.0 (highly relevant). "
        f"Return ONLY the JSON array."
    )

    response = _client.messages.create(
        model=FAST_MODEL,
        max_tokens=256,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        raw = response.content[0].text.strip()
        scores = json.loads(raw)
        scored_candidates = []
        for item in scores:
            idx   = item.get("index", -1)
            score = float(item.get("score", 0.0))
            if 0 <= idx < len(candidates):
                scored_candidates.append((score, candidates[idx][1]))
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[:top_k]
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback: return the top candidates as-is
        return candidates[:top_k]


# ── Answer generation ─────────────────────────────────────────────────────────

def generate_answer(query: str, context_chunks: list[str]) -> str:
    """Generate a grounded answer using retrieved context."""
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No context available."

    prompt = (
        "Answer the question using ONLY the context provided below. "
        "If the answer isn't in the context, say 'I don't have enough information to answer that.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )

    response = _client.messages.create(
        model=MAIN_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ── Full pipeline ─────────────────────────────────────────────────────────────

def rag_query(
    query:     str,
    retriever: HybridRetriever,
    top_k:     int = 5,
    use_rerank: bool = True,
) -> dict:
    """
    Full RAG pipeline: retrieve → (rerank) → generate.

    Returns a dict with:
      - answer        : str
      - sources       : list of (score, source_path) tuples
      - context_chunks: list of retrieved text chunks
    """
    candidates = retriever.retrieve(query, top_k=top_k * 2)

    if use_rerank and len(candidates) > top_k:
        final_candidates = rerank(query, candidates, top_k=top_k)
    else:
        final_candidates = candidates[:top_k]

    context_chunks = [doc.text for _, doc in final_candidates]
    sources        = [(score, doc.source) for score, doc in final_candidates]

    answer = generate_answer(query, context_chunks)

    return {
        "answer":         answer,
        "sources":        sources,
        "context_chunks": context_chunks,
    }
