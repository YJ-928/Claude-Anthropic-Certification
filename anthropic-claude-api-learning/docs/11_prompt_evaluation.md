# 11 — Prompt Evaluation

## Overview

An eval pipeline measures how well a prompt performs across a set of test cases, giving you a score you can track as you iterate.

```
Dataset (input/expected) → Run prompt → Score each output → Aggregate score
```

## Eval Pipeline Structure

```python
def run_eval(prompt_template, dataset, grader):
    results = []
    for item in dataset:
        output = call_claude(prompt_template.format(**item))
        score  = grader(output, item["expected"])
        results.append({"input": item, "output": output, "score": score})
    total = sum(r["score"] for r in results) / len(results)
    return total, results
```

## Grader Types

1. **Exact match** — `output.strip() == expected`
2. **Contains** — `expected in output`
3. **Code execution** — run the output as code, check result
4. **Model grading** — ask Claude to judge (see doc 13)

## Best Practices
- Build the dataset before writing the prompt
- Use at least 20 examples for meaningful scores
- Track scores across prompt versions in a table
- Separate "development" and "held-out" test sets

## Common Mistakes
- Evaluating on the same examples you used to tune the prompt
- Writing a grader that is easier to game than to solve
- Skipping evaluation and relying on vibes

## Exercise
Write an eval for a summarisation prompt. Score outputs by: (1) length ≤ 100 words, and (2) all key facts present (use model grading for fact coverage).
