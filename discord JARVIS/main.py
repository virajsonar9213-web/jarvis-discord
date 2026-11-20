#!/usr/bin/env python3
"""
JARVIS - Your Personal AI Assistant Inside Discord

Main entry point for the JARVIS Discord bot.
"""

import asyncio
import sys

from bot import JARVISBot
from utils.logger import setup_logging
from config.settings import Settings

# Set up logging first
logger = setup_logging()


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    errors = Settings.validate()

    if errors:
        logger.error("Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return False

    return True


async def main():
    """Main entry point for JARVIS."""
    logger.info("=" * 50)
    logger.info("Starting JARVIS Discord Bot")
    logger.info("=" * 50)

    # Validate environment
    if not validate_environment():
        logger.error("Please configure your .env file before running JARVIS.")
        logger.error("Copy .env.example to .env and fill in your values.")
        sys.exit(1)

    # Create the bot. All events (on_ready, on_message, on_interaction)
    # are handled by JARVISBot and its registered command tree.
    bot = JARVISBot()

    try:
        await bot.start(Settings.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
    finally:
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("JARVIS shutdown initiated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
