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
        yt-dlp integration plugin. Downloads from YouTube, Instagram,
        Facebook, TikTok, and 100+ other sites.

    COMMANDS:
        /dl <url>  — Download video from URL
        /adl <url> — Download audio only from URL

    FEATURES:
        FEATURE: YTDL_COMMAND
        FEATURE: AUDIO_ONLY_COMMAND
        FEATURE: FILE_SPLITTING
        FEATURE: AUDIO_METADATA
        FEATURE: CONCURRENT_LIMIT
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import asyncio
import logging
from ftmgram import filters
from ftmgram.types import Message
from bot import bot
from database.db import db
from utils.ytdl import is_ytdl_url, download_with_ytdl, get_video_info
from utils.splitter import split_file, cleanup_parts
from utils.audio_metadata import embed_audio_metadata
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)

# ===========================================================================
#   GLOBAL STATE
# ---------------------------------------------------------------------------
#   ongoing_downloads: Track concurrent downloads per user
#   NOTE: Prevents multiple simultaneous downloads per user
# ===========================================================================

ongoing_downloads = {}

# ===========================================================================
#   FEATURE: YTDL_COMMAND
# ---------------------------------------------------------------------------
#   /dl <url> — Download video from URL
#   Supports 100+ sites via yt-dlp
#
#   Process:
#   1. Validate URL
#   2. Get video info
#   3. Download with yt-dlp
#   4. Split if >2GB
#   5. Upload to user
#   6. Cleanup
#
#   FEATURE: FILE_SPLITTING
# ===========================================================================


@bot.on_message(filters.command("dl") & filters.private)
async def dl_cmd(client, message: Message):
    """Handle /dl command for video downloads.

    Args:
        client: Bot client
        message: User message with URL

    Returns:
        None

    Usage:
        /dl https://youtube.com/watch?v=xxx

    Supported Sites:
        YouTube, Instagram, Facebook, TikTok,
        Twitter/X, Reddit, Vimeo, SoundCloud,
        Twitch, and 100+ more sites

    Process:
        1. Check ban status
        2. Check daily limit
        3. Check concurrent download
        4. Validate URL
        5. Get video info
        6. Download with yt-dlp
        7. Split if >2GB
        8. Upload to user
        9. Increment usage
    """
    user_id = message.from_user.id

    # Check ban
    if await db.is_banned(user_id):
        await message.reply("**❌ You are banned** from using this bot.")
        return

    # Check daily limit
    if not await db.check_daily_limit(user_id):
        await message.reply("**📊 Daily Limit Reached**\n\nWait 24 hours or ask admin for premium.")
        return

    # Check concurrent download
    if ongoing_downloads.get(user_id):
        await message.reply("**⏳ Download in progress**\n\nPlease wait for current download to finish.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**📥 Download from URL**\n\n"
            "**Usage:**\n"
            "- `/dl <url>` — Download video\n"
            "- `/adl <url>` — Download audio only\n\n"
            "**Supported:**\n"
            "YouTube, Instagram, Facebook, TikTok,\n"
            "Twitter/X, Reddit, Vimeo, SoundCloud,\n"
            "and 100+ more sites."
        )
        return

    url = args[1].strip()

    if not is_ytdl_url(url):
        await message.reply("**❌ Unsupported URL**\n\nThis URL is not supported by yt-dlp.")
        return

    # Get video info first
    status_msg = await message.reply("**🔍 Fetching video info...**")

    info = await get_video_info(url)
    if info:
        title = info.get('title', 'Unknown')[:50]
        duration = info.get('duration', 0)
        uploader = info.get('uploader', 'Unknown')
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"

        await status_msg.edit_text(
            f"**📥 Found Video**\n\n"
            f"**Title:** {title}\n"
            f"**Uploader:** {uploader}\n"
            f"**Duration:** {duration_str}\n\n"
            f"Starting download..."
        )

    # Mark as ongoing
    ongoing_downloads[user_id] = True

    try:
        output_dir = os.path.join(OUTPUT_DIR, f"ytdl_{user_id}")
        os.makedirs(output_dir, exist_ok=True)

        # Download
        downloaded = await download_with_ytdl(url, output_dir, audio_only=False)

        if not downloaded:
            await status_msg.edit_text("**❌ Download Failed**\n\nCould not download the video.")
            return

        await status_msg.edit_text("**📤 Uploading...**")

        for file_path in downloaded:
            if not os.path.exists(file_path):
                continue

            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)

            # Apply rename tag
            rename_tag = await db.get_rename_tag(user_id)
            if rename_tag:
                name, ext = os.path.splitext(file_name)
                file_name = f"{rename_tag}{ext}"

            # Split if >2GB
            parts = await split_file(file_path)

            # Get custom thumbnail
            thumb = await db.get_thumbnail(user_id)

            for i, part_path in enumerate(parts):
                part_name = os.path.basename(part_path)

                if len(parts) > 1:
                    caption = f"**{file_name}** (Part {i+1}/{len(parts)})"
                else:
                    caption = f"**{file_name}**"

                # Upload based on file type
                ext = os.path.splitext(part_path)[1].lower()

                try:
                    if ext in ('.mp4', '.mkv', '.avi', '.webm'):
                        await client.send_video(
                            message.chat.id, part_path,
                            caption=caption,
                            thumb=thumb
                        )
                    elif ext in ('.mp3', '.m4a', '.aac', '.ogg', '.wav', '.flac'):
                        await client.send_audio(
                            message.chat.id, part_path,
                            caption=caption,
                            thumb=thumb
                        )
                    elif ext in ('.jpg', '.jpeg', '.png', '.webp'):
                        await client.send_photo(
                            message.chat.id, part_path,
                            caption=caption
                        )
                    else:
                        await client.send_document(
                            message.chat.id, part_path,
                            caption=caption,
                            thumb=thumb
                        )
                except Exception as e:
                    logger.error(f"Upload failed: {e}")
                    await message.reply(f"**Upload failed for {part_name}:** {e}")

            # Cleanup parts
            cleanup_parts(parts, file_path)

        # Increment usage
        await db.increment_daily_usage(user_id)

        # Dump chat forwarding
        dump_chat = await db.get_dump_chat(user_id)
        if dump_chat and downloaded:
            try:
                for file_path in downloaded:
                    if os.path.exists(file_path):
                        await client.send_video(dump_chat, file_path) if file_path.endswith(('.mp4', '.mkv')) else await client.send_document(dump_chat, file_path)
            except Exception:
                pass

        await status_msg.edit_text(f"**✅ Download Complete!**\n\nSent {len(downloaded)} file(s).")

    except Exception as e:
        logger.error(f"yt-dlp error: {e}")
        await status_msg.edit_text(f"**❌ Error:** {e}")

    finally:
        ongoing_downloads.pop(user_id, None)
        # Cleanup output dir
        try:
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)
        except Exception:
            pass

# ===========================================================================
#   FEATURE: AUDIO_ONLY_COMMAND
# ---------------------------------------------------------------------------
#   /adl <url> — Download audio only as MP3 (320kbps)
#   Embeds metadata (title, artist, album art)
#
#   FEATURE: AUDIO_METADATA
# ===========================================================================


@bot.on_message(filters.command("adl") & filters.private)
async def adl_cmd(client, message: Message):
    """Handle /adl command for audio downloads.

    Args:
        client: Bot client
        message: User message with URL

    Returns:
        None

    Usage:
        /adl https://youtube.com/watch?v=xxx

    Process:
        1. Check ban/limit
        2. Download audio only
        3. Embed metadata
        4. Upload as audio file

    Note:
        Downloads as MP3 320kbps with metadata
    """
    user_id = message.from_user.id

    if await db.is_banned(user_id):
        await message.reply("**❌ You are banned** from using this bot.")
        return

    if not await db.check_daily_limit(user_id):
        await message.reply("**📊 Daily Limit Reached**\n\nWait 24 hours or ask admin for premium.")
        return

    if ongoing_downloads.get(user_id):
        await message.reply("**⏳ Download in progress**\n\nPlease wait for current download to finish.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**🎵 Download Audio**\n\n"
            "**Usage:** `/adl <url>`\n\n"
            "Downloads audio as MP3 (320kbps)."
        )
        return

    url = args[1].strip()

    if not is_ytdl_url(url):
        await message.reply("**❌ Unsupported URL**")
        return

    status_msg = await message.reply("**🔍 Fetching audio info...**")
    ongoing_downloads[user_id] = True

    try:
        output_dir = os.path.join(OUTPUT_DIR, f"ytdl_audio_{user_id}")
        os.makedirs(output_dir, exist_ok=True)

        downloaded = await download_with_ytdl(url, output_dir, audio_only=True)

        if not downloaded:
            await status_msg.edit_text("**❌ Download Failed**")
            return

        await status_msg.edit_text("**📤 Uploading audio...**")

        for file_path in downloaded:
            if not os.path.exists(file_path):
                continue

            # Embed metadata (blocking call wrapped in thread)
            await asyncio.to_thread(embed_audio_metadata, file_path, title=os.path.basename(file_path))

            thumb = await db.get_thumbnail(user_id)

            try:
                await client.send_audio(
                    message.chat.id, file_path,
                    caption=f"**{os.path.basename(file_path)}**",
                    thumb=thumb
                )
            except Exception as e:
                await message.reply(f"**Upload failed:** {e}")

        await db.increment_daily_usage(user_id)
        await status_msg.edit_text(f"**✅ Audio Download Complete!**")

    except Exception as e:
        await status_msg.edit_text(f"**❌ Error:** {e}")

    finally:
        ongoing_downloads.pop(user_id, None)
        try:
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)
        except Exception:
            pass

# ===========================================================================
#   END OF YTDL PLUGIN
# ===========================================================================
