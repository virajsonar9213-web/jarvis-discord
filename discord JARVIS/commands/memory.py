"""
JARVIS /memory Command

Manages JARVIS's conversation memory.
"""

from discord import Interaction

from utils.logger import get_logger

logger = get_logger("commands.memory")


async def handle_memory(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /memory slash command.

    Usage:
    - /memory list - List recent memories
    - /memory add content:"..." category:"general" - Add a memory
    - /memory delete id:123 - Delete a memory
    - /memory forget - Forget all memories for this user
    """
    logger.info(f"/memory command from {interaction.user.name}")

    # Extract command subtype
    subcommand = None
    for option in options:
        if option.get("name") == "action":
            subcommand = option.get("value")
            break

    if not subcommand:
        await interaction.response.send_message(
            "Usage: `/memory list` or `/memory add content:\"...\" category:\"general\"` or `/memory delete id:123`",
            ephemeral=True,
        )
        return

    # Check permission to manage memory
    from config.permissions import Permissions
    permissions = Permissions()
    if not permissions.can_manage_memory(interaction.user):
        await interaction.response.send_message(
            "You don't have permission to manage memory.",
            ephemeral=True,
        )
        return

    if subcommand == "list":
        await handle_list_memory(bot, interaction)
    elif subcommand == "add":
        await handle_add_memory(bot, interaction, options)
    elif subcommand == "delete":
        await handle_delete_memory(bot, interaction, options)
    elif subcommand == "forget":
        await handle_forget_memory(bot, interaction)
    else:
        await interaction.response.send_message(
            f"Unknown memory action: {subcommand}",
            ephemeral=True,
        )


async def handle_list_memory(bot, interaction: Interaction) -> None:
    """List recent memories."""
    memory_manager = bot.memory_manager

    user_id = interaction.user.id
    memories = memory_manager.get_memories_for_user(user_id)
    shared = memory_manager.get_shared_memories()

    all_memories = memories + shared
    all_memories.sort(key=lambda m: m.created_at, reverse=True)
    recent = all_memories[:10]

    if not recent:
        await interaction.response.send_message(
            "No memories found.",
            ephemeral=True,
        )
        return

    response = "**📚 Recent Memories**\n\n"
    for memory in recent:
        user_label = f"(user #{memory.user_id})" if memory.user_id else "(shared)"
        response += f"**[{memory.category}]** {user_label}\n{memory.content}\n\n"

    await interaction.response.send_message(response, ephemeral=True)


async def handle_add_memory(bot, interaction: Interaction, options: list) -> None:
    """Add a new memory."""
    content = None
    category = "general"

    for option in options:
        name = option.get("name")
        value = option.get("value")

        if name == "content":
            content = value
        elif name == "category":
            category = value

    if not content:
        await interaction.response.send_message(
            "Please provide content for the memory.",
            ephemeral=True,
        )
        return

    memory_manager = bot.memory_manager
    memory = memory_manager.add_memory(
        content=content,
        user_id=interaction.user.id,
        category=category,
    )

    await interaction.response.send_message(
        f"✅ Memory added!\n\n**[{category}]** {content}",
        ephemeral=True,
    )


async def handle_delete_memory(bot, interaction: Interaction, options: list) -> None:
    """Delete a memory by ID."""
    memory_id = None

    for option in options:
        if option.get("name") == "id":
            memory_id = int(option.get("value"))
            break

    if not memory_id:
        await interaction.response.send_message(
            "Please provide a memory ID to delete.",
            ephemeral=True,
        )
        return

    memory_manager = bot.memory_manager
    success = memory_manager.delete_memory(memory_id)

    if success:
        await interaction.response.send_message(
            f"✅ Memory #{memory_id} deleted.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            f"Memory #{memory_id} not found.",
            ephemeral=True,
        )


async def handle_forget_memory(bot, interaction: Interaction) -> None:
    """Forget all memories for this user."""
    memory_manager = bot.memory_manager
    count = memory_manager.forget_user_memory(interaction.user.id)

    await interaction.response.send_message(
        f"✅ Forgot {count} memories for you.",
        ephemeral=True,
    )


async def setup_memory(bot) -> None:
    """Register the memory command with Discord."""
    logger.info("Memory command registered")
