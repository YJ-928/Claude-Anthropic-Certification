# 25 — Contextual Retrieval

## Overview

Chunks extracted from a document can lose context. "Contextual retrieval" pre-processes each chunk by prepending a Claude-generated context sentence.

```
Original chunk:
"It was resolved within 30 days."

Contextualized chunk:
"This chunk is from the Cybersecurity section of the Acme 2023 Annual Report,
 describing the resolution timeline for penetration testing findings.
 It was resolved within 30 days."
```

## Implementation

```python
ADD_CONTEXT_PROMPT = """Document:
<document>{source_document}</document>

Chunk:
<chunk>{chunk}</chunk>

Write ONE sentence situating this chunk within the broader document."""

def add_context(chunk, source_document, model="claude-haiku-4-5"):
    response = client.messages.create(
        model=model, max_tokens=150,
        messages=[{"role": "user", "content": ADD_CONTEXT_PROMPT.format(
            source_document=source_document[:3000], chunk=chunk
        )}]
    )
    return response.content[0].text.strip() + "\n\n" + chunk
```

## Cost Note
Contextual retrieval calls the API once per chunk during indexing. Use prompt caching (doc 26) on the source document to reduce cost by ~80%.

## Exercise
Index the same document with and without contextual retrieval. Run 10 queries and compare retrieval precision.
