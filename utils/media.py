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
        Media type detection and folder organization.

    FUNCTIONS:
        get_message_type — Detect media type
        get_media_folder — Get folder for type

    FEATURES:
        FEATURE: MEDIA_DETECTION
        FEATURE: FOLDER_ORGANIZATION
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from ftmgram.enums import MessageMediaType

# ===========================================================================
#   FEATURE: MEDIA_DETECTION
# ---------------------------------------------------------------------------
#   Detects media type from Telegram message
#   Used for routing files to correct folders
# ===========================================================================


def get_message_type(msg):
    """Determine the type of media in a message.

    Args:
        msg: Telegram message object

    Returns:
        str: Media type (photo, video, document, audio,
             voice, animation, sticker, text) or None

    Example:
        >>> get_message_type(msg)
        "video"
    """
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

# ===========================================================================
#   FEATURE: FOLDER_ORGANIZATION
# ---------------------------------------------------------------------------
#   Maps media types to folder names
#   Used for organizing downloaded files
# ===========================================================================


def get_media_folder(msg_type):
    """Get the folder name for a media type.

    Args:
        msg_type: Media type string

    Returns:
        str: Folder name (Photos, Videos, Audios, etc.)

    Example:
        >>> get_media_folder("video")
        "Videos"
    """
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

# ===========================================================================
#   END OF MEDIA MODULE
# ===========================================================================
