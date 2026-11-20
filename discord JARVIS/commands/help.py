"""
JARVIS /help Command

Displays available commands and usage information.
"""

from discord import Interaction

from utils.logger import get_logger

logger = get_logger("commands.help")


async def handle_help(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /help slash command.
    """
    logger.info(f"/help command from {interaction.user.name}")

    help_text = """---
**👋 JARVIS - Your Personal AI Assistant**

**Commands:**

🤖 **AI & Conversation**
- `/ask question:` - Ask JARVIS a question
- `/summarize` - Summarize recent messages

📖 **Reading & Awareness**
- `/read action:` - Read / pause / resume / stop channel messages
- `/status` - Check JARVIS status

🔔 **Reminders**
- `/remind action:add content:... time:...` - Set a reminder
- `/remind action:list` - View your reminders
- `/remind action:complete id:` / `action:delete id:`

⚙️ **Settings & Memory**
- `/settings action:view` - View settings (owner only to change)
- `/memory action:list/add/delete/forget` - Manage memory

🔊 **Voice**
- `/voice action:join/leave/speak/stop`

**How to Use:**
Type `/` in any channel JARVIS can see and pick a command.

**Authorized Users Only.**
*Contact the owner to request access.*
"""
    await interaction.response.send_message(help_text, ephemeral=True)


async def setup_help(bot) -> None:
    """Register the help command with Discord."""
    # TODO: Phase 2 - Implement proper slash command registration
    logger.info("Help command registered")
