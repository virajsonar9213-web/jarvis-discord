"""
JARVIS Message Sender Service

Handles sending messages through JARVIS's bot account.
Supports the draft → approve → send workflow.
"""

from typing import Optional

from discord import TextChannel, Embed

from utils.logger import get_logger

logger = get_logger("message_sender")


class MessageSenderService:
    """
    Service for sending messages as JARVIS.
    Implements the approval workflow for consequential actions.
    """

    def __init__(self):
        self._pending_messages: list[dict] = []

    def create_draft(
        self,
        channel_id: int,
        channel_name: str,
        content: str,
        is_embed: bool = False,
        embed_data: Optional[dict] = None,
    ) -> dict:
        """
        Create a message draft for approval.
        Returns the draft data.
        """
        draft = {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "content": content,
            "is_embed": is_embed,
            "embed_data": embed_data,
            "created_at": "pending",  # Will be set by caller
        }
        self._pending_messages.append(draft)
        logger.info(f"Created draft for channel {channel_id}: {channel_name}")
        return draft

    async def send_message(
        self,
        channel: TextChannel,
        content: str,
        embed: Optional[Embed] = None,
    ) -> Optional[int]:
        """
        Send a message to a channel.
        Returns the message ID if successful, None otherwise.
        """
        try:
            if embed:
                message = await channel.send(content=content, embed=embed)
            else:
                message = await channel.send(content=content)
            logger.info(f"Sent message to {channel.id}: {message.id}")
            return message.id
        except Exception as e:
            logger.error(f"Failed to send message to {channel.id}: {e}")
            return None

    async def delete_message(self, channel: TextChannel, message_id: int) -> bool:
        """
        Delete a message JARVIS sent.
        Returns True if successful.
        """
        try:
            message = await channel.fetch_message(message_id)
            await message.delete()
            logger.info(f"Deleted message {message_id} in {channel.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            return False

    async def edit_message(
        self,
        channel: TextChannel,
        message_id: int,
        new_content: str,
    ) -> bool:
        """
        Edit a message JARVIS sent.
        Returns True if successful.
        """
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(content=new_content)
            logger.info(f"Edited message {message_id} in {channel.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to edit message {message_id}: {e}")
            return False

    def get_pending_drafts(self) -> list[dict]:
        """Get all pending message drafts."""
        return self._pending_messages.copy()

    def clear_draft(self, draft_id: int) -> bool:
        """Remove a draft by index."""
        if 0 <= draft_id < len(self._pending_messages):
            self._pending_messages.pop(draft_id)
            return True
        return False
