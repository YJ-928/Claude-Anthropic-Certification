# 04 — Multi-Turn Conversations

## Overview

Claude has **no memory between API calls**. To maintain context you must send the complete conversation history on every request.

```
Turn 1                     Turn 2                     Turn 3
──────────────────         ──────────────────         ──────────────────
messages = [               messages = [               messages = [
  U: "My name is Alex"       U: "My name is Alex"       U: "My name is Alex"
]                            A: "Hi Alex!"              A: "Hi Alex!"
                           ]                            U: "What's my name?"
                                                        A: "Your name is Alex"
                                                      ]
```

## The Three Helper Pattern

```python
def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})

def chat(messages, system=None):
    params = {"model": MODEL, "max_tokens": 1024, "messages": messages}
    if system:
        params["system"] = system
    return client.messages.create(**params).content[0].text
```

## Chat Loop Pattern

```python
messages = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ("quit", "exit"):
        break

    add_user_message(messages, user_input)
    reply = chat(messages)
    add_assistant_message(messages, reply)
    print(f"Claude: {reply}")
```

## Best Practices

- Always append Claude's reply before the next user message
- Trim history if conversations grow very long (sliding window)
- Store history per-session in server applications (dict keyed by session_id)

## Common Mistakes

- Forgetting to append Claude's reply to history (context breaks)
- Creating a new `messages = []` inside the loop (resets memory each turn)
- Sending only the latest message instead of the full history

## Exercise

Build a chat loop that also prints the current history length after each turn, and automatically ends the session after 10 turns.
