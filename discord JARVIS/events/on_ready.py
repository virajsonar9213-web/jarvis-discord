"""
JARVIS on_ready Event Handler

Handles the bot's ready event.
"""

from discord import Client

from utils.logger import get_logger

logger = get_logger("events.on_ready")


async def on_ready(bot: Client) -> None:
    """
    Called when the bot is ready and connected to Discord.
    """
    logger.info(f"JARVIS is ready! Logged in as {bot.user}")
    logger.info(f"Slash commands registered: {len(bot.tree.get_commands())}")

    # Log server count
    servers = bot.guilds
    logger.info(f"Connected to {len(servers)} server(s)")

    for guild in servers:
        logger.info(f"  - {guild.name} (ID: {guild.id})")
