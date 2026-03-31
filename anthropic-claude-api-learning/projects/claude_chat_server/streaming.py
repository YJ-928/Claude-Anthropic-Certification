"""
streaming.py — Server-Sent Events (SSE) helper for the chat server.

Converts the ChatService's text-chunk generator into a properly formatted
SSE stream that browsers and fetch() clients can consume directly.
"""
import json
from typing import Iterator


def format_sse_event(data: str, event: str = "message") -> str:
    """
    Format a single SSE event frame.
    Spec: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
    """
    # Escape newlines inside the data payload so each event fits on one line
    escaped = data.replace("\n", "\\n")
    return f"event: {event}\ndata: {escaped}\n\n"


def sse_generator(text_chunks: Iterator[str]) -> Iterator[str]:
    """
    Wrap a text-chunk iterator as an SSE stream.

    Emits:
      - "message" events for each text chunk
      - A final "done" event with data "[DONE]"
    """
    try:
        for chunk in text_chunks:
            if chunk:
                payload = json.dumps({"text": chunk})
                yield format_sse_event(payload, event="message")
    finally:
        yield format_sse_event("[DONE]", event="done")
