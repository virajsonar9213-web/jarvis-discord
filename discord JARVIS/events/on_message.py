"""
JARVIS on_message Event Handler

Handles incoming Discord messages.
"""

from discord import Message

from utils.logger import get_logger

logger = get_logger("events.on_message")


async def on_message(bot, message: Message) -> None:
    """
    Handle an incoming message.

    Checks authorization, handles mentions, and routes to appropriate handlers.
    """
    # Ignore bot messages
    if message.author.bot:
        return

    # Check authorization
    from config.permissions import Permissions

    permissions = Permissions()
    if not permissions.is_authorized(message.author):
        logger.debug(f"Unauthorized user {message.author.id} in #{message.channel.name}")
        return

    logger.debug(f"Processing message from {message.author.name} in #{message.channel.name}")

    try:
        # Check if JARVIS is mentioned
        if bot.user in message.mentions:
            await handle_mention(bot, message)
            return

        # Check for command prefix
        if message.content.startswith("!"):
            await handle_command(bot, message)
            return

        # Check for natural conversation (Phase 3+)
        await handle_natural_conversation(bot, message)

    except Exception as e:
        from utils.error_handler import ErrorHandler
        error_handler = ErrorHandler()
        await error_handler.handle_event_error(e, "on_message", message)


async def handle_mention(bot, message: Message) -> None:
    """Handle a mention of JARVIS."""
    logger.info(f"JARVIS mentioned by {message.author.name} in #{message.channel.name}")

    # Get the content without the mention
    content = message.content.replace(f"<@{bot.user.id}>", "").strip()

    if not content:
        # Just a mention, no message
        await message.channel.send(f"Hello {message.author.display_name}. How can I assist you?")
        return

    # TODO: Phase 2 - route to Gemini for response
    # For now, just acknowledge
    await message.channel.send(f"I've received your message, {message.author.display_name}. Processing...")


async def handle_command(bot, message: Message) -> None:
    """Handle a command message (starting with !)."""
    command = message.content[1:].split()[0].lower()
    args = message.content[1:].split()[1:] if len(message.content) > 1 else []

    logger.info(f"Command '{command}' from {message.author.name} with args: {args}")

    # Simple command handler for Phase 1
    from bot import JARVISBot

    if isinstance(bot, JARVISBot):
        await bot._handle_command(message)
    else:
        # Fallback for direct message handling
        await message.channel.send(f"Command received: {command}")


async def handle_natural_conversation(bot, message: Message) -> None:
    """Handle natural conversation in configured channels."""
    # Phase 1: No automatic responses in natural conversation
    # Phase 3+ will implement channel-based conversation
    logger.debug(f"Natural conversation from {message.author.name}: {message.content[:50]}...")

    # Check if this channel is configured for responses
    from config.channels import ChannelConfigManager

    config_manager = ChannelConfigManager()
    if config_manager.is_channel_respond_enabled(message.channel.id):
        # Will be handled by Gemini in Phase 3+
        pass
