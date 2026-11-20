"""
JARVIS on_interaction Event Handler

Slash commands are owned by the discord.py CommandTree (registered in
commands/register.py), which Discord dispatches independently. This module
only handles interactions the tree does not: message components such as the
approval buttons used by the draft -> approve workflow.
"""

import discord

from utils.logger import get_logger

logger = get_logger("events.on_interaction")


async def on_interaction(bot, interaction: discord.Interaction) -> None:
    """Handle non-command interactions (buttons, select menus)."""
    if interaction.type is not discord.InteractionType.component:
        # Application commands and autocomplete are handled by bot.tree.
        return

    try:
        from config.permissions import Permissions

        if not Permissions.is_authorized(interaction.user):
            await interaction.response.send_message(
                "You are not authorized to use JARVIS.",
                ephemeral=True,
            )
            return

        custom_id = (interaction.data or {}).get("custom_id", "")
        logger.debug(f"Component interaction: {custom_id} from {interaction.user.name}")

        if custom_id.startswith("approve_"):
            await _handle_approval(bot, interaction, custom_id[len("approve_"):], approved=True)
        elif custom_id.startswith("reject_"):
            await _handle_approval(bot, interaction, custom_id[len("reject_"):], approved=False)
        else:
            await interaction.response.send_message(
                "This interaction is no longer valid.",
                ephemeral=True,
            )

    except Exception as e:
        from utils.error_handler import ErrorHandler
        await ErrorHandler.handle_command_error(e, interaction, "on_interaction")


async def _handle_approval(
    bot,
    interaction: discord.Interaction,
    approval_id: str,
    approved: bool,
) -> None:
    """Approve or reject a pending action."""
    try:
        parsed_id = int(approval_id)
    except ValueError:
        await interaction.response.send_message("Invalid approval request.", ephemeral=True)
        return

    approval_service = bot.approval
    user_id = interaction.user.id

    if approved:
        success, action_data = await approval_service.approve(parsed_id, user_id)
        if success:
            await interaction.response.send_message(
                "✅ Action approved.",
                ephemeral=True,
            )
            # TODO: Phase 4 - execute the approved action
        else:
            await interaction.response.send_message(
                "❌ Approval failed. The request may have expired or been revoked.",
                ephemeral=True,
            )
    else:
        success = await approval_service.reject(parsed_id, user_id)
        await interaction.response.send_message(
            "❌ Action rejected." if success else "❌ Rejection failed. The request may have expired.",
            ephemeral=True,
        )
