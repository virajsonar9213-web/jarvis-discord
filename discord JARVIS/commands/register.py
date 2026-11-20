"""
JARVIS Slash Command Registration

Registers all JARVIS slash commands with Discord's application command tree.
Each command delegates to the matching handler in commands/.
"""

from typing import Optional

import discord
from discord import app_commands

from config.permissions import Permissions
from utils.logger import get_logger

logger = get_logger("commands.register")


async def setup_commands(bot) -> None:
    """Register all slash commands on the bot's command tree."""
    tree = bot.tree

    async def guard(interaction: discord.Interaction) -> bool:
        """Reject anyone who is not the owner or authorized friend."""
        if not Permissions.is_authorized(interaction.user):
            await interaction.response.send_message(
                "You are not authorized to use JARVIS.",
                ephemeral=True,
            )
            return False
        return True

    # ---------------------------------------------------------------- /ask
    @tree.command(name="ask", description="Ask JARVIS a question")
    @app_commands.describe(question="What you want to ask JARVIS")
    async def ask(interaction: discord.Interaction, question: str) -> None:
        if not await guard(interaction):
            return
        from commands.ask import handle_ask
        await handle_ask(bot, interaction, [{"name": "question", "value": question}])

    # --------------------------------------------------------------- /help
    @tree.command(name="help", description="Show JARVIS commands and usage")
    async def help_cmd(interaction: discord.Interaction) -> None:
        if not await guard(interaction):
            return
        from commands.help import handle_help
        await handle_help(bot, interaction, [])

    # ------------------------------------------------------------- /status
    @tree.command(name="status", description="Show JARVIS status")
    async def status(interaction: discord.Interaction) -> None:
        if not await guard(interaction):
            return
        from commands.status import handle_status
        await handle_status(bot, interaction, [])

    # ---------------------------------------------------------- /summarize
    @tree.command(name="summarize", description="Summarize recent messages in a channel")
    @app_commands.describe(
        channel="Channel to summarize (defaults to the current channel)",
        limit="How many messages to analyze (default 50)",
    )
    async def summarize(
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        limit: Optional[int] = 50,
    ) -> None:
        if not await guard(interaction):
            return
        from commands.summarize import handle_summarize
        options = []
        if channel is not None:
            options.append({"name": "channel", "value": channel.id})
        options.append({"name": "limit", "value": limit or 50})
        await handle_summarize(bot, interaction, options)

    # --------------------------------------------------------------- /read
    @tree.command(name="read", description="Control message reading")
    @app_commands.describe(action="What to do", channel="Channel for start/channel")
    @app_commands.choices(action=[
        app_commands.Choice(name="start", value="start"),
        app_commands.Choice(name="stop", value="stop"),
        app_commands.Choice(name="pause", value="pause"),
        app_commands.Choice(name="resume", value="resume"),
        app_commands.Choice(name="change channel", value="channel"),
    ])
    async def read(
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        channel: Optional[discord.TextChannel] = None,
    ) -> None:
        if not await guard(interaction):
            return
        from commands.read import handle_read
        options = [{"name": "action", "value": action.value}]
        if channel is not None:
            options.append({"name": "channel", "value": channel.id})
        await handle_read(bot, interaction, options)

    # ------------------------------------------------------------- /remind
    @tree.command(name="remind", description="Manage your reminders")
    @app_commands.describe(
        action="What to do",
        content="Reminder text (for add)",
        time="When, e.g. '1 hour', 'tomorrow', '2026-12-01 09:00' (for add)",
        id="Reminder ID (for complete/delete)",
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="complete", value="complete"),
        app_commands.Choice(name="delete", value="delete"),
    ])
    async def remind(
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        content: Optional[str] = None,
        time: Optional[str] = None,
        id: Optional[int] = None,
    ) -> None:
        if not await guard(interaction):
            return
        from commands.reminder import handle_remind
        options = [{"name": "action", "value": action.value}]
        if content is not None:
            options.append({"name": "content", "value": content})
        if time is not None:
            options.append({"name": "time", "value": time})
        if id is not None:
            options.append({"name": "id", "value": id})
        await handle_remind(bot, interaction, options)

    # ----------------------------------------------------------- /settings
    @tree.command(name="settings", description="View or change JARVIS settings")
    @app_commands.describe(
        action="What to do",
        key="Setting name (for set)",
        value="New value (for set)",
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="reset", value="reset"),
    ])
    async def settings(
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        key: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        if not await guard(interaction):
            return
        from commands.settings import handle_settings
        options = [{"name": "action", "value": action.value}]
        if key is not None:
            options.append({"name": "key", "value": key})
        if value is not None:
            options.append({"name": "value", "value": value})
        await handle_settings(bot, interaction, options)

    # ------------------------------------------------------------- /memory
    @tree.command(name="memory", description="Manage JARVIS's memory")
    @app_commands.describe(
        action="What to do",
        content="Memory text (for add)",
        category="Category (for add), e.g. general, preference, project",
        id="Memory ID (for delete)",
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="delete", value="delete"),
        app_commands.Choice(name="forget", value="forget"),
    ])
    async def memory(
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        content: Optional[str] = None,
        category: Optional[str] = None,
        id: Optional[int] = None,
    ) -> None:
        if not await guard(interaction):
            return
        from commands.memory import handle_memory
        options = [{"name": "action", "value": action.value}]
        if content is not None:
            options.append({"name": "content", "value": content})
        if category is not None:
            options.append({"name": "category", "value": category})
        if id is not None:
            options.append({"name": "id", "value": id})
        await handle_memory(bot, interaction, options)

    # -------------------------------------------------------------- /voice
    @tree.command(name="voice", description="Control JARVIS voice features")
    @app_commands.describe(
        action="What to do",
        channel="Voice channel (for join)",
        text="Text to speak (for speak)",
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="join", value="join"),
        app_commands.Choice(name="leave", value="leave"),
        app_commands.Choice(name="speak", value="speak"),
        app_commands.Choice(name="stop", value="stop"),
    ])
    async def voice(
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        channel: Optional[discord.VoiceChannel] = None,
        text: Optional[str] = None,
    ) -> None:
        if not await guard(interaction):
            return
        from commands.voice import handle_voice
        options = [{"name": "action", "value": action.value}]
        if channel is not None:
            options.append({"name": "channel", "value": channel.id})
        if text is not None:
            options.append({"name": "text", "value": text})
        await handle_voice(bot, interaction, options)

    logger.info("Registered %d slash commands", len(tree.get_commands()))
