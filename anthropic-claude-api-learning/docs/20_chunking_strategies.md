# 20 — Chunking Strategies

## Three Approaches

| Strategy | How | Best For |
|----------|-----|---------- |
| Size-based | Split every N chars with overlap | Homogeneous prose |
| Structure-based | Split on headers/paragraphs | Markdown, HTML docs |
| Semantic | Group by topic similarity | Dense technical docs |

## Size-Based

```python
def chunk_by_size(text, chunk_size=500, overlap=100):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]
```

## Structure-Based (Recommended)

```python
import re
def chunk_by_section(text):
    sections = re.split(r'(?=^## )', text, flags=re.MULTILINE)
    return [s.strip() for s in sections if s.strip()]
```

## Best Practices
- For most documents, structure-based is best
- Always include some overlap in size-based chunking (avoid cutting sentences)
- Aim for 200–800 tokens per chunk

## Exercise
Compare all three strategies on a markdown document. Count chunks and average chunk length for each.
