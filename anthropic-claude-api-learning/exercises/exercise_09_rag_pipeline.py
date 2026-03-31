"""
exercise_09_rag_pipeline.py
────────────────────────────
Demonstrates a complete in-memory RAG (Retrieval-Augmented Generation) pipeline:
  1. Chunk a document into passages
  2. Embed passages with a simple TF-IDF-style vector (no external APIs)
  3. Retrieve the top-k passages by cosine similarity to the query
  4. Pass retrieved context to Claude for a grounded answer

Run:
    python exercise_09_rag_pipeline.py
"""
import sys, os, math, re
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL

# ── Sample corpus ─────────────────────────────────────────────────────────────

DOCUMENT = """
Python is a high-level, general-purpose programming language. Its design philosophy
emphasises code readability, and its syntax allows programmers to express concepts in
fewer lines of code than would be possible in languages such as C++ or Java.

Python supports multiple programming paradigms, including structured, object-oriented,
and functional programming. It is often described as a "batteries included" language due
to its comprehensive standard library.

Python was created by Guido van Rossum and first released in 1991. Van Rossum was the
project's "benevolent dictator for life" until 2018 when he stepped back from the role.

Python 3.0, released in 2008, was a major revision that is not fully backward-compatible
with earlier versions. Python 2 was discontinued with version 2.7.18, released in April 2020.

Python consistently ranks as one of the most popular programming languages; it is
widely used in web development, data science, artificial intelligence, and scripting.
"""

# ── Step 1: Chunking ──────────────────────────────────────────────────────────

def chunk_by_paragraph(text: str) -> list[str]:
    """Split text on blank lines, strip, and drop empty chunks."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


# ── Step 2: Simple TF-IDF bag-of-words embedding ─────────────────────────────

def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]+\b", text.lower())


def build_vocab(chunks: list[str]) -> list[str]:
    all_words: set[str] = set()
    for chunk in chunks:
        all_words.update(tokenize(chunk))
    return sorted(all_words)


def tfidf_vector(text: str, vocab: list[str], idf: dict[str, float]) -> list[float]:
    tokens = tokenize(text)
    tf = Counter(tokens)
    total = len(tokens) or 1
    vec = [tf.get(w, 0) / total * idf.get(w, 1.0) for w in vocab]
    return vec


def compute_idf(chunks: list[str], vocab: list[str]) -> dict[str, float]:
    n = len(chunks)
    idf = {}
    for word in vocab:
        df = sum(1 for c in chunks if word in tokenize(c))
        idf[word] = math.log((n + 1) / (df + 1)) + 1.0
    return idf


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot   = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ── Step 3: Vector store (in-memory) ─────────────────────────────────────────

class SimpleVectorStore:
    def __init__(self):
        self.chunks: list[str] = []
        self.vectors: list[list[float]] = []
        self.vocab: list[str] = []
        self.idf: dict[str, float] = {}

    def ingest(self, chunks: list[str]) -> None:
        self.chunks = chunks
        self.vocab = build_vocab(chunks)
        self.idf   = compute_idf(chunks, self.vocab)
        self.vectors = [tfidf_vector(c, self.vocab, self.idf) for c in chunks]

    def search(self, query: str, top_k: int = 3) -> list[tuple[float, str]]:
        q_vec = tfidf_vector(query, self.vocab, self.idf)
        scored = [
            (cosine_similarity(q_vec, v), chunk)
            for v, chunk in zip(self.vectors, self.chunks)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]


# ── Step 4: RAG answer generation ────────────────────────────────────────────

def rag_query(store: SimpleVectorStore, question: str, top_k: int = 3) -> str:
    hits = store.search(question, top_k=top_k)
    context_parts = [chunk for _, chunk in hits if _ > 0]

    if not context_parts:
        context = "No relevant context found."
    else:
        context = "\n\n".join(context_parts)

    prompt = (
        f"Use ONLY the context below to answer the question. "
        f"If the answer isn't in the context, say 'I don't know'.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Exercise 09 — RAG Pipeline ===\n")

    chunks = chunk_by_paragraph(DOCUMENT)
    print(f"Document chunked into {len(chunks)} passages.\n")

    store = SimpleVectorStore()
    store.ingest(chunks)
    print("Vector store built.\n")

    questions = [
        "Who created Python?",
        "When was Python 3.0 released?",
        "What programming paradigms does Python support?",
        "What is the capital of France?",   # out-of-context test
    ]

    for q in questions:
        print(f"Q: {q}")
        answer = rag_query(store, q)
        print(f"A: {answer}\n")
