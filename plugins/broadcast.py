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
        Admin broadcast plugin. Sends messages to all registered users.

    COMMANDS:
        /broadcast — Reply to a message to send to all users

    FEATURES:
        FEATURE: BROADCAST_COMMAND
        FEATURE: AUTO_CLEANUP
        FEATURE: PROGRESS_TRACKING
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import time
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid

from bot import bot
from database.db import db
from config import ADMINS

# ===========================================================================
#   FEATURE: BROADCAST_COMMAND
# ---------------------------------------------------------------------------
#   /broadcast — Send message to all users
#   Admin only command with progress tracking
#
#   NOTE: Automatically removes blocked/deleted users
# ===========================================================================


@bot.on_message(filters.command("broadcast"))
async def broadcast_cmd(client, message: Message):
    """Handle /broadcast command.

    Args:
        client: Bot client
        message: Reply to message to broadcast

    Returns:
        None

    Admin Only: Yes

    Process:
        1. Check if user is admin
        2. Check if replying to a message
        3. Iterate through all users
        4. Copy message to each user
        5. Handle errors (blocked, deleted, flood)
        6. Auto-cleanup blocked/deleted users
        7. Show final stats

    Stats Tracked:
        - Success: Messages sent successfully
        - Blocked: Users who blocked the bot
        - Deleted: Deleted accounts
        - Failed: Other errors
    """
    if not ADMINS or message.from_user.id not in ADMINS:
        return
    if not message.reply_to_message:
        await message.reply("**Usage:** Reply to a message with `/broadcast` to send it to all users.")
        return

    status_msg = await message.reply("**Broadcast starting...**")

    total_users = await db.total_users_count()
    success = 0
    blocked = 0
    deleted = 0
    failed = 0
    start_time = time.time()

    async for user in db.get_all_users():
        user_id = user.get("id")
        if not user_id:
            failed += 1
            continue

        try:
            await message.reply_to_message.copy(user_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user_id)
                success += 1
            except:
                failed += 1
        except UserIsBlocked:
            await db.delete_user(user_id)
            blocked += 1
        except InputUserDeactivated:
            await db.delete_user(user_id)
            deleted += 1
        except PeerIdInvalid:
            await db.delete_user(user_id)
            failed += 1
        except Exception:
            failed += 1

        done = success + blocked + deleted + failed
        if done % 20 == 0:
            try:
                await status_msg.edit_text(
                    f"**Broadcast Progress**\n\n"
                    f"Total: {total_users}\n"
                    f"Done: {done}/{total_users}\n"
                    f"Success: {success}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}"
                )
            except:
                pass

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    await status_msg.edit_text(
        f"**Broadcast Complete!**\n\n"
        f"**Time:** {minutes}m {seconds}s\n"
        f"**Total:** {total_users}\n"
        f"**Success:** {success}\n"
        f"**Blocked:** {blocked}\n"
        f"**Deleted:** {deleted}\n"
        f"**Failed:** {failed}"
    )

# ===========================================================================
#   END OF BROADCAST PLUGIN
# ===========================================================================
