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
        Custom bot management. Each user can set their own bot token
        to prevent bans on the main bot.

    COMMANDS:
        /setbot <token> — Set custom bot token
        /delbot         — Remove custom bot
        /mybot          — View current bot status

    FEATURES:
        FEATURE: CUSTOM_BOT_COMMANDS
        FEATURE: BOT_VALIDATION
        FEATURE: BOT_CACHING
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import logging
from ftmgram import filters, Client
from ftmgram.types import Message
from bot import bot
from database.db import db

logger = logging.getLogger(__name__)

# ===========================================================================
#   GLOBAL STATE
# ---------------------------------------------------------------------------
#   custom_bot_clients: Cache of active custom bot clients
#
#   NOTE: Clients are reused across requests for performance
# ===========================================================================

custom_bot_clients = {}

# ===========================================================================
#   HELPER FUNCTIONS
# ===========================================================================


async def get_user_bot(user_id):
    """Get or create a user's custom bot client.

    Args:
        user_id: Telegram user ID

    Returns:
        Client: Active bot client or None

    Process:
        1. Check cache for existing client
        2. Verify client is connected
        3. Get token from database
        4. Create and start new client
        5. Cache for reuse

    Note:
        Returns None if no custom bot set
    """
    if user_id in custom_bot_clients:
        client = custom_bot_clients[user_id]
        if client.is_connected:
            return client

    bot_token = await db.get_bot_token(user_id)
    if not bot_token:
        return None

    try:
        client = Client(
            f"userbot_{user_id}",
            bot_token=bot_token,
            api_id=int(os.environ.get("API_ID", "0")),
            api_hash=os.environ.get("API_HASH", ""),
        )
        await client.start()
        custom_bot_clients[user_id] = client
        return client
    except Exception as e:
        logger.error(f"Failed to start custom bot for {user_id}: {e}")
        # Cleanup: stop and remove the client if start() failed
        try:
            await client.stop()
        except Exception:
            pass
        return None


async def stop_user_bot(user_id):
    """Stop a user's custom bot client.

    Args:
        user_id: Telegram user ID

    Returns:
        None

    Note:
        Removes client from cache after stopping
    """
    if user_id in custom_bot_clients:
        try:
            await custom_bot_clients[user_id].stop()
        except Exception:
            pass
        del custom_bot_clients[user_id]

# ===========================================================================
#   FEATURE: CUSTOM_BOT_COMMANDS
# ---------------------------------------------------------------------------
#   /setbot <token> — Set custom bot token
#   /delbot         — Remove custom bot
#   /mybot          — View current bot status
#
#   TIP: Custom bots prevent bans on main bot token
# ===========================================================================


@bot.on_message(filters.command("setbot") & filters.private)
async def setbot_cmd(client, message: Message):
    """Set custom bot token.

    Args:
        client: Bot client
        message: User message with bot token

    Returns:
        None

    Usage:
        /setbot 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

    Process:
        1. Check ban status
        2. Validate token format
        3. Test token by starting client
        4. Save to database
        5. Show success message

    Note:
        Token format: "bot_token" (e.g., "123456:ABC-DEF")
    """
    user_id = message.from_user.id

    if await db.is_banned(user_id):
        await message.reply("**❌ You are banned**")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**🤖 Custom Bot**\n\n"
            "Use your own bot token for downloads.\n"
            "This prevents bans on the main bot.\n\n"
            "**Usage:** `/setbot <bot_token>`\n\n"
            "**How to get bot token:**\n"
            "1. Message @BotFather on Telegram\n"
            "2. Create a new bot with /newbot\n"
            "3. Copy the bot token\n"
            "4. Send it here\n\n"
            "**To remove:** `/delbot`"
        )
        return

    bot_token = args[1].strip()

    # Validate bot token format
    if not bot_token.count(':') == 1:
        await message.reply("**❌ Invalid bot token format**\n\nToken should be like: `123456:ABC-DEF`")
        return

    # Test the bot token
    status_msg = await message.reply("**🔄 Testing bot token...**")

    try:
        test_client = Client(
            "test_bot",
            bot_token=bot_token,
            api_id=int(os.environ.get("API_ID", "0")),
            api_hash=os.environ.get("API_HASH", ""),
        )
        await test_client.start()
        me = await test_client.get_me()
        await test_client.stop()

        # Save to database
        await db.set_bot_token(user_id, bot_token)

        await status_msg.edit_text(
            f"**✅ Custom Bot Set!**\n\n"
            f"**Bot:** @{me.username}\n"
            f"**Name:** {me.first_name}\n\n"
            f"Now all your downloads will go through this bot.\n"
            f"This prevents bans on the main bot."
        )

    except Exception as e:
        await status_msg.edit_text(
            f"**❌ Invalid Bot Token**\n\n"
            f"**Error:** {e}\n\n"
            f"Make sure:\n"
            f"1. Token is correct\n"
            f"2. Bot is not deleted\n"
            f"3. BotFather created this bot"
        )


@bot.on_message(filters.command("delbot") & filters.private)
async def delbot_cmd(client, message: Message):
    """Remove custom bot.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Process:
        1. Stop active client
        2. Remove from database
        3. Show success message
    """
    user_id = message.from_user.id

    await stop_user_bot(user_id)
    await db.delete_bot_token(user_id)

    await message.reply(
        "**✅ Custom Bot Removed**\n\n"
        "Now using the main bot for downloads."
    )


@bot.on_message(filters.command("mybot") & filters.private)
async def mybot_cmd(client, message: Message):
    """Show current bot status.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Displays:
        - Bot username and name
        - Bot ID
        - Connection status
    """
    user_id = message.from_user.id

    bot_token = await db.get_bot_token(user_id)

    if bot_token:
        # Get bot info
        try:
            test_client = Client(
                "test_bot",
                bot_token=bot_token,
                api_id=int(os.environ.get("API_ID", "0")),
                api_hash=os.environ.get("API_HASH", ""),
            )
            await test_client.start()
            me = await test_client.get_me()
            await test_client.stop()

            await message.reply(
                f"**🤖 Your Custom Bot**\n\n"
                f"**Bot:** @{me.username}\n"
                f"**Name:** {me.first_name}\n"
                f"**ID:** `{me.id}`\n\n"
                f"Status: ✅ Active\n\n"
                f"Use /delbot to remove."
            )
        except Exception:
            await message.reply(
                f"**🤖 Your Custom Bot**\n\n"
                f"**Token:** `{bot_token[:10]}...{bot_token[-5:]}`\n\n"
                f"Status: ⚠️ Error connecting\n\n"
                f"Use /delbot to remove and re-add."
            )
    else:
        await message.reply(
            "**🤖 No Custom Bot**\n\n"
            "Using the main bot.\n\n"
            "Use /setbot <token> to add your own bot."
        )

# ===========================================================================
#   END OF CUSTOM_BOT PLUGIN
# ===========================================================================
