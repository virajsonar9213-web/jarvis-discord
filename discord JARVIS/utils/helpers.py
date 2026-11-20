"""
JARVIS Helpers

Utility functions used throughout the bot.
"""

from typing import Optional


def truncate_text(text: str, max_length: int = 2000, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated.
    Ensures the result doesn't exceed max_length.
    """
    if len(text) <= max_length:
        return text

    # Reserve space for the suffix
    suffix_length = len(suffix)
    if suffix_length >= max_length:
        return text[:max_length]

    return text[: max_length - suffix_length] + suffix


def format_user_mention(user_id: int) -> str:
    """Format a user mention string for Discord."""
    return f"<@{user_id}>"


def format_channel_mention(channel_id: int) -> str:
    """Format a channel mention string for Discord."""
    return f"<#{channel_id}>"


def isnumeric(value: str) -> bool:
    """Check if a string represents a number."""
    try:
        int(value)
        return True
    except ValueError:
        return False


def parse_int(value: str | None) -> Optional[int]:
    """Safely parse an integer from a string."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return the singular or plural form of a word based on count."""
    if plural is None:
        plural = singular + "s"
    return singular if count == 1 else plural


def time_ago(timestamp: str) -> str:
    """
    Convert a timestamp to a human-readable 'time ago' string.
    Simple implementation for Phase 1.
    """
    from datetime import datetime, timezone

    try:
        # Handle ISO format timestamps
        if "T" in timestamp:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(timestamp)

        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = now - dt

        seconds = int(delta.total_seconds())

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            weeks = seconds // 604800
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    except (ValueError, TypeError):
        return "unknown time"


def chunk_list(items: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of a specified size."""
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
