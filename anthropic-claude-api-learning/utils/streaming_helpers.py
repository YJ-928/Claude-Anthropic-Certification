"""
utils/streaming_helpers.py
Helper functions for streaming Claude responses to the terminal or a callback.
"""
from __future__ import annotations
from typing import Callable, Optional, Iterator
from utils.anthropic_client import client, FAST_MODEL


def stream_to_stdout(
    user_message: str,
    *,
    system: Optional[str] = None,
    model: str = FAST_MODEL,
    max_tokens: int = 1024,
) -> str:
    """
    Send a single-turn message and print tokens to stdout as they arrive.

    Returns the full concatenated response text when streaming completes.
    """
    messages = [{"role": "user", "content": user_message}]
    params: dict = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        params["system"] = system

    full_text = ""
    with client.messages.stream(**params) as stream:
        for text_chunk in stream.text_stream:
            print(text_chunk, end="", flush=True)
            full_text += text_chunk
    print()  # newline after stream ends
    return full_text


def stream_with_callback(
    messages: list[dict],
    callback: Callable[[str], None],
    *,
    system: Optional[str] = None,
    model: str = FAST_MODEL,
    max_tokens: int = 1024,
) -> str:
    """
    Stream a multi-turn response and call `callback(chunk)` for each text chunk.

    Returns the full concatenated response text.
    Useful for websockets, SSE, or any custom output destination.
    """
    params: dict = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        params["system"] = system

    full_text = ""
    with client.messages.stream(**params) as stream:
        for chunk in stream.text_stream:
            callback(chunk)
            full_text += chunk
    return full_text


def stream_generator(
    messages: list[dict],
    *,
    system: Optional[str] = None,
    model: str = FAST_MODEL,
    max_tokens: int = 1024,
) -> Iterator[str]:
    """
    Yield text chunks from a streaming Claude response.

    Usage:
        for chunk in stream_generator(messages):
            print(chunk, end="", flush=True)
    """
    params: dict = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        params["system"] = system

    with client.messages.stream(**params) as stream:
        yield from stream.text_stream
