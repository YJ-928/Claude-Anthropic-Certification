# 12 — Dataset Generation

## Overview

Claude can generate its own test datasets — faster and cheaper than manual labelling for many use cases.

```python
GEN_PROMPT = """Generate {n} diverse test cases for an {task} system.
Each case must have:
  - "input": a realistic user input
  - "expected": the correct output

Return a JSON array. No explanation."""

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=2048,
    messages=[{"role": "user", "content": GEN_PROMPT.format(n=20, task="sentiment analysis")}],
)
dataset = json.loads(response.content[0].text)
```

## Best Practices
- Specify diversity explicitly ("include edge cases, negations, sarcasm")
- Validate generated data — spot-check manually and run schema validation
- Generate more than you need and filter out low-quality items
- Save datasets to disk (datasets/eval_dataset.json) for reproducibility

## Common Mistakes
- Not seeding enough variety → all examples look the same
- Using generated data without any manual review
- Using the same model for generation and evaluation (bias)

## Exercise
Generate a 30-item dataset for a "classify programming language" task. Each item: `{"code_snippet": "...", "expected_language": "..."}`.
