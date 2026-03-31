# 10 — Prompt Engineering

## Key Techniques

| Technique | Description | When to Use |
|-----------|-------------|-------------|
| Role assignment | "You are a..." | Always — shapes tone and expertise |
| Few-shot examples | Show input→output pairs | Complex format requirements |
| Chain of thought | "Think step by step" | Math, logic, multi-step tasks |
| XML tags | `<context>...</context>` | Separate sections, long prompts |
| Positive framing | Say what TO do, not just what NOT to do | Clearer instructions |

## XML Tag Pattern

```python
PROMPT = """<document>
{document_text}
</document>

<task>
Summarise the document above in exactly 3 bullet points.
</task>"""
```

## Few-Shot Pattern

```python
PROMPT = """Convert these to JSON:

Input: "Alice is 30 and works as a nurse"
Output: {"name": "Alice", "age": 30, "job": "nurse"}

Input: "Bob, 25, software engineer"
Output: {"name": "Bob", "age": 25, "job": "software engineer"}

Input: "{user_input}"
Output:"""
```

## Best Practices
- Be specific and explicit — vague prompts get vague outputs
- Use XML tags to structure long prompts
- Test with edge cases and adversarial inputs
- Iterate: measure first, then improve

## Common Mistakes
- Giving contradictory instructions
- Over-specifying format and under-specifying content
- Writing prompts without testing them

## Exercise
Take a poorly written prompt and improve it using at least three techniques from the table above. Measure the improvement using an eval (see doc 11).
