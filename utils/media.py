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

from pyrogram.enums import MessageMediaType


def get_message_type(msg):
    """Determine the type of media in a message."""
    if msg.media:
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
    elif msg.text:
        return "text"
    return None


def get_media_folder(msg_type):
    """Get the folder name for a media type."""
    folders = {
        "photo": "Photos",
        "video": "Videos",
        "audio": "Audios",
        "voice": "Voice",
        "animation": "GIFs",
        "sticker": "Stickers",
        "document": "Documents",
        "text": "Text",
    }
    return folders.get(msg_type, "Other")
