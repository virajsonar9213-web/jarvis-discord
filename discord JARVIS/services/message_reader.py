"""
JARVIS Message Reader Service

Handles reading messages from Discord channels.
Supports /read start, /read stop, /read pause, /read resume, /read channel.
"""

import asyncio
from typing import Optional

from discord import TextChannel, Message

from utils.logger import get_logger

logger = get_logger("message_reader")


class MessageReaderService:
    """
    Service for reading messages aloud from Discord channels.
    Text-to-speech functionality will be added in Phase 5 (Voice).
    """

    def __init__(self):
        self.is_reading: bool = False
        self.is_paused: bool = False
        self.current_channel: Optional[TextChannel] = None
        self._stop_event: asyncio.Event = asyncio.Event()
        self._pause_event: asyncio.Event = asyncio.Event()
        self._pause_event.set()  # Start as not paused

    async def start_reading(self, channel: TextChannel) -> bool:
        """
        Start reading messages from a channel.
        Returns True if started successfully.
        """
        if self.is_reading:
            logger.info("Already reading from a channel")
            return False

        self.current_channel = channel
        self.is_reading = True
        self.is_paused = False
        self._stop_event.clear()
        self._pause_event.set()

        logger.info(f"Started reading from channel: {channel.id}")
        return True

    async def stop_reading(self) -> bool:
        """
        Stop reading messages.
        Returns True if stopped successfully.
        """
        if not self.is_reading:
            logger.info("Not currently reading")
            return False

        self._stop_event.set()
        self.is_reading = False
        self.is_paused = False
        self.current_channel = None

        logger.info("Stopped reading")
        return True

    async def pause_reading(self) -> bool:
        """Pause reading messages."""
        if not self.is_reading:
            logger.info("Not currently reading")
            return False

        self.is_paused = True
        self._pause_event.clear()

        logger.info("Paused reading")
        return True

    async def resume_reading(self) -> bool:
        """Resume reading messages."""
        if not self.is_reading or not self.is_paused:
            logger.info("Not paused or not reading")
            return False

        self.is_paused = False
        self._pause_event.set()

        logger.info("Resumed reading")
        return True

    async def set_channel(self, channel: TextChannel) -> bool:
        """
        Set the channel to read from.
        Can be called while reading to change channels.
        """
        self.current_channel = channel
        logger.info(f"Set reading channel to: {channel.id}")
        return True

    def should_read_message(self, message: Message, ignore_users: list[int]) -> bool:
        """
        Check if a message should be read.
        Considers whether reading is active, not paused, and user is not ignored.
        """
        if not self.is_reading or self.is_paused:
            return False
        if message.author.id in ignore_users:
            return False
        return True

    async def wait_for_next_message(self, timeout: float = 1.0) -> bool:
        """
        Wait for the next message to be read.
        Returns False if stopped.
        """
        # Wait for either a stop signal or a message
        done, _ = await asyncio.wait(
            [self._stop_event.wait(), self._pause_event.wait()],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if self._stop_event.is_set():
            return False

        if not self._pause_event.is_set():
            # Paused, wait more
            return await self.wait_for_next_message(timeout)

        return True

    def is_active(self) -> bool:
        """Check if the message reader is actively reading."""
        return self.is_reading and not self.is_paused
