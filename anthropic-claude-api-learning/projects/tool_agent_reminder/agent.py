"""
agent.py — ReminderAgent: high-level wrapper around the conversation runner.

Provides a clean, session-aware interface for the interactive CLI.
"""
from .conversation_runner import run_conversation
from .tools import list_reminders


class ReminderAgent:
    """
    Stateful reminder agent that maintains a multi-turn conversation history.

    Usage:
        agent = ReminderAgent()
        reply = agent.chat("Remind me to drink water in 20 minutes.")
        print(reply)
    """

    def __init__(self, verbose: bool = True) -> None:
        self._history: list[dict] = []
        self._verbose = verbose

    def chat(self, user_message: str) -> str:
        """Send a message and return the agent's reply."""
        reply, self._history = run_conversation(
            user_message,
            history=self._history,
            verbose=self._verbose,
        )
        return reply

    def get_reminders(self) -> str:
        """Return a formatted string of all set reminders."""
        return list_reminders()

    def reset(self) -> None:
        """Clear conversation history (but keep reminders)."""
        self._history = []
