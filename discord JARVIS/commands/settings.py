"""
JARVIS /settings Command

Manages bot settings for authorized users.
"""

from discord import Interaction

from utils.logger import get_logger

logger = get_logger("commands.settings")


async def handle_settings(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /settings slash command.

    Usage:
    - /settings view - View current settings
    - /settings set key:"..." value:"..."
    - /settings reset - Reset to defaults
    """
    logger.info(f"/settings command from {interaction.user.name}")

    # Check permission to change settings
    from config.permissions import Permissions
    permissions = Permissions()
    if not permissions.can_change_settings(interaction.user):
        await interaction.response.send_message(
            "Only the owner can change settings.",
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
        subcommand = "view"

    if subcommand == "view":
        await handle_settings_view(bot, interaction)
    elif subcommand == "set":
        await handle_settings_set(bot, interaction, options)
    elif subcommand == "reset":
        await handle_settings_reset(bot, interaction)
    else:
        await interaction.response.send_message(
            f"Unknown settings action: {subcommand}",
            ephemeral=True,
        )


async def handle_settings_view(bot, interaction: Interaction) -> None:
    """Display current settings."""
    from config.settings import Settings

    settings_text = f"""---
**⚙️ JARVIS Settings**

**Bot Configuration:**
- **Name:** {Settings.JARVIS_NAME}
- **Owner:** User ID {Settings.OWNER_USER_ID}
- **Friend:** User ID {Settings.FRIEND_USER_ID}

**AI Configuration:**
- **Gemini Model:** {Settings.GEMINI_MODEL}
- **API Key:** {'✅ Set' if Settings.GEMINI_API_KEY else '❌ Not set'}

**Discord Configuration:**
- **Token:** {'✅ Set' if Settings.DISCORD_TOKEN else '❌ Not set'}

*To change settings, edit the `.env` file and restart JARVIS.*
"""
    await interaction.response.send_message(settings_text, ephemeral=True)


async def handle_settings_set(bot, interaction: Interaction, options: list) -> None:
    """Set a specific setting."""
    key = None
    value = None

    for option in options:
        name = option.get("name")
        val = option.get("value")

        if name == "key":
            key = val
        elif name == "value":
            value = val

    if not key or not value:
        await interaction.response.send_message(
            "Please provide both key and value.",
            ephemeral=True,
        )
        return

    # In Phase 1, settings are read from .env
    # Database settings will be implemented in later phases
    from database.database import Database

    db = bot.database
    if db and db.conn:
        await db.execute(
            "INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        await db.commit()
        await interaction.response.send_message(
            f"✅ Setting `{key}` updated to `{value}`.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Database not connected. Please restart JARVIS.",
            ephemeral=True,
        )


async def handle_settings_reset(bot, interaction: Interaction) -> None:
    """Reset settings to defaults."""
    from database.database import Database

    db = bot.database
    if db and db.conn:
        await db.execute("DELETE FROM bot_settings")
        await db.commit()

        # Re-initialize defaults
        from config.settings import Settings
        await db.initialize_defaults(
            owner_id=Settings.OWNER_USER_ID or 0,
            owner_name="Owner",
            friend_id=Settings.FRIEND_USER_ID or 0,
            friend_name="Friend",
        )

        await interaction.response.send_message(
            "✅ Settings reset to defaults.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Database not connected.",
            ephemeral=True,
        )


async def setup_settings(bot) -> None:
    """Register the settings command with Discord."""
    logger.info("Settings command registered")
