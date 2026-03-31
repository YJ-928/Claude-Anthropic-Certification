"""
conversation_runner.py — Agentic conversation loop for the Reminder Agent.

Handles:
  - Dispatching Claude's tool_use blocks to real Python functions
  - Feeding tool results back as tool_result content blocks
  - Iterating until stop_reason == "end_turn" or max_steps is reached
"""
import anthropic
import os
from pathlib import Path

from .tools import get_current_datetime, add_duration_to_datetime, set_reminder, list_reminders
from .schemas import TOOL_SCHEMAS


# ── Client setup ──────────────────────────────────────────────────────────────

def _load_env() -> None:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        env = parent / ".env"
        if env.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env)
            except ImportError:
                pass
            break


_load_env()
_client = anthropic.Anthropic()
MODEL = os.environ.get("DEFAULT_MODEL", "claude-haiku-4-5")


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    """Dispatch a tool name + inputs to the appropriate Python function."""
    if name == "get_current_datetime":
        return get_current_datetime()
    if name == "add_duration_to_datetime":
        return add_duration_to_datetime(**inputs)
    if name == "set_reminder":
        return set_reminder(**inputs)
    if name == "list_reminders":
        return list_reminders()
    return f"Error: Unknown tool '{name}'"


def run_tools(tool_use_blocks) -> list[dict]:
    """Execute all tool_use blocks and return tool_result content blocks."""
    results = []
    for block in tool_use_blocks:
        if block.type != "tool_use":
            continue
        output = run_tool(block.name, block.input)
        print(f"    [tool: {block.name}] → {output}")
        results.append({
            "type":        "tool_result",
            "tool_use_id": block.id,
            "content":     output,
        })
    return results


# ── Conversation loop ─────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a helpful reminder assistant. When a user asks you to set a reminder:
1. Call get_current_datetime to know the current time.
2. If the user gave a relative time ("in 1 hour", "tomorrow"), call add_duration_to_datetime.
3. Call set_reminder with the absolute datetime.
4. Confirm to the user with the reminder details.

Always use absolute ISO-8601 datetimes when calling set_reminder.
Never guess the current time.
"""


def run_conversation(
    user_message: str,
    history: list[dict] | None = None,
    max_steps: int = 8,
    verbose: bool = True,
) -> tuple[str, list[dict]]:
    """
    Run one user turn through the agent loop.

    Args:
        user_message: The user's request.
        history:      Existing conversation history (modified in-place and returned).
        max_steps:    Maximum tool-call iterations before giving up.
        verbose:      If True, print tool calls to stdout.

    Returns:
        (final_reply_text, updated_history)
    """
    if history is None:
        history = []

    history.append({"role": "user", "content": user_message})

    for step in range(max_steps):
        response = _client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=history,
        )

        history.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            reply = ""
            for block in response.content:
                if hasattr(block, "text"):
                    reply += block.text
            return reply, history

        if response.stop_reason == "tool_use":
            tool_results = run_tools(response.content)
            history.append({"role": "user", "content": tool_results})

    return "Reached maximum steps without a final answer.", history
