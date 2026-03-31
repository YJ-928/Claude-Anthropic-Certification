"""
Config

Loads and validates configuration from environment variables.
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    api_key: str
    model: str

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is required. "
                "Set it in your .env file or as an environment variable."
            )
        model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        return cls(api_key=api_key, model=model)
