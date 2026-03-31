"""
config.py — Application settings for the Claude Chat Server.
Settings are read from environment variables / .env file.
"""
import os
from pathlib import Path

# Walk up to find the .env in the repo root
def _find_env() -> Path | None:
    here = Path(__file__).resolve().parent
    for parent in [here, *here.parents]:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return None

_env_path = _find_env()
if _env_path:
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

# ── Settings ──────────────────────────────────────────────────────────────────

API_KEY        = os.environ.get("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL  = os.environ.get("DEFAULT_MODEL", "claude-haiku-4-5")
MAX_TOKENS     = int(os.environ.get("MAX_TOKENS", "1024"))
HOST           = os.environ.get("HOST", "127.0.0.1")
PORT           = int(os.environ.get("PORT", "8000"))
SYSTEM_PROMPT  = os.environ.get(
    "SYSTEM_PROMPT",
    "You are a helpful assistant. Be concise and accurate.",
)
