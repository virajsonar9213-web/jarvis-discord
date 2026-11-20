"""
JARVIS Memory Manager

Manages conversation memory and user preferences.
Stores memories in SQLite database.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.logger import get_logger

logger = get_logger("memory")


@dataclass
class Memory:
    """A stored memory."""

    id: Optional[int] = None
    user_id: Optional[int] = None  # None for shared memories
    category: str = "general"
    content: str = ""
    created_at: datetime | None = None
    is_active: bool = True

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class MemoryManager:
    """
    Manager for JARVIS's conversation memory.

    Memory categories:
    1. User preferences
    2. Important instructions
    3. Ongoing projects
    4. Previous conversations
    5. Frequently used commands
    6. Configured settings

    Phase 1: In-memory storage.
    Phase 2+: Database persistence.
    """

    def __init__(self):
        self._memories: dict[int, Memory] = {}
        self._next_id: int = 1

    def add_memory(
        self,
        content: str,
        user_id: Optional[int] = None,
        category: str = "general",
    ) -> Memory:
        """Add a new memory."""
        memory = Memory(
            id=self._next_id,
            user_id=user_id,
            category=category,
            content=content,
        )
        self._memories[self._next_id] = memory
        self._next_id += 1

        logger.info(f"Added memory #{memory.id}: {category}")
        return memory

    def get_memory(self, memory_id: int) -> Optional[Memory]:
        """Get a specific memory by ID."""
        return self._memories.get(memory_id)

    def get_memories_for_user(
        self,
        user_id: int,
        category: Optional[str] = None,
        include_inactive: bool = False,
    ) -> list[Memory]:
        """Get memories for a specific user."""
        memories = [
            m for m in self._memories.values()
            if m.user_id == user_id and (include_inactive or m.is_active)
        ]

        if category:
            memories = [m for m in memories if m.category == category]

        return memories

    def get_shared_memories(self, category: Optional[str] = None) -> list[Memory]:
        """Get memories not tied to a specific user."""
        memories = [
            m for m in self._memories.values()
            if m.user_id is None and m.is_active
        ]

        if category:
            memories = [m for m in memories if m.category == category]

        return memories

    def get_all_active_memories(self) -> list[Memory]:
        """Get all active memories."""
        return [m for m in self._memories.values() if m.is_active]

    def update_memory(
        self,
        memory_id: int,
        content: Optional[str] = None,
        category: Optional[str] = None,
    ) -> bool:
        """Update an existing memory."""
        memory = self.get_memory(memory_id)
        if not memory:
            return False

        if content is not None:
            memory.content = content
        if category is not None:
            memory.category = category

        logger.info(f"Updated memory #{memory_id}")
        return True

    def delete_memory(self, memory_id: int) -> bool:
        """Delete (deactivate) a memory."""
        memory = self.get_memory(memory_id)
        if not memory:
            return False

        memory.is_active = False
        logger.info(f"Deleted memory #{memory_id}")
        return True

    def forget_user_memory(self, user_id: int) -> int:
        """Forget all memories for a user. Returns count deleted."""
        count = 0
        for memory_id, memory in list(self._memories.items()):
            if memory.user_id == user_id and memory.is_active:
                memory.is_active = False
                count += 1

        logger.info(f"Forgot {count} memories for user {user_id}")
        return count

    def get_relevant_memories(
        self,
        user_id: Optional[int],
        query: str,
    ) -> list[Memory]:
        """
        Get memories relevant to a query.
        Simple keyword matching for Phase 1.
        Phase 2+: Gemini-powered relevance matching.
        """
        relevant = []

        # Get memories for the user and shared memories
        if user_id:
            candidates = self.get_memories_for_user(user_id) + self.get_shared_memories()
        else:
            candidates = self.get_all_active_memories()

        query_words = set(query.lower().split())

        for memory in candidates:
            memory_words = set(memory.content.lower().split())
            # Simple overlap check
            if query_words & memory_words:
                relevant.append(memory)

        return relevant

    def format_memories_for_context(
        self,
        user_id: Optional[int],
        max_memories: int = 5,
    ) -> str:
        """Format memories for inclusion in AI context."""
        memories = self.get_all_active_memories()
        user_memories = [m for m in memories if m.user_id == user_id]
        shared_memories = [m for m in memories if m.user_id is None]

        # Combine, preferring user-specific memories
        combined = user_memories[:max_memories // 2] + shared_memories[:max_memories // 2]
        combined = combined[:max_memories]

        if not combined:
            return ""

        result = "MEMORY CONTEXT:\n"
        for memory in combined:
            user_label = f" (user #{memory.user_id})" if memory.user_id else " (shared)"
            result += f"- [{memory.category}]{user_label}: {memory.content}\n"

        return result

    def clear_all(self) -> int:
        """Clear all memories. Returns count cleared."""
        count = len(self._memories)
        self._memories.clear()
        self._next_id = 1
        logger.info(f"Cleared all {count} memories")
        return count
