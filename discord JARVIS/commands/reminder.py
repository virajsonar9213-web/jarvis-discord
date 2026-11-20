"""
JARVIS /remind Command

Manages user reminders and tasks.
"""

from datetime import datetime, timedelta

from discord import Interaction, ChannelType

from utils.logger import get_logger
from utils.helpers import parse_int

logger = get_logger("commands.reminder")


async def handle_remind(bot, interaction: Interaction, options: list) -> None:
    """
    Handle the /remind slash command.

    Usage:
    - /remind add content:"..." time:"1 hour" or time:"2024-01-01 10:00"
    - /remind list
    - /remind complete id:123
    - /remind delete id:123
    """
    logger.info(f"/remind command from {interaction.user.name}")

    # Extract subcommand
    subcommand = None
    for option in options:
        if option.get("name") == "action":
            subcommand = option.get("value")
            break

    if not subcommand:
        await interaction.response.send_message(
            "Usage: `/remind add content:\"...\" time:\"1 hour\"` or `/remind list`",
            ephemeral=True,
        )
        return

    if subcommand == "add":
        await handle_remind_add(bot, interaction, options)
    elif subcommand == "list":
        await handle_remind_list(bot, interaction)
    elif subcommand == "complete":
        await handle_remind_complete(bot, interaction, options)
    elif subcommand == "delete":
        await handle_remind_delete(bot, interaction, options)
    else:
        await interaction.response.send_message(
            f"Unknown reminder action: {subcommand}",
            ephemeral=True,
        )


async def handle_remind_add(bot, interaction: Interaction, options: list) -> None:
    """Add a new reminder."""
    content = None
    time_str = None

    for option in options:
        name = option.get("name")
        value = option.get("value")

        if name == "content":
            content = value
        elif name == "time":
            time_str = value

    if not content:
        await interaction.response.send_message(
            "Please provide content for the reminder.",
            ephemeral=True,
        )
        return

    if not time_str:
        await interaction.response.send_message(
            "Please provide a time. Examples: '1 hour', '2 hours', 'tomorrow', '2024-01-01 10:00'",
            ephemeral=True,
        )
        return

    # Parse the time
    scheduled_for = parse_reminder_time(time_str)
    if not scheduled_for:
        await interaction.response.send_message(
            "Invalid time format. Use relative time ('1 hour', 'tomorrow') or absolute ('2024-01-01 10:00').",
            ephemeral=True,
        )
        return

    # Check if time is in the past
    if scheduled_for <= datetime.now():
        await interaction.response.send_message(
            "The specified time is in the past.",
            ephemeral=True,
        )
        return

    # Add the reminder
    reminder_service = bot.reminder
    reminder = reminder_service.add_reminder(
        user_id=interaction.user.id,
        content=content,
        scheduled_for=scheduled_for,
    )

    # Format the time for display
    time_display = format_reminder_time(scheduled_for)

    await interaction.response.send_message(
        f"✅ Reminder set!\n\n"
        f"**Content:** {content}\n"
        f"**Scheduled for:** {time_display}\n"
        f"**ID:** {reminder.id}",
        ephemeral=True,
    )


async def handle_remind_list(bot, interaction: Interaction) -> None:
    """List user's reminders."""
    reminder_service = bot.reminder
    reminders = reminder_service.get_user_reminders(interaction.user.id)

    if not reminders:
        await interaction.response.send_message(
            "No reminders found.",
            ephemeral=True,
        )
        return

    response = "**📋 Your Reminders**\n\n"
    for reminder in reminders:
        status = "✅ Completed" if reminder.is_completed else "⏳ Pending"
        time_display = format_reminder_time(reminder.scheduled_for)
        response += f"**ID: {reminder.id}** - {status}\n"
        response += f"Content: {reminder.content}\n"
        response += f"When: {time_display}\n\n"

    await interaction.response.send_message(response, ephemeral=True)


async def handle_remind_complete(bot, interaction: Interaction, options: list) -> None:
    """Mark a reminder as complete."""
    reminder_id = None

    for option in options:
        if option.get("name") == "id":
            reminder_id = parse_int(option.get("value"))
            break

    if not reminder_id:
        await interaction.response.send_message(
            "Please provide a reminder ID.",
            ephemeral=True,
        )
        return

    reminder_service = bot.reminder
    success = reminder_service.complete_reminder(reminder_id)

    if success:
        await interaction.response.send_message(
            "✅ Reminder marked as complete!",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Reminder not found.",
            ephemeral=True,
        )


async def handle_remind_delete(bot, interaction: Interaction, options: list) -> None:
    """Delete a reminder."""
    reminder_id = None

    for option in options:
        if option.get("name") == "id":
            reminder_id = parse_int(option.get("value"))
            break

    if not reminder_id:
        await interaction.response.send_message(
            "Please provide a reminder ID.",
            ephemeral=True,
        )
        return

    reminder_service = bot.reminder
    success = reminder_service.delete_reminder(reminder_id)

    if success:
        await interaction.response.send_message(
            "🗑️ Reminder deleted.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "Reminder not found.",
            ephemeral=True,
        )


def parse_reminder_time(time_str: str) -> datetime | None:
    """Parse a reminder time string into a datetime."""
    time_str = time_str.lower().strip()

    # Try absolute datetime formats
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue

    # Try relative time formats
    import re

    # Number + unit patterns
    patterns = [
        (r"(\d+)\s*minute", lambda m: timedelta(minutes=int(m.group(1)))),
        (r"(\d+)\s*minutes", lambda m: timedelta(minutes=int(m.group(1)))),
        (r"(\d+)\s*hour", lambda m: timedelta(hours=int(m.group(1)))),
        (r"(\d+)\s*hours", lambda m: timedelta(hours=int(m.group(1)))),
        (r"(\d+)\s*day", lambda m: timedelta(days=int(m.group(1)))),
        (r"(\d+)\s*days", lambda m: timedelta(days=int(m.group(1)))),
        (r"(\d+)\s*week", lambda m: timedelta(weeks=int(m.group(1)))),
        (r"(\d+)\s*weeks", lambda m: timedelta(weeks=int(m.group(1)))),
    ]

    for pattern, calculator in patterns:
        match = re.match(pattern, time_str)
        if match:
            return datetime.now() + calculator(match)

    # Special keywords
    if time_str == "tomorrow":
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)

    if time_str == "today":
        today = datetime.now()
        return today.replace(hour=9, minute=0, second=0, microsecond=0)

    return None


def format_reminder_time(dt: datetime) -> str:
    """Format a datetime for display."""
    now = datetime.now()
    diff = dt - now

    if diff.total_seconds() < 60:
        return "now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"in {minutes} minute{'s' if minutes != 1 else ''}"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"in {hours} hour{'s' if hours != 1 else ''}"
    else:
        days = int(diff.total_seconds() / 86400)
        return f"in {days} day{'s' if days != 1 else ''}"

    return dt.strftime("%Y-%m-%d %H:%M")


async def setup_reminder(bot) -> None:
    """Register the reminder command with Discord."""
    logger.info("Reminder command registered")
