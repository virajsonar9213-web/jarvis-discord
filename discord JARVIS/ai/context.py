"""
JARVIS Context Manager

Manages conversation context for AI interactions.
Builds context from conversation history, memories, and channel information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.logger import get_logger

logger = get_logger("context")


@dataclass
class ConversationContext:
    """Context for a conversation with the AI."""

    user_id: int
    channel_id: Optional[int] = None
    guild_id: Optional[int] = None
    messages: list[dict] = field(default_factory=list)
    memories: list[dict] = field(default_factory=list)
    system_instruction: str = ""
    max_history_messages: int = 20

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the context."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

        # Trim old messages if over limit
        if len(self.messages) > self.max_history_messages:
            self.messages = self.messages[-self.max_history_messages:]

    def get_history_for_api(self) -> list[dict]:
        """Get message history formatted for API calls."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear the conversation context."""
        self.messages.clear()
        self.memories.clear()


class ContextManager:
    """
    Manager for conversation contexts.

    Maintains separate contexts for different users/channels.
    """

    def __init__(self):
        self._contexts: dict[str, ConversationContext] = {}
        self._max_context_age_hours: int = 24

    def _get_context_key(self, user_id: int, channel_id: Optional[int] = None) -> str:
        """Generate a key for a context."""
        if channel_id:
            return f"{user_id}:{channel_id}"
        return str(user_id)

    def get_context(
        self,
        user_id: int,
        channel_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        system_instruction: str = "",
    ) -> ConversationContext:
        """Get or create a context for a user/channel."""
        key = self._get_context_key(user_id, channel_id)

        if key not in self._contexts:
            self._contexts[key] = ConversationContext(
                user_id=user_id,
                channel_id=channel_id,
                guild_id=guild_id,
                system_instruction=system_instruction,
            )
            logger.debug(f"Created new context for {key}")

        return self._contexts[key]

    def get_or_create_context(
        self,
        user_id: int,
        channel_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        system_instruction: str = "",
    ) -> ConversationContext:
        """Alias for get_context for clarity."""
        return self.get_context(user_id, channel_id, guild_id, system_instruction)

    def add_user_message(
        self,
        user_id: int,
        content: str,
        channel_id: Optional[int] = None,
    ) -> None:
        """Add a user message to the context."""
        context = self.get_context(user_id, channel_id)
        context.add_message("user", content)

    def add_assistant_message(
        self,
        user_id: int,
        content: str,
        channel_id: Optional[int] = None,
    ) -> None:
        """Add an assistant message to the context."""
        context = self.get_context(user_id, channel_id)
        context.add_message("assistant", content)

    def get_recent_messages(
        self,
        user_id: int,
        channel_id: Optional[int] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Get recent messages from a context."""
        context = self._contexts.get(self._get_context_key(user_id, channel_id))
        if not context:
            return []

        return context.messages[-limit:]

    def prune_old_contexts(self) -> int:
        """Remove contexts older than max age. Returns count removed."""
        now = datetime.now()
        expired_keys = []

        for key, context in self._contexts.items():
            if context.messages:
                last_message = context.messages[-1]
                try:
                    last_time = datetime.fromisoformat(last_message["timestamp"])
                    age_hours = (now - last_time).total_seconds() / 3600
                    if age_hours > self._max_context_age_hours:
                        expired_keys.append(key)
                except (ValueError, KeyError):
                    pass

        for key in expired_keys:
            del self._contexts[key]

        if expired_keys:
            logger.info(f"Pruned {len(expired_keys)} old contexts")

        return len(expired_keys)

    def clear_context(self, user_id: int, channel_id: Optional[int] = None) -> bool:
        """Clear a specific context."""
        key = self._get_context_key(user_id, channel_id)
        if key in self._contexts:
            self._contexts[key].clear()
            return True
        return False

    def clear_all_contexts(self) -> int:
        """Clear all contexts. Returns count cleared."""
        count = len(self._contexts)
        self._contexts.clear()
        logger.info(f"Cleared {count} contexts")
        return count

    def get_context_count(self) -> int:
        """Get the number of active contexts."""
        return len(self._contexts)
