"""
JARVIS /summarize Command

Summarizes recent messages in a channel.
"""

from discord import Interaction, TextChannel

from utils.logger import get_logger

logger = get_logger("commands.summarize")


async def handle_summarize(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /summarize slash command.

    Usage: /summarize channel:#general limit:50
    """
    logger.info(f"/summarize command from {interaction.user.name}")

    # Extract parameters
    channel_id = None
    limit = 50

    for option in options:
        name = option.get("name")
        value = option.get("value")

        if name == "channel" and value:
            # Discord channel IDs are integers in interactions
            channel_id = int(value) if isinstance(value, str) else value
        elif name == "limit" and value:
            limit = int(value)

    # If no channel specified, use current channel
    if not channel_id:
        channel = interaction.channel
        if not isinstance(channel, TextChannel):
            await interaction.response.send_message(
                "This command can only be used in text channels.",
                ephemeral=True,
            )
            return
    else:
        channel = bot.get_channel(channel_id)
        if not isinstance(channel, TextChannel):
            await interaction.response.send_message(
                "Invalid channel specified.",
                ephemeral=True,
            )
            return

    # Check authorization for channel access
    from config.permissions import Permissions
    permissions = Permissions()
    if not permissions.can_access_channel(interaction.user, channel_id or channel.id):
        await interaction.response.send_message(
            "You don't have access to summarize this channel.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"📝 Summarizing recent messages in {channel.mention}...",
        ephemeral=True,
    )

    # Gather messages
    from services.summarizer import SummarizerService
    summarizer = SummarizerService()
    messages = await summarizer.gather_messages(channel, limit=limit)

    if not messages:
        await interaction.followup.send(
            "No messages found to summarize.",
            ephemeral=True,
        )
        return

    # Generate summary
    summary = summarizer.summarize_basic(messages)

    # Check for action items and unanswered questions
    action_items = summarizer.identify_action_items(messages)
    questions = summarizer.identify_unanswered_questions(messages)

    response = f"""**📊 Summary for {channel.name}**

{summary}"""

    if action_items:
        response += "\n\n**📋 Action Items:**\n"
        for item in action_items[:5]:
            response += f"- {item}\n"

    if questions:
        response += "\n\n**❓ Unanswered Questions:**\n"
        for q in questions[-3:]:
            response += f"- {q}\n"

    response += f"\n\n*Analyzed {len(messages)} messages.*"

    await interaction.followup.send(response, ephemeral=True)


async def setup_summarize(bot) -> None:
    """Register the summarize command with Discord."""
    logger.info("Summarize command registered")
