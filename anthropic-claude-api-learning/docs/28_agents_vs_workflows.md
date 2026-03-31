# 28 — Agents vs Workflows

## Definitions

| Type | Description | When to Use |
|------|-------------|-------------|
| **Workflow** | Predefined sequence of steps | Known, predictable processes |
| **Agent** | Claude decides which tools to call | Open-ended, dynamic tasks |

## Workflow Pattern

```
Input → Step 1 (always) → Step 2 (always) → Output
```

```python
def run_workflow(document):
    summary   = summarise(document)      # always step 1
    sentiment = analyse_sentiment(summary)  # always step 2
    return {"summary": summary, "sentiment": sentiment}
```

## Agent Pattern

```python
# Claude decides which tools to call and in what order
def run_agent(user_goal, tools):
    messages = [{"role": "user", "content": user_goal}]
    while True:
        response = client.messages.create(model=MODEL, tools=tools, messages=messages)
        if response.stop_reason != "tool_use":
            return response.content[0].text
        # execute tools Claude chose, append results, continue
```

## Decision Guide

```
Is the sequence of steps always the same?
├── YES → use a Workflow
└── NO  → do you trust Claude to decide the steps?
          ├── YES → use an Agent
          └── NO  → add guardrails or switch to Workflow
```

## Best Practices
- Prefer workflows for production — they are predictable and easier to debug
- Use agents for exploratory or open-ended tasks
- Always add a max_steps guard to agents

## Exercise
Build the same "research and summarise" task as both a workflow and an agent. Compare the outputs on 5 inputs and measure which is more reliable.
