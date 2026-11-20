"""
JARVIS User Authorization System

Only two Discord users can control JARVIS:
- Owner (full access)
- Authorized Friend (configurable access)

All authorization is checked server-side before executing commands.
Unauthorized users receive a simple access-denied response.
"""

from discord import User
from config.settings import Settings


class Permissions:
    """
    Permission categories:
    | Permission            | Owner | Friend |
    |-----------------------|-------|--------|
    | Chat with AI         | Yes   | Yes    |
    | Use commands         | Yes   | Yes    |
    | Ask for summaries    | Yes   | Yes    |
    | Access selected channels | Yes | Configurable |
    | Use voice features   | Yes   | Yes    |
    | Request messages     | Yes   | Yes    |
    | Approve actions      | Yes   | Configurable |
    | Change bot settings  | Yes   | No (default) |
    | Manage memory        | Yes   | Configurable |
    """

    @staticmethod
    def is_authorized(user: User) -> bool:
        """Check if a Discord user is authorized to use JARVIS."""
        if user.id == Settings.OWNER_USER_ID:
            return True
        if user.id == Settings.FRIEND_USER_ID:
            return True
        return False

    @staticmethod
    def is_owner(user: User) -> bool:
        """Check if the user is the owner."""
        return user.id == Settings.OWNER_USER_ID

    @staticmethod
    def is_friend(user: User) -> bool:
        """Check if the user is the authorized friend."""
        return user.id == Settings.FRIEND_USER_ID

    @staticmethod
    def can_access_channel(user: User, channel_id: int) -> bool:
        """
        Check if user can access a specific channel.
        Owner: always yes.
        Friend: configurable per channel (default: no unless explicitly granted).
        """
        if Permissions.is_owner(user):
            return True
        # Friend channel access: configurable in database
        # For now, default is no for friend unless configured
        return False

    @staticmethod
    def can_approve_actions(user: User) -> bool:
        """Check if user can approve actions (message sending, moderation, etc.)."""
        if Permissions.is_owner(user):
            return True
        # Friend approval: configurable, default no
        return False

    @staticmethod
    def can_change_settings(user: User) -> bool:
        """Check if user can change bot settings."""
        return Permissions.is_owner(user)

    @staticmethod
    def can_manage_memory(user: User) -> bool:
        """Check if user can manage memory (add/update/delete memories)."""
        if Permissions.is_owner(user):
            return True
        # Friend memory management: configurable, default no
        return False

    @staticmethod
    def get_permission_status(user: User) -> dict:
        """Get the permission status for a user."""
        is_owner = Permissions.is_owner(user)
        is_friend = Permissions.is_friend(user)

        return {
            "is_authorized": is_owner or is_friend,
            "is_owner": is_owner,
            "is_friend": is_friend,
            "can_chat": is_owner or is_friend,
            "can_use_commands": is_owner or is_friend,
            "can_summarize": is_owner or is_friend,
            "can_access_channels": is_owner,  # Friend: configurable
            "can_use_voice": is_owner or is_friend,
            "can_request_messages": is_owner or is_friend,
            "can_approve_actions": is_owner,  # Friend: configurable
            "can_change_settings": is_owner,
            "can_manage_memory": is_owner,  # Friend: configurable
        }
