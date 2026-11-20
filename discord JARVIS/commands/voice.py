"""
JARVIS /voice Command

Controls Discord voice channel features.
Phase 5 feature - currently a placeholder.
"""

from discord import Interaction, VoiceChannel

from utils.logger import get_logger

logger = get_logger("commands.voice")


async def handle_voice(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /voice slash command.

    Usage:
    - /voice join channel:#voice-channel
    - /voice leave
    - /voice speak text:"..."
    - /voice stop
    """
    logger.info(f"/voice command from {interaction.user.name}")

    # Check permission for voice features
    from config.permissions import Permissions
    permissions = Permissions()
    if not permissions.can_use_voice(interaction.user):
        await interaction.response.send_message(
            "You don't have permission to use voice features.",
            ephemeral=True,
        )
        return

    # Extract subcommand
    subcommand = None
    for option in options:
        if option.get("name") == "action":
            subcommand = option.get("value")
            break

    if not subcommand:
        await interaction.response.send_message(
            "Usage: `/voice join channel:#voice` or `/voice leave` or `/voice speak text:\"...\"`",
            ephemeral=True,
        )
        return

    voice_service = bot.voice

    if subcommand == "join":
        await handle_voice_join(bot, interaction, options, voice_service)
    elif subcommand == "leave":
        await handle_voice_leave(bot, interaction, voice_service)
    elif subcommand == "speak":
        await handle_voice_speak(bot, interaction, options, voice_service)
    elif subcommand == "stop":
        await handle_voice_stop(bot, interaction, voice_service)
    else:
        await interaction.response.send_message(
            f"Unknown voice action: {subcommand}",
            ephemeral=True,
        )


async def handle_voice_join(bot, interaction: Interaction, options: list, voice_service) -> None:
    """Join a voice channel."""
    channel_id = None

    for option in options:
        if option.get("name") == "channel" and option.get("value"):
            channel_id = int(option.get("value")) if isinstance(option.get("value"), str) else option.get("value")
            break

    if not channel_id:
        # Try to use current channel's voice channel
        guild = interaction.guild
        if guild and guild.voice_client:
            channel_id = guild.voice_client.channel.id

    if not channel_id:
        await interaction.response.send_message(
            "Please specify a voice channel to join.",
            ephemeral=True,
        )
        return

    channel = bot.get_channel(channel_id)
    if not isinstance(channel, VoiceChannel):
        await interaction.response.send_message(
            "Invalid voice channel specified.",
            ephemeral=True,
        )
        return

    # Check bot permissions
    if not channel.permissions_for(interaction.guild.me).connect:
        await interaction.response.send_message(
            "I don't have permission to join that voice channel.",
            ephemeral=True,
        )
        return

    success = await voice_service.join_channel(channel)

    if success:
        await interaction.response.send_message(
            f"🔊 Joined {channel.name}!",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Failed to join voice channel.",
            ephemeral=True,
        )


async def handle_voice_leave(bot, interaction: Interaction, voice_service) -> None:
    """Leave the current voice channel."""
    success = await voice_service.leave_channel()

    if success:
        await interaction.response.send_message(
            "🔇 Left voice channel.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Not currently in a voice channel.",
            ephemeral=True,
        )


async def handle_voice_speak(bot, interaction: Interaction, options: list, voice_service) -> None:
    """Speak text using TTS."""
    text = None

    for option in options:
        if option.get("name") == "text":
            text = option.get("value")
            break

    if not text:
        await interaction.response.send_message(
            "Please provide text to speak.",
            ephemeral=True,
        )
        return

    if not voice_service.is_connected:
        await interaction.response.send_message(
            "I'm not in a voice channel. Use `/voice join` first.",
            ephemeral=True,
        )
        return

    success = await voice_service.speak(text)

    if success:
        await interaction.response.send_message(
            f"🔊 Speaking: \"{text[:50]}{'...' if len(text) > 50 else ''}\"",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Failed to speak.",
            ephemeral=True,
        )


async def handle_voice_stop(bot, interaction: Interaction, voice_service) -> None:
    """Stop speaking."""
    success = await voice_service.stop_speaking()

    if success:
        await interaction.response.send_message(
            "🔇 Stopped speaking.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Not currently speaking.",
            ephemeral=True,
        )


async def setup_voice(bot) -> None:
    """Register the voice command with Discord."""
    logger.info("Voice command registered")
