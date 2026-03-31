"""
exercise_01_basic_api_call.py
─────────────────────────────
Demonstrates:
  - Loading the API key from .env
  - Creating an Anthropic client
  - Making a basic messages.create() call
  - Accessing the response text and usage stats

Run:
    python exercise_01_basic_api_call.py
"""
import sys
import os

# Allow running from any directory inside the repo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL


def basic_api_call(prompt: str) -> str:
    """Send a single-turn message to Claude and return the reply text."""
    response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    print(f"Model used:     {response.model}")
    print(f"Input tokens:   {response.usage.input_tokens}")
    print(f"Output tokens:  {response.usage.output_tokens}")
    print(f"Stop reason:    {response.stop_reason}")
    print()

    return response.content[0].text


if __name__ == "__main__":
    print("=== Exercise 01 — Basic API Call ===\n")

    # Simple question
    reply = basic_api_call("What is the capital of Japan? Reply in one sentence.")
    print(f"Reply: {reply}\n")

    # Check for truncation
    short_response = client.messages.create(
        model=FAST_MODEL,
        max_tokens=5,          # intentionally too small
        messages=[{"role": "user", "content": "Write a short poem about Python."}],
    )
    if short_response.stop_reason == "max_tokens":
        print("WARNING: Response was truncated (max_tokens too low).")
        print(f"Partial text: {short_response.content[0].text!r}")
