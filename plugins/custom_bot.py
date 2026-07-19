#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TelegramDL - Advanced Telegram Downloader Bot

Copyright (c) 2024-2026 Shinei Nouzen (Shineii86)
Licensed under the MIT License

Author:    Shinei Nouzen
GitHub:    https://github.com/Shineii86/TelegramDL
Telegram:  https://t.me/Shineii86
Email:     ikx7a@hotmail.com

Description:
    Advanced Telegram Restricted Content Downloader with Premium System,
    yt-dlp Integration, File Splitting, Custom Bots & More.

Version:    2.0.0
Python:     3.10+
Framework:  Kurigram (Pyrogram Fork)

Disclaimer:
    This bot is for educational purposes only.
    Use responsibly and respect Telegram's Terms of Service.
"""

import os
import asyncio
import logging
from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery
from bot import bot
from database.db import db

logger = logging.getLogger(__name__)

# Store active custom bot clients
custom_bot_clients = {}


async def get_user_bot(user_id):
    """Get or create a user's custom bot client."""
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
        return None


async def stop_user_bot(user_id):
    """Stop a user's custom bot client."""
    if user_id in custom_bot_clients:
        try:
            await custom_bot_clients[user_id].stop()
        except:
            pass
        del custom_bot_clients[user_id]


@bot.on_message(filters.command("setbot") & filters.private)
async def setbot_cmd(client, message: Message):
    """Set a custom bot token for your account."""
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
    """Remove custom bot and use main bot."""
    user_id = message.from_user.id

    await stop_user_bot(user_id)
    await db.delete_bot_token(user_id)

    await message.reply(
        "**✅ Custom Bot Removed**\n\n"
        "Now using the main bot for downloads."
    )


@bot.on_message(filters.command("mybot") & filters.private)
async def mybot_cmd(client, message: Message):
    """Show current bot status."""
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
        except:
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
