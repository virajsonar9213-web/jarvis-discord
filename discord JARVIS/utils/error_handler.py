"""
JARVIS Error Handler

Centralized error handling for Discord events and commands.
Handles API errors, rate limits, and other exceptions gracefully.
"""

import traceback
from typing import Any

from discord import Interaction, Message
from utils.logger import get_logger

logger = get_logger("error_handler")


class ErrorHandler:
    """Handles errors throughout the bot."""

    @staticmethod
    async def handle_command_error(
        error: Exception,
        interaction: Interaction | None = None,
        context: str = "",
    ) -> None:
        """
        Handle errors that occur during command execution.
        Logs the error and sends a user-friendly response if possible.
        """
        error_msg = f"Command error: {type(error).__name__}: {error}"
        if context:
            error_msg = f"{context} - {error_msg}"

        logger.error(error_msg, exc_info=True)

        # Send response if interaction is available
        if interaction and interaction.response.is_done() is False:
            try:
                await interaction.response.send_message(
                    "I encountered an error processing your request. Please try again.",
                    ephemeral=True,
                )
            except Exception as e:
                logger.error(f"Failed to send error response: {e}")

    @staticmethod
    async def handle_event_error(
        error: Exception,
        event_name: str,
        message: Message | None = None,
    ) -> None:
        """
        Handle errors that occur during event processing.
        """
        error_msg = f"Event '{event_name}' error: {type(error).__name__}: {error}"
        logger.error(error_msg, exc_info=True)

    @staticmethod
    async def handle_api_error(
        error: Exception,
        operation: str = "API call",
    ) -> None:
        """
        Handle errors from external API calls (Gemini, Discord API, etc.).
        """
        error_msg = f"API error during {operation}: {type(error).__name__}: {error}"
        logger.error(error_msg, exc_info=True)

    @staticmethod
    def format_error_for_display(error: Exception) -> str:
        """
        Format an error for display to users.
        Returns a user-friendly error message without exposing internals.
        """
        error_type = type(error).__name__

        # Known error types with user-friendly messages
        error_messages = {
            "RateLimitError": "I'm being rate limited. Please wait a moment and try again.",
            "AuthenticationError": "There's an authentication issue. The bot may need to be reconfigured.",
            "PermissionError": "I don't have permission to perform that action here.",
            "TimeoutError": "The request timed out. Please try again.",
            "ConnectionError": "I'm having trouble connecting. Please try again.",
        }

        for key, message in error_messages.items():
            if key in error_type:
                return message

        return "Something went wrong. Please try again later."


async def safe_execute(func, *args, **kwargs) -> tuple[bool, Any]:
    """
    Safely execute an async function, catching all exceptions.
    Returns (success, result_or_none).
    """
    try:
        result = await func(*args, **kwargs)
        return True, result
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
        return False, None


async def safe_execute_sync(func, *args, **kwargs) -> tuple[bool, Any]:
    """
    Safely execute a sync function, catching all exceptions.
    Returns (success, result_or_none).
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
        return False, None
