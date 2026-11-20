"""
JARVIS Bot Settings

Central configuration management.
Loads from environment variables via python-dotenv.
Never hardcode secrets here.
"""

import os
from dotenv import load_dotenv


# Load .env file
load_dotenv()


def _parse_int(value: str | None) -> int | None:
    """Safely parse an integer from env value."""
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


class Settings:
    """Bot-wide settings loaded from environment."""

    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    OWNER_USER_ID: int | None = _parse_int(os.getenv("OWNER_USER_ID"))
    FRIEND_USER_ID: int | None = _parse_int(os.getenv("FRIEND_USER_ID"))

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    JARVIS_NAME: str = os.getenv("JARVIS_NAME", "JARVIS")
    JARVIS_OWNER_USERNAME: str = os.getenv("JARVIS_OWNER_USERNAME", "Owner")

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of validation errors. Empty if valid."""
        errors = []
        if not cls.DISCORD_TOKEN:
            errors.append("DISCORD_TOKEN is not set in .env")
        if cls.OWNER_USER_ID is None:
            errors.append("OWNER_USER_ID is not set or invalid in .env")
        if cls.FRIEND_USER_ID is None:
            errors.append("FRIEND_USER_ID is not set or invalid in .env")
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set in .env")
        return errors
