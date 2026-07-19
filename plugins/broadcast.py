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

Framework:  Kurigram (Pyrogram Fork)

Disclaimer:
    This bot is for educational purposes only.
    Use responsibly and respect Telegram's Terms of Service.
"""

import time
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid

from bot import bot
from database.db import db
from config import ADMINS


@bot.on_message(filters.command("broadcast"))
async def broadcast_cmd(client, message: Message):
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
