# 05 — System Prompts

## Overview

A system prompt tells Claude **how to behave** across the entire conversation — it defines role, tone, rules and restrictions. It is completely separate from the user messages.

```
API Call
│
├── system  ← "You are a strict JSON formatter. Only output valid JSON."
│
└── messages
    └── user: "What is the capital of France?"
         → assistant: {"capital": "Paris"}     (JSON because of system prompt)
```

## Structure

```python
SYSTEM = """You are a [ROLE].

You SHOULD:
- [behaviour 1]
- [behaviour 2]

You should NOT:
- [restriction 1]
- [restriction 2]"""

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=512,
    system=SYSTEM,
    messages=[{"role": "user", "content": "..."}]
)
```

## Recipe: Math Tutor Specialist

```python
MATH_TUTOR = """You are a specialist math tutor.

Responses SHOULD:
- Initially only give hints -- do not reveal the answer
- Patiently walk the student through steps when they need more help
- Show solutions for similar (but different) problems

Responses should NOT:
- Immediately give a direct answer
- Tell the student to use a calculator"""
```

## Recipe: Strict Output Format

```python
JSON_ASSISTANT = """You are a data extraction assistant.
Always respond with valid JSON only. No explanation, no markdown fences.
Schema: {"answer": string, "confidence": "high"|"medium"|"low"}"""
```

## Best Practices

- Keep the system prompt focused on behaviour, not content
- Use explicit SHOULD / SHOULD NOT structure for clarity
- Test the system prompt against adversarial questions that try to break the rules
- Place long reference documents in the system prompt with `cache_control` (see doc 26)

## Common Mistakes

- Putting behavioural instructions inside user messages instead of system
- Writing vague instructions ("be helpful") instead of specific rules
- Forgetting that system prompts count toward input tokens

## Exercise

Write three different system prompts and measure how they change Claude's response to the same question: "Can you help me?" Compare the outputs.
