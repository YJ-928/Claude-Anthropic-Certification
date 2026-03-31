"""
chat_service.py — Session-based chat service.

Manages per-session message histories so each client can have a
persistent conversation without server restarts losing context.
"""
import uuid
from typing import Optional
import anthropic
from . import config

# One shared Anthropic client for the application
_client = anthropic.Anthropic(api_key=config.API_KEY)


class ChatService:
    def __init__(self) -> None:
        # Maps session_id -> list of message dicts
        self._sessions: dict[str, list[dict]] = {}

    # ── Session management ────────────────────────────────────────────────────

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = []
        return session_id

    def get_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())

    # ── Message exchange ──────────────────────────────────────────────────────

    def send_message(
        self,
        session_id: str,
        user_text: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Append user_text to the session history, call Claude, append the
        assistant reply, and return the reply text.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Unknown session: {session_id!r}")

        self._sessions[session_id].append({"role": "user", "content": user_text})

        response = _client.messages.create(
            model=model or config.DEFAULT_MODEL,
            max_tokens=max_tokens or config.MAX_TOKENS,
            system=config.SYSTEM_PROMPT,
            messages=self._sessions[session_id],
        )

        reply = response.content[0].text
        self._sessions[session_id].append({"role": "assistant", "content": reply})
        return reply

    def get_stream(
        self,
        session_id: str,
        user_text: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Append the user message, stream Claude's reply, then append the
        complete reply text to history when done.

        Yields text chunks. Callers should consume the entire generator.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Unknown session: {session_id!r}")

        self._sessions[session_id].append({"role": "user", "content": user_text})
        full_reply = ""

        with _client.messages.stream(
            model=model or config.DEFAULT_MODEL,
            max_tokens=max_tokens or config.MAX_TOKENS,
            system=config.SYSTEM_PROMPT,
            messages=self._sessions[session_id],
        ) as stream:
            for chunk in stream.text_stream:
                full_reply += chunk
                yield chunk

        self._sessions[session_id].append({"role": "assistant", "content": full_reply})


# Module-level singleton — imported by main.py and streaming.py
service = ChatService()
