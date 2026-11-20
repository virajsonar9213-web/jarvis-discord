"""
JARVIS Notification Service

Handles proactive notifications to authorized users.
Supports keyword alerts, mentions, and scheduled reminders.
"""

from dataclasses import dataclass, field
from typing import Optional

from discord import TextChannel, User

from utils.logger import get_logger

logger = get_logger("notifications")


@dataclass
class NotificationConfig:
    """Configuration for a user's notifications."""

    user_id: int
    enabled: bool = True
    quiet_hours_start: Optional[str] = None  # e.g., "22:00"
    quiet_hours_end: Optional[str] = None  # e.g., "08:00"
    keyword_filters: list[str] = field(default_factory=list)
    notification_channels: list[int] = field(default_factory=list)


class NotificationService:
    """
    Service for sending notifications to authorized users.
    """

    def __init__(self):
        self._configs: dict[int, NotificationConfig] = {}

    def configure_user(
        self,
        user_id: int,
        enabled: bool = True,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None,
        keyword_filters: Optional[list[str]] = None,
        notification_channels: Optional[list[int]] = None,
    ) -> NotificationConfig:
        """Configure notification settings for a user."""
        config = NotificationConfig(
            user_id=user_id,
            enabled=enabled,
            quiet_hours_start=quiet_hours_start,
            quiet_hours_end=quiet_hours_end,
            keyword_filters=keyword_filters or [],
            notification_channels=notification_channels or [],
        )
        self._configs[user_id] = config
        logger.info(f"Configured notifications for user {user_id}")
        return config

    def get_config(self, user_id: int) -> Optional[NotificationConfig]:
        """Get notification config for a user."""
        return self._configs.get(user_id)

    async def notify_user(
        self,
        user: User,
        message: str,
        channel: Optional[TextChannel] = None,
    ) -> bool:
        """
        Send a notification to a user.
        Returns True if sent successfully.
        """
        config = self.get_config(user.id)
        if config and not config.enabled:
            logger.info(f"Notifications disabled for user {user.id}")
            return False

        # Check quiet hours
        if config and self._in_quiet_hours(config):
            logger.info(f"In quiet hours for user {user.id}, suppressing notification")
            return False

        try:
            if channel:
                await channel.send(f"{user.mention} {message}")
            else:
                await user.send(message)
            logger.info(f"Sent notification to {user.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to {user.id}: {e}")
            return False

    async def notify_mention(
        self,
        mentioned_user: User,
        context: str,
        channel: TextChannel,
    ) -> None:
        """Notify a user they were mentioned."""
        await self.notify_user(
            mentioned_user,
            f"You were mentioned in {channel.mention}: {context}",
            channel,
        )

    async def notify_keyword_alert(
        self,
        user: User,
        keyword: str,
        message_content: str,
        channel: TextChannel,
    ) -> None:
        """Notify a user about a keyword match."""
        await self.notify_user(
            user,
            f"Keyword '{keyword}' mentioned in {channel.mention}: {message_content[:200]}",
            channel,
        )

    async def notify_important_message(
        self,
        user: User,
        message_preview: str,
        channel: TextChannel,
    ) -> None:
        """Notify a user about an important message."""
        await self.notify_user(
            user,
            f"Important message in {channel.mention}: {message_preview[:200]}",
            channel,
        )

    def _in_quiet_hours(self, config: NotificationConfig) -> bool:
        """Check if we're currently in the user's quiet hours."""
        if not config.quiet_hours_start or not config.quiet_hours_end:
            return False

        from datetime import datetime

        now = datetime.now()
        current_hour = now.hour

        try:
            start_hour = int(config.quiet_hours_start.split(":")[0])
            end_hour = int(config.quiet_hours_end.split(":")[0])

            if start_hour < end_hour:
                return start_hour <= current_hour < end_hour
            else:
                # Quiet hours cross midnight
                return current_hour >= start_hour or current_hour < end_hour
        except (ValueError, IndexError):
            return False

    async def send_error_notification(self, user: User, error_message: str) -> None:
        """Send an error/service notification to the owner."""
        await self.notify_user(
            user,            f"⚠️ JARVIS Alert: {error_message}",
        )