"""
JARVIS Discord Bot

Main bot class that ties together all components.
Handles Discord connection, commands, events, and services.
"""

import asyncio

from discord import Intents, Message
from discord.ext import commands

from config.permissions import Permissions
from config.channels import ChannelConfigManager
from utils.logger import get_logger
from utils.error_handler import ErrorHandler

logger = get_logger("bot")


class JARVISBot(commands.Bot):
    """
    Main JARVIS Discord bot.

    Extends discord.py's commands.Bot with JARVIS-specific functionality.
    """

    def __init__(self):
        # Set up intents - only non-privileged intents to avoid developer portal requirements
        intents = Intents.default()
        intents.messages = True
        intents.reactions = True
        intents.guilds = True

        # Initialize the bot
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,  # We use slash commands
        )

        # Core components (initialized in setup)
        self.permissions = Permissions()
        self.channel_config = ChannelConfigManager()
        self.error_handler = ErrorHandler()
        self.logger = get_logger("bot")

        # Service modules (to be initialized)
        self.message_reader = None
        self.message_sender = None
        self.summarizer = None
        self.notifications = None
        self.approval = None
        self.voice = None
        self.reminder = None

        # AI components (to be initialized)
        self.gemini_client = None
        self.personality = None
        self.memory_manager = None
        self.context_manager = None
        self.tool_manager = None

        # Database (to be initialized)
        self.database = None

        # Ready state
        self.is_ready = False
        self._commands_synced = False

    async def setup_hook(self) -> None:
        """
        Setup hook called when the bot is starting.
        Initialize all components here.
        """
        logger.info("Setting up JARVIS bot...")

        # Import and initialize services
        from services.message_reader import MessageReaderService
        from services.message_sender import MessageSenderService
        from services.summarizer import SummarizerService
        from services.notifications import NotificationService
        from services.approval import ApprovalService
        from services.voice import VoiceService
        from services.reminder import ReminderService

        from ai.gemini import GeminiClient
        from ai.personality import JARVISPersonality
        from ai.memory import MemoryManager
        from ai.context import ContextManager
        from ai.tools import ToolManager

        from database.database import Database

        # Initialize services
        self.message_reader = MessageReaderService()
        self.message_sender = MessageSenderService()
        self.summarizer = SummarizerService()
        self.notifications = NotificationService()
        self.approval = ApprovalService()
        self.voice = VoiceService()
        self.reminder = ReminderService()

        # Initialize AI components
        from config.settings import Settings
        self.gemini_client = GeminiClient(
            api_key=Settings.GEMINI_API_KEY,
            model=Settings.GEMINI_MODEL,
        )
        self.personality = JARVISPersonality()
        self.memory_manager = MemoryManager()
        self.context_manager = ContextManager()
        self.tool_manager = ToolManager()

        # Initialize database
        self.database = Database()

        # Register slash commands and sync them with Discord
        from commands.register import setup_commands
        await setup_commands(self)

        logger.info("JARVIS bot setup complete")

    async def sync_commands(self) -> None:
        """
        Push slash commands to Discord, once per process.

        Synced per guild: that is immediate and uses a separate rate-limit
        bucket from global command sync, which is easy to exhaust while
        restarting the bot during development.
        """
        if self._commands_synced or not self.guilds:
            return

        try:
            total = 0
            for guild in self.guilds:
                # Commands are registered globally; copy them into the guild
                # so a guild-scoped sync (immediate, own rate-limit bucket)
                # actually has something to publish.
                self.tree.copy_global_to(guild=guild)
                synced = await asyncio.wait_for(
                    self.tree.sync(guild=guild), timeout=20
                )
                total += len(synced)
            self._commands_synced = True
            logger.info(
                f"Synced {total} slash command(s) to {len(self.guilds)} guild(s)"
            )
        except asyncio.TimeoutError:
            logger.warning(
                "Slash command sync timed out. Commands may already be "
                "registered; they will sync on a later start."
            )
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

    async def on_ready(self) -> None:
        """
        Called when the bot is ready and connected to Discord.
        """
        self.is_ready = True

        # Register slash commands with Discord
        await self.sync_commands()

        # Initialize database connection
        try:
            await self.database.connect()

            # Initialize default data if needed
            from config.settings import Settings
            if Settings.OWNER_USER_ID and Settings.FRIEND_USER_ID:
                await self.database.initialize_defaults(
                    owner_id=Settings.OWNER_USER_ID,
                    owner_name="Owner",
                    friend_id=Settings.FRIEND_USER_ID,
                    friend_name="Friend",
                )
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

        # Initialize Gemini client
        try:
            await self.gemini_client.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")

        # Log connection details
        from events.on_ready import on_ready as on_ready_handler
        await on_ready_handler(self)

    async def on_message(self, message: Message) -> None:
        """Delegate incoming messages to the message event handler."""
        from events.on_message import on_message as on_message_handler
        await on_message_handler(self, message)

    async def on_interaction(self, interaction) -> None:
        """Delegate component interactions to the interaction handler."""
        from events.on_interaction import on_interaction as on_interaction_handler
        await on_interaction_handler(self, interaction)

    async def _handle_command(self, message: Message) -> None:
        """Handle a command message."""
        command = message.content[1:].split()[0].lower()  # Remove ! and get command

        self.logger.info(f"Command received: {command} from {message.author.name}")

        # Simple command routing for Phase 1
        commands_map = {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "ping": self._cmd_ping,
        }

        handler = commands_map.get(command)
        if handler:
            await handler(message)
        else:
            await message.channel.send(f"Unknown command: {command}. Use !help for available commands.")

    async def _cmd_help(self, message: Message) -> None:
        """Handle !help command."""
        help_text = """---
**JARVIS - Personal AI Assistant**

Available commands:
- `!help` - Show this help message
- `!status` - Show JARVIS status
- `!ping` - Check if JARVIS is responding

Slash commands (`/ask`, `/summarize`, `/read`, `/remind`,
`/memory`, `/settings`, `/voice`, `/status`, `/help`) are the
preferred interface and work without the Message Content Intent.

*Authorized users only.*
"""
        await message.channel.send(help_text)

    async def _cmd_status(self, message: Message) -> None:
        """Handle !status command."""
        status = f"""---
**JARVIS Status**

- **Online:** {self.is_ready}
- **Uptime:** Running
- **AI:** {'Connected' if self.gemini_client and self.gemini_client.is_ready else 'Not connected'}
- **Database:** {'Connected' if self.database else 'Not connected'}
- **Memory:** {len(self.memory_manager._memories) if self.memory_manager else 0} memories
- **Contexts:** {self.context_manager.get_context_count() if self.context_manager else 0} active

*Speaking: JARVIS*
"""
        await message.channel.send(status)

    async def _cmd_ping(self, message: Message) -> None:
        """Handle !ping command."""
        import time

        start = time.time()
        await message.channel.send("Pong!")
        latency = (time.time() - start) * 1000
        self.logger.info(f"Ping: {latency:.2f}ms")

    async def send_response(
        self,
        channel,
        content: str,
        reference_message: Message | None = None,
    ) -> None:
        """
        Send a response to a channel.
        Optionally reference a previous message.
        """
        try:
            if reference_message:
                await channel.send(content, reference=reference_message)
            else:
                await channel.send(content)
        except Exception as e:
            await self.error_handler.handle_command_error(
                e,
                context=f"Sending response to {channel.id}",
            )

    async def send_error_response(
        self,
        channel,
        error: Exception,
        reference_message: Message | None = None,
    ) -> None:
        """Send an error response to a channel."""
        friendly_error = self.error_handler.format_error_for_display(error)
        await self.send_response(channel, f"⚠️ {friendly_error}", reference_message)
