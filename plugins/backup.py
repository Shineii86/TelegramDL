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

import os
import asyncio
import logging
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait

from bot import bot, user_client, start_user_client
from database.db import db
from utils.progress import DownloadProgress
from utils.checkpoint import load_checkpoint, save_checkpoint
from config import (
    API_ID, API_HASH, LOGIN_SYSTEM, OUTPUT_DIR, CHANNEL_ID,
    WAITING_TIME, ERROR_MESSAGE, MAX_FILE_SIZE_MB
)

logger = logging.getLogger(__name__)


def get_folder(msg_type):
    folders = {
        "photo": "Photos", "video": "Videos", "audio": "Audios",
        "voice": "Voice", "animation": "GIFs", "sticker": "Stickers",
        "document": "Documents",
    }
    return folders.get(msg_type, "Other")


def get_ext(msg_type):
    exts = {
        "photo": "jpg", "video": "mp4", "audio": "mp3",
        "voice": "ogg", "animation": "mp4", "document": "",
    }
    return exts.get(msg_type, "")


def get_media_type(msg):
    if msg.media == MessageMediaType.PHOTO:
        return "photo"
    elif msg.media == MessageMediaType.VIDEO:
        return "video"
    elif msg.media == MessageMediaType.DOCUMENT:
        return "document"
    elif msg.media == MessageMediaType.AUDIO:
        return "audio"
    elif msg.media == MessageMediaType.VOICE:
        return "voice"
    elif msg.media == MessageMediaType.ANIMATION:
        return "animation"
    elif msg.media == MessageMediaType.STICKER:
        return "sticker"
    return None


def make_caption(msg, folder):
    date_str = msg.date.strftime("%Y-%m-%d") if msg.date else "unknown"
    return f"{folder} | {date_str} | #{msg.id}"


async def download_file(client, msg, dest, user_id):
    for attempt in range(3):
        try:
            await client.download_media(msg, file_name=dest)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except Exception as e:
            logger.error(f"Download failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)
    return False


async def send_file(client, chat_id, file_path, caption, msg):
    for attempt in range(3):
        try:
            if file_path.endswith((".jpg", ".jpeg", ".png", ".webp")):
                await client.send_photo(chat_id, file_path, caption=caption)
            elif file_path.endswith((".mp4", ".mkv", ".avi")):
                duration = 0
                if msg.media == MessageMediaType.VIDEO:
                    vid = getattr(msg, "video", None)
                    if vid and hasattr(vid, "duration"):
                        duration = vid.duration
                await client.send_video(chat_id, file_path, caption=caption, duration=duration)
            elif file_path.endswith((".mp3", ".ogg", ".wav")):
                await client.send_audio(chat_id, file_path, caption=caption)
            else:
                await client.send_document(chat_id, file_path, caption=caption)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except Exception as e:
            logger.error(f"Send failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)
    return False


@bot.on_message(filters.command("backup") & filters.private)
async def backup_cmd(client, message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply(
            "**Usage:** `/backup <channel_url>`\n\n"
            "Backs up all media from a channel to a backup channel.\n"
            "Supports public, private, and restricted channels."
        )
        return

    channel_url = args[1].strip()

    # Get user session for restricted content
    acc = None
    if LOGIN_SYSTEM:
        session = await db.get_session(user_id)
        if session:
            from pyrogram import Client
            acc = Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=session)
            await acc.start()
    else:
        await start_user_client()
        acc = user_client

    if not acc:
        await message.reply("No user session available. Use /login first.")
        return

    try:
        # Parse channel
        chat_id = channel_url
        if "t.me/" in channel_url:
            parts = channel_url.rstrip("/").split("/")
            if "+" in parts[-1] or parts[-1].isdigit():
                chat_id = parts[-1]
            else:
                chat_id = parts[-1]

        # Try to get entity
        try:
            entity = await acc.get_chat(chat_id)
        except Exception:
            try:
                entity = await client.get_chat(chat_id)
            except Exception as e:
                await message.reply(f"Cannot access channel: {e}")
                return

        # Create backup channel
        backup_name = f"{entity.title} [BACKUP]" if hasattr(entity, 'title') else "Backup"
        backup_channel = None

        if CHANNEL_ID:
            try:
                backup_channel = await client.get_chat(int(CHANNEL_ID))
            except:
                pass

        if not backup_channel:
            try:
                backup_channel = await client.create_channel(backup_name, "Auto-created backup channel")
            except Exception as e:
                await message.reply(f"Cannot create backup channel: {e}")
                return

        await message.reply(f"Backing up to: {backup_channel.title}\nStarting...")

        # Count total first
        total = 0
        async for _ in acc.get_chat_history(chat_id):
            total += 1

        # Create progress tracker
        progress = DownloadProgress(client, message.chat.id)
        await progress.create(total)

        # Process messages
        checkpoint = load_checkpoint()
        downloaded_ids = set(checkpoint.get("downloaded", []))
        count = 0
        skip_count = 0
        fail_count = 0

        async for msg in acc.get_chat_history(chat_id):
            if msg.media:
                msg_type = get_media_type(msg)
                if msg_type and msg.id not in downloaded_ids:
                    folder = get_folder(msg_type)
                    ext = get_ext(msg_type)
                    file_name = f"{msg.id}.{ext}" if ext else str(msg.id)
                    file_path = os.path.join(OUTPUT_DIR, folder, file_name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # Check file size
                    media_obj = getattr(msg, msg.media.value, None)
                    if media_obj and hasattr(media_obj, 'file_size'):
                        if media_obj.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                            skip_count += 1
                            progress.update(skipped=skip_count)
                            continue

                    if os.path.exists(file_path):
                        skip_count += 1
                        progress.update(skipped=skip_count)
                        continue

                    # Download
                    progress.update(current_file=f"#{msg.id} ({msg_type})")
                    success = await download_file(acc, msg, file_path, user_id)
                    if success:
                        # Send to backup channel
                        caption = make_caption(msg, folder)
                        sent = await send_file(client, backup_channel.id, file_path, caption, msg)
                        if sent:
                            count += 1
                            progress.update(downloaded=count)
                        else:
                            fail_count += 1
                            progress.update(failed=fail_count)

                        # Cleanup
                        try:
                            os.remove(file_path)
                        except:
                            pass

                        # Save checkpoint
                        downloaded_ids.add(msg.id)
                        if len(downloaded_ids) % 50 == 0:
                            checkpoint["downloaded"] = list(downloaded_ids)
                            save_checkpoint(checkpoint)

                    await progress.update_message()
                    await asyncio.sleep(WAITING_TIME)

        # Final checkpoint save
        checkpoint["downloaded"] = list(downloaded_ids)
        save_checkpoint(checkpoint)

        await progress.finish()

        await message.reply(
            f"**Backup Complete!**\n\n"
            f"Downloaded: {count}\n"
            f"Skipped: {skip_count}\n"
            f"Failed: {fail_count}\n"
            f"Total: {total}"
        )

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        await message.reply(f"Backup failed: {e}")

    finally:
        if acc and acc != user_client:
            try:
                await acc.stop()
            except:
                pass
