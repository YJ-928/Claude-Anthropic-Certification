# 23 — Hybrid Search & BM25

## BM25 Overview

BM25 is a keyword search algorithm. Unlike vector search it excels at exact term matching.

```python
import math, re
from collections import defaultdict

class BM25Index:
    def __init__(self, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self._docs, self._tokenized, self._df = [], [], defaultdict(int)

    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def add(self, metadata):
        tokens = self._tokenize(metadata["content"])
        self._docs.append(metadata)
        self._tokenized.append(tokens)
        for t in set(tokens):
            self._df[t] += 1

    def search(self, query, top_k=3):
        terms = self._tokenize(query)
        N = len(self._docs)
        avg_dl = sum(len(t) for t in self._tokenized) / (N or 1)
        scores = []
        for idx, (doc, tokens) in enumerate(zip(self._docs, self._tokenized)):
            tf_map = defaultdict(int)
            for t in tokens: tf_map[t] += 1
            dl, score = len(tokens), 0.0
            for term in terms:
                tf  = tf_map.get(term, 0)
                df  = self._df.get(term, 0)
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
                tf_norm = tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * dl / avg_dl))
                score += idf * tf_norm
            scores.append({"score": score, **doc})
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
```

## Reciprocal Rank Fusion

```python
from collections import defaultdict

def rrf(ranked_lists, top_k=3):
    scores, lookup = defaultdict(float), {}
    for lst in ranked_lists:
        for rank, doc in enumerate(lst):
            scores[doc["id"]] += 1.0 / (rank + 1)
            lookup[doc["id"]] = doc
    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [{"rrf_score": scores[i], **lookup[i]} for i in sorted_ids[:top_k]]
```

## Best Practices
- Always use hybrid search in production — vector alone misses exact matches
- RRF is simple and works well; no need for learned fusion weights

## Exercise
Index 20 paragraphs using both vector and BM25. For 5 queries, compare which results each approach finds that the other misses.
