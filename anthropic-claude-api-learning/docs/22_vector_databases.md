# 22 — Vector Databases

## Overview

A vector database stores embeddings and supports fast nearest-neighbor search.

## Simple In-Memory Store

```python
class VectorStore:
    def __init__(self):
        self._data = []   # list of (vector, metadata)

    def add(self, vector, metadata):
        self._data.append((vector, metadata))

    def search(self, query_vector, top_k=3):
        scored = [
            {"score": cosine_similarity(query_vector, v), **meta}
            for v, meta in self._data
        ]
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
```

## Production Options

| Database | Notes |
|----------|-------|
| Chroma | Easy local setup, good for prototypes |
| Pinecone | Managed, scales to billions of vectors |
| Weaviate | Open source, GraphQL interface |
| pgvector | Postgres extension — great if you already use Postgres |

## Best Practices
- For < 10K chunks, an in-memory store is fine
- For production, use a managed service with persistent storage
- Index metadata (source file, section title) alongside vectors for filtering

## Exercise
Extend the VectorStore class to support filtering by a metadata field (e.g., only search within a specific document).
