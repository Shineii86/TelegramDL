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
        User settings plugin. Handles rename tags, word rules,
        and topic group configuration.

    COMMANDS:
        /set_rename <tag>        — Set rename tag
        /del_rename              — Remove rename tag
        /set_del_words <words>   — Set words to delete
        /view_del_words          — View delete words
        /del_del_words           — Clear delete words
        /set_replace <old=new>   — Set word replacements
        /view_replace            — View replacements
        /del_replace             — Clear replacements
        /set_topic <chat> <topic> — Set topic group
        /del_topic               — Remove topic group

    FEATURES:
        FEATURE: RENAME_COMMANDS
        FEATURE: WORD_RULES
        FEATURE: TOPIC_GROUP
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import asyncio
import logging
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from bot import bot
from database.db import db
from utils.ui import back_keyboard

logger = logging.getLogger(__name__)

# ===========================================================================
#   FEATURE: RENAME_COMMANDS
# ---------------------------------------------------------------------------
#   /set_rename <tag> — Set prefix for uploaded files
#   /del_rename       — Remove rename tag
#
#   TIP: Files will be named "tag_filename.ext"
# ===========================================================================


@bot.on_message(filters.command("set_rename") & filters.private)
async def set_rename_cmd(client, message: Message):
    """Set rename tag for uploaded files.

    Args:
        client: Bot client
        message: User message with tag

    Returns:
        None

    Usage:
        /set_rename MyFiles

    Result:
        Files named: MyFiles_filename.ext
    """
    user_id = message.from_user.id

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**📝 Rename Tag**\n\n"
            "Set a prefix for your uploaded files.\n\n"
            "**Usage:** `/set_rename <tag>`\n"
            "**Example:** `/set_rename MyFiles`\n\n"
            "Files will be named: `MyFiles_filename.ext`\n\n"
            "**To remove:** `/del_rename`"
        )
        return

    tag = args[1].strip()
    await db.set_rename_tag(user_id, tag)
    await message.reply(f"**✅ Rename Tag Set:** `{tag}`")


@bot.on_message(filters.command("del_rename") & filters.private)
async def del_rename_cmd(client, message: Message):
    """Remove rename tag.

    Args:
        client: Bot client
        message: User message

    Returns:
        None
    """
    await db.delete_rename_tag(message.from_user.id)
    await message.reply("**✅ Rename Tag Removed**")

# ===========================================================================
#   FEATURE: WORD_RULES
# ---------------------------------------------------------------------------
#   /set_del_words <words>  — Words to auto-delete from captions
#   /view_del_words         — View current delete words
#   /del_del_words          — Clear delete words
#   /set_replace <old=new>  — Word replacements
#   /view_replace           — View replacements
#   /del_replace            — Clear replacements
#
#   TIP: Multiple words separated by spaces
# ===========================================================================


@bot.on_message(filters.command("set_del_words") & filters.private)
async def set_del_words_cmd(client, message: Message):
    """Set words to auto-delete from captions.

    Args:
        client: Bot client
        message: User message with words

    Returns:
        None

    Usage:
        /set_del_words ads spam promo

    Note:
        Words are space-separated
    """
    user_id = message.from_user.id

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**🗑 Delete Words**\n\n"
            "Auto-remove words from captions.\n\n"
            "**Usage:** `/set_del_words word1 word2 word3`\n"
            "**Example:** `/set_del_words ads spam promo`\n\n"
            "**To view:** `/view_del_words`\n"
            "**To clear:** `/del_del_words`"
        )
        return

    words = args[1].split()
    await db.set_delete_words(user_id, words)
    await message.reply(f"**✅ Delete Words Set:** {', '.join(words)}")


@bot.on_message(filters.command("view_del_words") & filters.private)
async def view_del_words_cmd(client, message: Message):
    """View current delete words.

    Args:
        client: Bot client
        message: User message

    Returns:
        None
    """
    words = await db.get_delete_words(message.from_user.id)
    if words:
        await message.reply(f"**🗑 Delete Words:**\n{', '.join(words)}")
    else:
        await message.reply("No delete words set.")


@bot.on_message(filters.command("del_del_words") & filters.private)
async def del_del_words_cmd(client, message: Message):
    """Clear delete words.

    Args:
        client: Bot client
        message: User message

    Returns:
        None
    """
    await db.set_delete_words(message.from_user.id, [])
    await message.reply("**✅ Delete Words Cleared**")


@bot.on_message(filters.command("set_replace") & filters.private)
async def set_replace_cmd(client, message: Message):
    """Set word replacements in captions.

    Args:
        client: Bot client
        message: User message with replacements

    Returns:
        None

    Usage:
        /set_replace ads=nothing promo=deal

    Note:
        Format: old=new (space-separated for multiple)
    """
    user_id = message.from_user.id

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**🔄 Replace Words**\n\n"
            "Auto-replace words in captions.\n\n"
            "**Usage:** `/set_replace old1=new1 old2=new2`\n"
            "**Example:** `/set_replace ads=nothing promo=deal`\n\n"
            "**To view:** `/view_replace`\n"
            "**To clear:** `/del_replace`"
        )
        return

    replacements = {}
    for pair in args[1].split():
        if '=' in pair:
            old, new = pair.split('=', 1)
            replacements[old] = new

    if replacements:
        await db.set_replace_words(user_id, replacements)
        formatted = ", ".join(f"{k}→{v}" for k, v in replacements.items())
        await message.reply(f"**✅ Replace Words Set:**\n{formatted}")
    else:
        await message.reply("**❌ Invalid format**\n\nUse: `old=new old2=new2`")


@bot.on_message(filters.command("view_replace") & filters.private)
async def view_replace_cmd(client, message: Message):
    """View current replace words.

    Args:
        client: Bot client
        message: User message

    Returns:
        None
    """
    replacements = await db.get_replace_words(message.from_user.id)
    if replacements:
        formatted = "\n".join(f"`{k}` → `{v}`" for k, v in replacements.items())
        await message.reply(f"**🔄 Replace Words:**\n\n{formatted}")
    else:
        await message.reply("No replace words set.")


@bot.on_message(filters.command("del_replace") & filters.private)
async def del_replace_cmd(client, message: Message):
    """Clear replace words.

    Args:
        client: Bot client
        message: User message

    Returns:
        None
    """
    await db.set_replace_words(message.from_user.id, {})
    await message.reply("**✅ Replace Words Cleared**")

# ===========================================================================
#   FEATURE: TOPIC_GROUP
# ---------------------------------------------------------------------------
#   /set_topic <chat_id> <topic_id> — Set topic for groups
#   /del_topic                      — Remove topic setting
#
#   NOTE: For topic-enabled groups only
# ===========================================================================


@bot.on_message(filters.command("set_topic") & filters.private)
async def set_topic_cmd(client, message: Message):
    """Set topic ID for topic-enabled groups.

    Args:
        client: Bot client
        message: User message with chat_id and topic_id

    Returns:
        None

    Usage:
        /set_topic -1001234567890 12

    Note:
        Requires topic-enabled group
    """
    user_id = message.from_user.id

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**📌 Topic Group**\n\n"
            "Upload files to a specific topic in topic-enabled groups.\n\n"
            "**Usage:** `/set_topic <chat_id> <topic_id>`\n"
            "**Example:** `/set_topic -1001234567890 12`\n\n"
            "**To remove:** `/del_topic`"
        )
        return

    parts = args[1].split()
    if len(parts) < 2:
        await message.reply("**❌ Usage:** `/set_topic <chat_id> <topic_id>`")
        return

    chat_id = parts[0]
    topic_id = parts[1]

    await db.set_dump_chat(user_id, chat_id)
    await db.set_topic_id(user_id, topic_id)

    await message.reply(
        f"**✅ Topic Group Set**\n\n"
        f"**Chat:** `{chat_id}`\n"
        f"**Topic:** `{topic_id}`\n\n"
        f"Files will be uploaded to this topic."
    )


@bot.on_message(filters.command("del_topic") & filters.private)
async def del_topic_cmd(client, message: Message):
    """Remove topic group setting.

    Args:
        client: Bot client
        message: User message

    Returns:
        None
    """
    await db.delete_dump_chat(message.from_user.id)
    await db.delete_topic_id(message.from_user.id)
    await message.reply("**✅ Topic Group Removed**")

# ===========================================================================
#   END OF SETTINGS PLUGIN
# ===========================================================================
