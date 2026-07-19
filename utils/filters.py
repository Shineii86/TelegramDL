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
        Message filtering utilities for batch downloads.

    FUNCTIONS:
        filter_by_date — Filter by date range
        filter_by_type — Filter by media type

    FEATURES:
        FEATURE: DATE_FILTER
        FEATURE: TYPE_FILTER
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from datetime import datetime

# ===========================================================================
#   FEATURE: DATE_FILTER
# ---------------------------------------------------------------------------
#   Filters messages by date range
#   Used for selective batch downloads
# ===========================================================================


def filter_by_date(msg, date_start=None, date_end=None):
    """Filter message by date range.

    Args:
        msg: Telegram message
        date_start: Start date (inclusive)
        date_end: End date (inclusive)

    Returns:
        bool: True if message passes filter

    Note:
        Returns True if no dates specified
    """
    if not date_start and not date_end:
        return True

    msg_date = msg.date
    if isinstance(msg_date, datetime):
        pass
    else:
        return True

    if date_start:
        if msg_date < date_start:
            return False
    if date_end:
        if msg_date > date_end:
            return False
    return True

# ===========================================================================
#   FEATURE: TYPE_FILTER
# ---------------------------------------------------------------------------
#   Filters messages by media type
#   Supports: photo, video, audio, all
# ===========================================================================


def filter_by_type(msg, media_type="all"):
    """Filter message by media type.

    Args:
        msg: Telegram message
        media_type: Filter type (photo, video, audio, all)

    Returns:
        bool: True if message passes filter

    Note:
        Returns True for "all" or unknown types
    """
    if media_type == "all":
        return True

    from pyrogram.enums import MessageMediaType

    type_map = {
        "photo": MessageMediaType.PHOTO,
        "video": MessageMediaType.VIDEO,
        "audio": MessageMediaType.AUDIO,
    }

    if media_type in type_map:
        return msg.media == type_map[media_type]
    return True

# ===========================================================================
#   END OF FILTERS MODULE
# ===========================================================================
