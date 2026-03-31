"""
exercise_02_multi_turn_chat.py
──────────────────────────────
Demonstrates:
  - The 3-helper pattern: make_messages / add_user_message / add_assistant_message
  - Building a multi-turn conversation list manually
  - Running an interactive CLI chat loop

Run:
    python exercise_02_multi_turn_chat.py
Type 'quit' or 'exit' to stop.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL

# ── 3 Helper Functions ────────────────────────────────────────────────────────

def make_messages() -> list:
    """Return a fresh, empty message history."""
    return []


def add_user_message(messages: list, text: str) -> list:
    """Append a user turn in-place and return the list."""
    messages.append({"role": "user", "content": text})
    return messages


def add_assistant_message(messages: list, text: str) -> list:
    """Append an assistant turn in-place and return the list."""
    messages.append({"role": "assistant", "content": text})
    return messages


# ── One-shot helper using the history ────────────────────────────────────────

def chat(messages: list, system: str = "", max_tokens: int = 512) -> str:
    """Send the current history to Claude and return the reply text."""
    kwargs = {
        "model": FAST_MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return response.content[0].text


# ── Interactive loop ──────────────────────────────────────────────────────────

def run_chat_loop(system: str = "") -> None:
    messages = make_messages()
    print("Chat started — type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        add_user_message(messages, user_input)
        reply = chat(messages, system=system)
        add_assistant_message(messages, reply)

        print(f"Claude: {reply}\n")


# ── Demo: show a 3-turn conversation without the interactive loop ─────────────

def demo_fixed_conversation() -> None:
    print("=== Exercise 02 — Multi-turn Demo ===\n")
    messages = make_messages()

    turns = [
        "My name is Alex. Remember that.",
        "What is 7 * 6?",
        "What is my name?",
    ]

    for user_text in turns:
        add_user_message(messages, user_text)
        reply = chat(messages)
        add_assistant_message(messages, reply)
        print(f"User:   {user_text}")
        print(f"Claude: {reply}\n")


if __name__ == "__main__":
    demo_fixed_conversation()

    start_interactive = input("Start interactive chat? [y/N]: ").strip().lower()
    if start_interactive == "y":
        run_chat_loop(system="You are a helpful assistant. Be concise.")
