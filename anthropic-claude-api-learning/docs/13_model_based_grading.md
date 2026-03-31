# 13 — Model-Based Grading

## Overview

Use Claude (as a judge) to score outputs that are too complex for exact-match grading — quality, correctness, style.

```python
GRADER_PROMPT = """You are an impartial evaluator.

Question: {question}
Expected answer: {expected}
Actual answer: {actual}

Does the actual answer correctly answer the question?
Reply with exactly one word: correct or incorrect"""

def model_grade(question, expected, actual):
    response = client.messages.create(
        model="claude-haiku-4-5",   # cheap model for grading
        max_tokens=5,
        messages=[{"role": "user", "content": GRADER_PROMPT.format(
            question=question, expected=expected, actual=actual
        )}]
    )
    return response.content[0].text.strip().lower() == "correct"
```

## Best Practices
- Use a cheaper/faster model (Haiku) for grading to save costs
- Keep grader prompts simple — single word or score responses
- Validate the grader itself against a small manually-labelled set
- Use `temperature=0` for deterministic grading

## Common Mistakes
- Using the same model instance that generated the output as grader (lenient bias)
- Asking for a numeric score without a rubric (unstable results)
- Forgetting to set `temperature=0` (non-deterministic grades)

## Exercise
Implement a 1–5 scale grader that evaluates the quality of a customer support response. Validate it by grading 10 manually-rated examples.
