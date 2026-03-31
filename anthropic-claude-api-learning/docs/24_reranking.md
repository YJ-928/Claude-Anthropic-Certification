# 24 — Reranking

## Overview

After hybrid search returns top N candidates, reranking uses an LLM to re-order them by actual relevance.

```python
RERANK_PROMPT = """User query: {query}

Candidates:
{candidates}

Return a JSON array of document IDs ordered from most to least relevant.
Example: [2, 0, 1]"""

def rerank(query, candidates, model="claude-haiku-4-5"):
    cand_text = "\n".join(f"[{c['id']}] {c['content'][:200]}" for c in candidates)
    response = client.messages.create(
        model=model, max_tokens=100,
        stop_sequences=["]"],
        messages=[
            {"role": "user",      "content": RERANK_PROMPT.format(query=query, candidates=cand_text)},
            {"role": "assistant", "content": "["},
        ]
    )
    import json
    ranked_ids = json.loads("[" + response.content[0].text)
    id_map = {c["id"]: c for c in candidates}
    return [id_map[i] for i in ranked_ids if i in id_map]
```

## Best Practices
- Retrieve 2–3x more candidates than you need, then rerank to top_k
- Use a cheap model (Haiku) for reranking — it just needs to rank, not answer
- Fallback to original order if reranking fails (parse error, timeout)

## Exercise
Compare RAG quality with and without reranking on 10 questions. Score each with a model grader.
