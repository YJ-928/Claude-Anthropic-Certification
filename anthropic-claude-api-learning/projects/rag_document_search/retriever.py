"""
retriever.py — Hybrid retrieval: dense vector search + BM25 keyword search.

Combines both signals with Reciprocal Rank Fusion (RRF) to produce a ranked
list that benefits from both semantic and exact-keyword matching.
"""
import math
import re
from collections import Counter
from typing import Optional

from .vector_store import VectorStore, Document
from .embeddings import TFIDFEmbedder, cosine_similarity


# ── BM25 index ────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]+\b", text.lower())


class BM25Index:
    """
    Okapi BM25 index over a list of Document objects.

    Parameters:
        k1 (float): Term-frequency saturation parameter (default 1.5).
        b  (float): Length normalisation factor (default 0.75).
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b  = b
        self._docs:       list[Document] = []
        self._term_freqs: list[Counter]  = []
        self._idf:        dict[str, float] = {}
        self._avg_dl: float = 0.0

    def build(self, docs: list[Document]) -> "BM25Index":
        self._docs = docs
        self._term_freqs = [Counter(_tokenize(d.text)) for d in docs]
        n = len(docs)

        # Average document length
        lengths = [sum(tf.values()) for tf in self._term_freqs]
        self._avg_dl = sum(lengths) / n if n else 1.0

        # IDF for every term in the corpus
        all_terms: set[str] = set()
        for tf in self._term_freqs:
            all_terms.update(tf.keys())

        for term in all_terms:
            df = sum(1 for tf in self._term_freqs if term in tf)
            self._idf[term] = math.log((n - df + 0.5) / (df + 0.5) + 1)

        return self

    def search(self, query: str, top_k: int = 10) -> list[tuple[float, Document]]:
        query_terms = _tokenize(query)
        scores = []

        for idx, (doc, tf) in enumerate(zip(self._docs, self._term_freqs)):
            dl = sum(tf.values())
            score = 0.0
            for term in query_terms:
                if term not in tf:
                    continue
                f   = tf[term]
                idf = self._idf.get(term, 0.0)
                score += idf * (f * (self.k1 + 1)) / (
                    f + self.k1 * (1 - self.b + self.b * dl / self._avg_dl)
                )
            scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]


# ── Reciprocal Rank Fusion ────────────────────────────────────────────────────

def reciprocal_rank_fusion(
    ranked_lists: list[list[tuple[float, Document]]],
    k: int = 60,
) -> list[tuple[float, Document]]:
    """
    Combine multiple ranked lists using RRF.
    Score = Σ 1 / (k + rank_i) for each document across all lists.
    """
    rrf_scores: dict[str, float]   = {}
    doc_index:  dict[str, Document] = {}

    for ranked in ranked_lists:
        for rank, (_, doc) in enumerate(ranked, start=1):
            doc_index[doc.chunk_id] = doc
            rrf_scores[doc.chunk_id] = rrf_scores.get(doc.chunk_id, 0.0) + 1 / (k + rank)

    combined = [(score, doc_index[cid]) for cid, score in rrf_scores.items()]
    combined.sort(key=lambda x: x[0], reverse=True)
    return combined


# ── Hybrid retriever ──────────────────────────────────────────────────────────

class HybridRetriever:
    """
    Combines VectorStore (dense) + BM25Index (sparse) results via RRF.

    Usage:
        retriever = HybridRetriever(store, bm25, embedder)
        results   = retriever.retrieve(query, top_k=5)
    """

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index:   BM25Index,
        embedder:     TFIDFEmbedder,
    ) -> None:
        self._store    = vector_store
        self._bm25     = bm25_index
        self._embedder = embedder

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        n_candidates: int = 20,
    ) -> list[tuple[float, Document]]:
        q_vec  = self._embedder.embed(query)
        dense  = self._store.search(q_vec, top_k=n_candidates)
        sparse = self._bm25.search(query, top_k=n_candidates)
        return reciprocal_rank_fusion([dense, sparse])[:top_k]
