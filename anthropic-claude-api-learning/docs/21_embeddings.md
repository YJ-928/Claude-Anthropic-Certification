# 21 — Embeddings

## Overview

An embedding is a list of numbers (vector) that represents the meaning of text. Similar texts have similar vectors.

```
"Paris is the capital of France"  → [0.12, -0.45, 0.88, ...]  (1024 floats)
"France's capital city is Paris"  → [0.11, -0.44, 0.87, ...]  (very similar!)
"I like pizza"                    → [0.93,  0.21, -0.34, ...]  (very different)
```

## Cosine Similarity

```python
import math

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b))
    return dot / mag if mag else 0.0
```

## Production: Voyage AI

```python
import voyageai
vo = voyageai.Client()  # reads VOYAGE_API_KEY from env
embedding = vo.embed(["your text"], model="voyage-3").embeddings[0]
```

## Best Practices
- Use voyage-3 or similar for production — simple bag-of-words embeddings are for demos only
- Normalize vectors before storing for faster cosine search
- Cache embeddings — recomputing is expensive

## Exercise
Embed 10 sentences about different topics. Build a 10x10 similarity matrix and visualize which sentences are most similar.
