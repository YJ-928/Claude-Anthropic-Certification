"""
utils/message_helpers.py
Helper functions for building and managing multi-turn conversation histories.

Usage:
    from utils.message_helpers import add_user_message, add_assistant_message, chat
"""
from __future__ import annotations
from typing import Optional
from utils.anthropic_client import client, FAST_MODEL

MessageList = list[dict]


def make_messages() -> MessageList:
    """Return a fresh empty conversation history."""
    return []


def add_user_message(messages: MessageList, text: str) -> None:
    """Append a user turn to the conversation history."""
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages: MessageList, text: str) -> None:
    """Append an assistant turn to the conversation history."""
    messages.append({"role": "assistant", "content": text})


def chat(
    messages: MessageList,
    *,
    system: Optional[str] = None,
    model: str = FAST_MODEL,
    max_tokens: int = 1024,
    temperature: float = 1.0,
) -> str:
    """
    Send the full message history to Claude and return the reply text.

    Args:
        messages:   Conversation history (modified in-place if you call
                    add_assistant_message after this).
        system:     Optional system prompt string.
        model:      Model ID to use.
        max_tokens: Maximum tokens in the response.
        temperature: Sampling temperature (0 = deterministic, 1 = creative).

    Returns:
        The assistant's reply as a plain string.
    """
    params: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    if system:
        params["system"] = system

    response = client.messages.create(**params)
    return response.content[0].text


def chat_turn(
    messages: MessageList,
    user_input: str,
    **kwargs,
) -> str:
    """
    Convenience wrapper: append user message, call API, append assistant reply.

    Returns the assistant reply string. The messages list is updated in-place.
    """
    add_user_message(messages, user_input)
    reply = chat(messages, **kwargs)
    add_assistant_message(messages, reply)
    return reply
