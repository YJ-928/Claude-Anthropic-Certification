"""
utils/anthropic_client.py
Shared Anthropic client setup used across the entire repo.
Import this instead of creating a new client in every file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Walk up from this file to find a .env in any parent directory
_env_path = Path(__file__).parent
for _ in range(4):
    candidate = _env_path / ".env"
    if candidate.exists():
        load_dotenv(candidate)
        break
    _env_path = _env_path.parent
else:
    load_dotenv()  # fallback: system environment

# ---------------------------------------------------------------------------
# Model aliases — change these to switch the whole repo to a different model
# ---------------------------------------------------------------------------
FAST_MODEL   = os.getenv("DEFAULT_MODEL", "claude-haiku-4-5")   # exercises, grading
MAIN_MODEL   = "claude-sonnet-4-5"                              # general use
REASON_MODEL = "claude-sonnet-4-5"                              # extended thinking

# Shared client instance
client = Anthropic()


def get_client() -> Anthropic:
    """Return the shared Anthropic client instance."""
    return client
