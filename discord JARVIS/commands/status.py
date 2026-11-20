"""
JARVIS /status Command

Shows JARVIS's current status and statistics.
"""

from discord import Interaction

from utils.logger import get_logger

logger = get_logger("commands.status")


async def handle_status(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /status slash command.
    """
    logger.info(f"/status command from {interaction.user.name}")

    # Gather status information
    gemini_status = "✅ Connected" if (
        bot.gemini_client and bot.gemini_client.is_ready
    ) else "❌ Not connected"

    db_status = "✅ Connected" if bot.database else "❌ Not connected"

    memory_count = len(bot.memory_manager._memories) if bot.memory_manager else 0
    context_count = bot.context_manager.get_context_count() if bot.context_manager else 0

    status_text = f"""---
**📊 JARVIS Status**

| Component | Status |
|-----------|--------|
| **Bot** | ✅ Online |
| **AI (Gemini)** | {gemini_status} |
| **Database** | {db_status} |
| **Memory** | {memory_count} memories |
| **Contexts** | {context_count} active |

**Bot Info:**
- Name: {bot.user.name}
- ID: {bot.user.id}
- Logged in as: {bot.user.display_name}

*JARVIS is ready to assist.*
"""
    await interaction.response.send_message(status_text, ephemeral=True)


async def setup_status(bot) -> None:
    """Register the status command with Discord."""
    logger.info("Status command registered")
