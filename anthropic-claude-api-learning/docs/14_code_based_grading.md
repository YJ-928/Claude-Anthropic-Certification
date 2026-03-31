# 14 — Code-Based Grading

## Overview

Deterministic graders: run the output as code and check the result, or use regex/schema validation.

```python
import ast, re, json

def is_valid_json(text):
    try:
        json.loads(text)
        return 1.0
    except json.JSONDecodeError:
        return 0.0

def is_valid_python(code):
    try:
        ast.parse(code)
        return 1.0
    except SyntaxError:
        return 0.0

def matches_pattern(text, pattern):
    return 1.0 if re.search(pattern, text) else 0.0
```

## Execution-Based Grading

```python
def run_code_test(code: str, test_input, expected_output):
    """Execute generated code and compare output."""
    namespace = {}
    exec(code, namespace)           # run the generated code
    result = namespace["solution"](test_input)
    return 1.0 if result == expected_output else 0.0
```

## Best Practices
- Prefer code graders over model graders when possible (faster, cheaper, deterministic)
- Sandbox code execution if running untrusted output
- Chain graders: first check format, then check correctness

## Common Mistakes
- Running untrusted generated code without a sandbox
- Treating partial credit as binary pass/fail
- Not catching all exception types in validators

## Exercise
Build a grader for a "write a Python function" task that: (1) checks syntax, (2) runs 5 unit tests, and returns a score from 0.0–1.0.
