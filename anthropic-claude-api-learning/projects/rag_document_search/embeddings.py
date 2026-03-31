"""
embeddings.py — Simple embedding utilities for the RAG Document Search project.

Provides:
  - A lightweight TF-IDF bag-of-words embedder (no external API required)
  - cosine_similarity() for comparing vectors
  - Optional Voyage AI integration (set VOYAGE_API_KEY in .env)
"""
import math
import re
from collections import Counter
from typing import Optional


# ── Tokenization ──────────────────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    """Lowercase and extract alphabetic tokens."""
    return re.findall(r"\b[a-z]+\b", text.lower())


# ── TF-IDF embedder ───────────────────────────────────────────────────────────

class TFIDFEmbedder:
    """
    Fits a vocabulary and IDF weights on a corpus of documents, then converts
    any text into a fixed-length TF-IDF vector.
    """

    def __init__(self) -> None:
        self.vocab: list[str] = []
        self.idf: dict[str, float] = {}
        self._fitted = False

    def fit(self, corpus: list[str]) -> "TFIDFEmbedder":
        all_words: set[str] = set()
        for doc in corpus:
            all_words.update(tokenize(doc))
        self.vocab = sorted(all_words)

        n = len(corpus)
        for word in self.vocab:
            df = sum(1 for doc in corpus if word in tokenize(doc))
            self.idf[word] = math.log((n + 1) / (df + 1)) + 1.0

        self._fitted = True
        return self

    def embed(self, text: str) -> list[float]:
        if not self._fitted:
            raise RuntimeError("Call fit() before embed().")
        tokens = tokenize(text)
        tf = Counter(tokens)
        total = len(tokens) or 1
        return [tf.get(w, 0) / total * self.idf.get(w, 1.0) for w in self.vocab]

    @property
    def dimension(self) -> int:
        return len(self.vocab)


# ── Cosine similarity ─────────────────────────────────────────────────────────

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot   = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ── Optional Voyage AI integration ───────────────────────────────────────────

def voyage_embed(
    texts: list[str],
    input_type: str = "document",
    model: str = "voyage-3",
    api_key: Optional[str] = None,
) -> list[list[float]]:
    """
    Use Voyage AI to generate dense embeddings.
    Requires: pip install voyageai  and VOYAGE_API_KEY in environment.

    Falls back gracefully if the SDK is not installed.
    """
    try:
        import voyageai  # type: ignore
        import os
        key = api_key or os.environ.get("VOYAGE_API_KEY", "")
        vo = voyageai.Client(api_key=key)
        result = vo.embed(texts, model=model, input_type=input_type)
        return result.embeddings
    except ImportError:
        raise ImportError(
            "voyageai is not installed. Run: pip install voyageai"
        )
