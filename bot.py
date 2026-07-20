#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
    PROJECT:  TelegramDL - Advanced Telegram Downloader Bot
    AUTHOR:   Shinei Nouzen (Shineii86)
    LICENSE:  MIT License (c) 2024-2026
    REPO:     https://github.com/Shineii86/TelegramDL
============================================================================
    DESCRIPTION:
        Main entry point. Initializes Bot and User clients,
        registers plugins, and starts the event loop.

    CLIENTS:
        - Bot:        Handles public content via bot token
        - UserClient: Handles restricted content via session string
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import logging
import asyncio
import warnings
warnings.filterwarnings("ignore", message="coroutine.*was never awaited")
from ftmgram import Client

from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM, __version__

# ===========================================================================
#   LOGGING CONFIGURATION
# ===========================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===========================================================================
#   GLOBAL USER CLIENT
# ---------------------------------------------------------------------------
#   Used for restricted content when LOGIN_SYSTEM=false.
#   Initialized once at import, started/stopped with bot lifecycle.
# ===========================================================================

user_client = None

if not LOGIN_SYSTEM and STRING_SESSION:
    try:
        user_client = Client(
            "user_session",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=STRING_SESSION
        )
        logger.info("User client initialized from STRING_SESSION")
    except Exception as e:
        logger.error(f"Failed to initialize user client: {e}")
        user_client = None

# ===========================================================================
#   BOT CLASS
# ---------------------------------------------------------------------------
#   Extends Pyrogram Client with custom configuration.
#   Plugins are auto-loaded from plugins/ directory.
#
#   CONFIG:
#       workers=150       — Max concurrent handlers
#       sleep_threshold=5 — Sleep after this many pending tasks
# ===========================================================================


class Bot(Client):
    def __init__(self):
        super().__init__(
            "telegramdl_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=150,
            sleep_threshold=5
        )

    @property
    def handlers(self):
        """Expose handlers for ftmgram plugin discovery."""
        result = []
        for group, handler_list in self.dispatcher.groups.items():
            for handler in handler_list:
                result.append((handler, group))
        return result


bot = Bot()

# ===========================================================================
#   CLIENT LIFECYCLE MANAGEMENT
# ---------------------------------------------------------------------------
#   start_user_client():  Start user client for restricted content
#   stop_user_client():   Stop user client gracefully
# ===========================================================================


async def start_user_client():
    """Start user client if initialized and not connected.

    Returns:
        None

    Tip:
        Called automatically when bot starts. Only runs if
        LOGIN_SYSTEM=false and STRING_SESSION is provided.
    """
    global user_client
    if user_client and not user_client.is_connected:
        await user_client.start()
        logger.info("User client started")


async def stop_user_client():
    """Stop user client gracefully.

    Returns:
        None
    """
    global user_client
    if user_client and user_client.is_connected:
        await user_client.stop()
        logger.info("User client stopped")

# ===========================================================================
#   MAIN ENTRY POINT
# ---------------------------------------------------------------------------
#   Creates downloads directory and starts the bot.
#   Bot runs until interrupted (Ctrl+C).
# ===========================================================================


def main():
    """Start TelegramDL bot.

    Returns:
        None

    Process:
        1. Create downloads directory
        2. Log version info
        3. Start bot (blocking)
    """
    os.makedirs("downloads", exist_ok=True)
    logger.info(f"Starting TelegramDL v{__version__}...")
    
    async def _run():
        await start_user_client()
        await bot.start()
        logger.info("Bot is running!")
        await asyncio.Event().wait()  # Run forever
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Colab / nest_asyncio — schedule as a task
            task = loop.create_task(_run())
            loop.run_until_complete(task)
        else:
            loop.run_until_complete(_run())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_run())


# ===========================================================================
#   SCRIPT ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    main()

# ===========================================================================
#   END OF BOT
# ===========================================================================
