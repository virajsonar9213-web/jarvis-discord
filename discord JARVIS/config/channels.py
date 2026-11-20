"""
JARVIS Channel Configuration

Manages which servers and channels JARVIS can access.
Configuration is stored in the database.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChannelConfig:
    """Configuration for a single channel."""

    channel_id: int
    guild_id: int
    can_read: bool = True
    can_respond: bool = False
    should_ignore: bool = False
    is_private_assistant: bool = False
    monitored_users: list[int] = field(default_factory=list)
    ignored_users: list[int] = field(default_factory=list)


@dataclass
class ServerConfig:
    """Configuration for a single server (guild)."""

    guild_id: int
    enabled: bool = False
    monitored_channels: list[int] = field(default_factory=list)
    respond_channels: list[int] = field(default_factory=list)
    ignored_channels: list[int] = field(default_factory=list)
    monitored_users: list[int] = field(default_factory=list)
    notification_channels: list[int] = field(default_factory=list)


class ChannelConfigManager:
    """
    Manages channel and server configurations.
    In Phase 1, this uses in-memory defaults.
    In later phases, configuration moves to the database.
    """

    def __init__(self):
        self.servers: dict[int, ServerConfig] = {}
        self.channels: dict[int, ChannelConfig] = {}

    def get_server(self, guild_id: int) -> Optional[ServerConfig]:
        """Get server config by guild ID."""
        return self.servers.get(guild_id)

    def get_channel(self, channel_id: int) -> Optional[ChannelConfig]:
        """Get channel config by channel ID."""
        return self.channels.get(channel_id)

    def is_channel_monitored(self, channel_id: int) -> bool:
        """Check if a channel is monitored for messages."""
        config = self.get_channel(channel_id)
        if config is None:
            return False
        return config.can_read and not config.should_ignore

    def is_channel_respond_enabled(self, channel_id: int) -> bool:
        """Check if JARVIS can respond in a channel."""
        config = self.get_channel(channel_id)
        if config is None:
            return False
        return config.can_respond

    def should_ignore_channel(self, channel_id: int) -> bool:
        """Check if a channel should be ignored."""
        config = self.get_channel(channel_id)
        if config is None:
            return False
        return config.should_ignore

    def is_user_monitored(self, channel_id: int, user_id: int) -> bool:
        """
        Check if messages from a user in a channel should be monitored.
        Returns True if the user is in the monitored list or if no users are specified.
        """
        config = self.get_channel(channel_id)
        if config is None:
            return False
        if not config.monitored_users:
            # No specific users configured: monitor all (subject to channel settings)
            return config.can_read and not config.should_ignore
        return user_id in config.monitored_users

    def is_user_ignored(self, channel_id: int, user_id: int) -> bool:
        """Check if a user should be ignored in a channel."""
        config = self.get_channel(channel_id)
        if config is None:
            return False
        return user_id in config.ignored_users

    # Phase 3+ will add database persistence for these methods
