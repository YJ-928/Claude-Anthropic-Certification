"""
Anthropic Client Utility

Thin wrapper around the Anthropic SDK for common operations.
"""

import os
from anthropic import Anthropic


def get_client(api_key: str | None = None) -> Anthropic:
    """
    Create an Anthropic client.

    Uses the provided api_key, or falls back to the ANTHROPIC_API_KEY
    environment variable.
    """
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is required. "
            "Set it in your .env file or pass it directly."
        )
    return Anthropic(api_key=key)


def get_model() -> str:
    """Get the configured Claude model name."""
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")


def send_message(
    client: Anthropic,
    messages: list[dict],
    model: str | None = None,
    system: str | None = None,
    tools: list[dict] | None = None,
    max_tokens: int = 8000,
):
    """
    Send a message to Claude and return the response.

    This is a convenience wrapper around client.messages.create()
    that handles optional parameters cleanly.
    """
    kwargs = {
        "model": model or get_model(),
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system
    if tools:
        kwargs["tools"] = tools
    return client.messages.create(**kwargs)
