"""
JARVIS /read Command

Controls message reading functionality.
"""

from discord import Interaction, TextChannel

from utils.logger import get_logger

logger = get_logger("commands.read")


async def handle_read(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /read slash command.

    Usage:
    - /read start channel:#general
    - /read stop
    - /read pause
    - /read resume
    - /read channel:#new-channel
    """
    logger.info(f"/read command from {interaction.user.name}")

    # Extract subcommand
    subcommand = None
    for option in options:
        if option.get("name") == "action":
            subcommand = option.get("value")
            break

    if not subcommand:
        await interaction.response.send_message(
            "Usage: `/read start channel:#general` or `/read stop` or `/read pause` or `/read resume`",
            ephemeral=True,
        )
        return

    message_reader = bot.message_reader

    if subcommand == "start":
        await handle_read_start(bot, interaction, options)
    elif subcommand == "stop":
        await handle_read_stop(bot, interaction)
    elif subcommand == "pause":
        await handle_read_pause(bot, interaction)
    elif subcommand == "resume":
        await handle_read_resume(bot, interaction)
    elif subcommand == "channel":
        await handle_read_channel(bot, interaction, options)
    else:
        await interaction.response.send_message(
            f"Unknown read action: {subcommand}",
            ephemeral=True,
        )


async def handle_read_start(bot, interaction: Interaction, options: list) -> None:
    """Start reading messages from a channel."""
    channel_id = None

    for option in options:
        if option.get("name") == "channel" and option.get("value"):
            channel_id = int(option.get("value")) if isinstance(option.get("value"), str) else option.get("value")
            break

    if not channel_id and interaction.channel:
        channel_id = interaction.channel.id

    if not channel_id:
        await interaction.response.send_message(
            "Please specify a channel to read from.",
            ephemeral=True,
        )
        return

    channel = bot.get_channel(channel_id)
    if not isinstance(channel, TextChannel):
        await interaction.response.send_message(
            "Invalid channel specified.",
            ephemeral=True,
        )
        return

    success = await bot.message_reader.start_reading(channel)

    if success:
        await interaction.response.send_message(
            f"🔊 Now reading messages from {channel.mention}.\n"
            f"Use `/read pause` to pause, `/read resume` to resume, `/read stop` to stop.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Already reading from a channel. Use `/read stop` first.",
            ephemeral=True,
        )


async def handle_read_stop(bot, interaction: Interaction) -> None:
    """Stop reading messages."""
    success = await bot.message_reader.stop_reading()

    if success:
        await interaction.response.send_message(
            "🔇 Stopped reading messages.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Not currently reading.",
            ephemeral=True,
        )


async def handle_read_pause(bot, interaction: Interaction) -> None:
    """Pause reading messages."""
    success = await bot.message_reader.pause_reading()

    if success:
        await interaction.response.send_message(
            "⏸️ Paused reading. Use `/read resume` to continue.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Not currently reading or already paused.",
            ephemeral=True,
        )


async def handle_read_resume(bot, interaction: Interaction) -> None:
    """Resume reading messages."""
    success = await bot.message_reader.resume_reading()

    if success:
        await interaction.response.send_message(
            "▶️ Resumed reading.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Not paused or not reading.",
            ephemeral=True,
        )


async def handle_read_channel(bot, interaction: Interaction, options: list) -> None:
    """Change the channel being read."""
    channel_id = None

    for option in options:
        if option.get("name") == "channel" and option.get("value"):
            channel_id = int(option.get("value")) if isinstance(option.get("value"), str) else option.get("value")
            break

    if not channel_id:
        await interaction.response.send_message(
            "Please specify a channel.",
            ephemeral=True,
        )
        return

    channel = bot.get_channel(channel_id)
    if not isinstance(channel, TextChannel):
        await interaction.response.send_message(
            "Invalid channel specified.",
            ephemeral=True,
        )
        return

    success = await bot.message_reader.set_channel(channel)

    if success:
        await interaction.response.send_message(
            f"📻 Now reading from {channel.mention}.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Failed to change channel.",
            ephemeral=True,
        )


async def setup_read(bot) -> None:
    """Register the read command with Discord."""
    logger.info("Read command registered")
