"""
JARVIS /ask Command

Allows users to ask JARVIS questions.
Will use Gemini in Phase 2.
"""

from discord import Interaction

from utils.logger import get_logger

logger = get_logger("commands.ask")


async def handle_ask(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /ask slash command.

    Usage: /ask question:"What is Python?"
    """
    logger.info(f"/ask command from {interaction.user.name}")

    # Extract the question from options
    question = None
    for option in options:
        if option.get("name") == "question":
            question = option.get("value")
            break

    if not question:
        await interaction.response.send_message(
            "Please provide a question. Usage: `/ask question:\"Your question here\"`",
            ephemeral=True,
        )
        return

    # Defer the response while we process
    await interaction.response.send_message(
        f"🔍 Processing your question, {interaction.user.display_name}...",
        ephemeral=True,
    )

    # TODO: Phase 2 - Route to Gemini for answer
    # For now, provide a placeholder response
    answer = f"""I've received your question: "{question}"

In Phase 2, I'll use my AI capabilities to provide a thoughtful answer.

For now, you can ask me about:
- General knowledge
- Task assistance
- Discord server information
- Your reminders and tasks

*Your question has been noted.*"""

    await interaction.followup.send(answer, ephemeral=True)


async def setup_ask(bot) -> None:
    """Register the ask command with Discord."""
    logger.info("Ask command registered")
