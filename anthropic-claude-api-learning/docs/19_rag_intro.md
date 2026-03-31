# 19 — RAG Introduction

## Overview

RAG (Retrieval Augmented Generation) solves the problem of querying documents that are too large for a single context window.

```
Document (500 pages)
      │
      ▼ ingest once
Chunks → Embeddings → Vector Index
      │
      ▼ at query time
User Query → Retrieve top-k chunks → Send only those to Claude
```

## Why RAG?
- 500-page document = ~300K tokens = expensive + slow per query
- With RAG: pre-process once, then each query sends only 3–5 relevant chunks (~2K tokens)

## RAG Pipeline Steps
1. **Chunking** — split document into pieces (see doc 20)
2. **Embedding** — convert chunks to vectors (doc 21)
3. **Index** — store vectors for fast search (doc 22)
4. **Retrieve** — find top-k relevant chunks at query time
5. **Generate** — send chunks + question to Claude

## Best Practices
- Use section-based chunking for structured documents
- Combine vector + BM25 search (hybrid) for best recall
- Add context to chunks before indexing (contextual retrieval, doc 25)

## Exercise
Build the simplest possible RAG: chunk a text file by paragraph, search with keyword matching, pass top 3 chunks to Claude.
