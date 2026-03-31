"""
exercise_03_streaming_response.py
──────────────────────────────────
Demonstrates:
  - client.messages.stream() context manager
  - Printing text chunks as they arrive (real-time output)
  - Collecting the full response after streaming finishes
  - Checking usage stats from the final message

Run:
    python exercise_03_streaming_response.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.anthropic_client import client, FAST_MODEL


def stream_and_print(prompt: str, system: str = "") -> str:
    """Stream Claude's reply to stdout and return the full response text."""
    messages = [{"role": "user", "content": prompt}]
    kwargs = {"model": FAST_MODEL, "max_tokens": 512, "messages": messages}
    if system:
        kwargs["system"] = system

    full_text = ""
    print("Claude: ", end="", flush=True)

    with client.messages.stream(**kwargs) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
            full_text += chunk

    # Final message is available after the context manager exits
    final = stream.get_final_message()
    print()  # newline after streamed output
    print(f"\n[Input tokens: {final.usage.input_tokens} | "
          f"Output tokens: {final.usage.output_tokens} | "
          f"Stop: {final.stop_reason}]")
    return full_text


def stream_multi_turn_demo() -> None:
    """Show streaming in a two-turn conversation."""
    messages = [
        {"role": "user",      "content": "List three benefits of type hints in Python."},
        {"role": "assistant", "content": "Sure! Here are three key benefits:\n"},
    ]

    print("\n--- Pre-filled assistant prefix then stream ---")
    print("Claude: Sure! Here are three key benefits:", flush=True)

    with client.messages.stream(
        model=FAST_MODEL,
        max_tokens=256,
        messages=messages,
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    print("=== Exercise 03 — Streaming Responses ===\n")

    user_prompt = "Explain the difference between a list and a tuple in Python in 3 sentences."
    stream_and_print(user_prompt)

    stream_multi_turn_demo()
