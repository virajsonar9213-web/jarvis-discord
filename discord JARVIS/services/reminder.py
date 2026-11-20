"""
JARVIS Reminder Service

Manages user reminders and tasks.
Persists to SQLite database.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from utils.logger import get_logger

logger = get_logger("reminder")


@dataclass
class Reminder:
    """A user reminder/task."""

    id: int
    user_id: int
    content: str
    scheduled_for: datetime
    is_completed: bool = False
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ReminderService:
    """
    Service for managing reminders and tasks.
    Phase 1: In-memory storage.
    Phase 2+: Database persistence with scheduled notifications.
    """

    def __init__(self):
        self._reminders: dict[int, Reminder] = {}
        self._next_id: int = 1

    def add_reminder(
        self,
        user_id: int,
        content: str,
        scheduled_for: datetime,
    ) -> Reminder:
        """Add a new reminder."""
        reminder = Reminder(
            id=self._next_id,
            user_id=user_id,
            content=content,
            scheduled_for=scheduled_for,
        )
        self._reminders[self._next_id] = reminder
        self._next_id += 1

        logger.info(f"Added reminder #{reminder.id} for user {user_id}")
        return reminder

    def get_user_reminders(self, user_id: int) -> list[Reminder]:
        """Get all reminders for a user."""
        return [
            r for r in self._reminders.values()
            if r.user_id == user_id
        ]

    def get_pending_reminders(self, user_id: int) -> list[Reminder]:
        """Get pending (not completed) reminders for a user."""
        return [
            r for r in self._get_user_reminders(user_id)
            if not r.is_completed
        ]

    def _get_user_reminders(self, user_id: int) -> list[Reminder]:
        """Internal method to get all reminders for a user."""
        return [r for r in self._reminders.values() if r.user_id == user_id]

    def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        """Get a specific reminder by ID."""
        return self._reminders.get(reminder_id)

    def complete_reminder(self, reminder_id: int) -> bool:
        """Mark a reminder as completed."""
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return False

        reminder.is_completed = True
        logger.info(f"Completed reminder #{reminder_id}")
        return True

    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder."""
        if reminder_id in self._reminders:
            del self._reminders[reminder_id]
            logger.info(f"Deleted reminder #{reminder_id}")
            return True
        return False

    def get_due_reminders(self) -> list[Reminder]:
        """Get all reminders that are due now."""
        now = datetime.now()
        return [
            r for r in self._reminders.values()
            if not r.is_completed and r.scheduled_for <= now
        ]

    def list_all(self) -> list[Reminder]:
        """List all reminders (for admin/display)."""
        return list(self._reminders.values())
