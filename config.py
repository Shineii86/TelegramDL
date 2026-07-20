#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
    PROJECT:  TelegramDL - Advanced Telegram Downloader Bot
    AUTHOR:   Shinei Nouzen (Shineii86)
    LICENSE:  MIT License (c) 2024-2026
    VERSION:  See __version__ below
    REPO:     https://github.com/Shineii86/TelegramDL
    CONTACT:  https://t.me/Shineii86 | ikx7a@hotmail.com
============================================================================
    DESCRIPTION:
        Central configuration module. All settings are loaded from
        environment variables with sensible defaults. Single source
        of truth for __version__.

    FRAMEWORK: ftmgram (Bot API 10.1)
    PYTHON:    3.10+
============================================================================
    DISCLAIMER:
        This bot is for educational purposes only.
        Use responsibly and respect Telegram's Terms of Service.
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from os import environ

# ===========================================================================
#   VERSION — Single source of truth (update only here)
# ===========================================================================

__version__ = "2.0.0"

# ===========================================================================
#   TELEGRAM API CREDENTIALS
# ---------------------------------------------------------------------------
#   Get these from https://my.telegram.org
#   API_ID must be integer, API_HASH is string
# ===========================================================================

API_ID = int(environ.get("API_ID", "0"))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# ===========================================================================
#   USER SESSION — Restricted Content Access
# ---------------------------------------------------------------------------
#   STRING_SESSION: Pyrogram session string for user client
#   LOGIN_SYSTEM:   If True, each user logs in with own phone
#                   If False, single global session is used
#   TIP: Generate session with /login command or gen_session.py
# ===========================================================================

STRING_SESSION = environ.get("STRING_SESSION", "")
LOGIN_SYSTEM = environ.get("LOGIN_SYSTEM", "true").lower() == "true"

# ===========================================================================
#   DATABASE — MongoDB Connection
# ---------------------------------------------------------------------------
#   DB_URI:  MongoDB connection string (required if LOGIN_SYSTEM=True)
#   DB_NAME: Database name (default: telegramdl)
# ===========================================================================

DB_URI = environ.get("DB_URI", "")
DB_NAME = environ.get("DB_NAME", "telegramdl")

# ===========================================================================
#   ADMIN SETTINGS
# ---------------------------------------------------------------------------
#   ADMINS:       Comma-separated list of admin user IDs
#   CHANNEL_ID:   Channel ID for auto-upload (with -100 prefix)
#   WAITING_TIME: Delay between messages (anti-flood)
# ===========================================================================

ADMINS_RAW = environ.get("ADMINS", "")
ADMINS = [int(x.strip()) for x in ADMINS_RAW.split(",") if x.strip().isdigit()] if ADMINS_RAW else []
CHANNEL_ID = environ.get("CHANNEL_ID", "")
LOG_CHANNEL = environ.get("LOG_CHANNEL", "")
WAITING_TIME = int(environ.get("WAITING_TIME", "10"))
ERROR_MESSAGE = environ.get("ERROR_MESSAGE", "true").lower() == "true"
ADMIN_CONTACT = environ.get("ADMIN_CONTACT", "https://t.me/Shineii86")

# ===========================================================================
#   DOWNLOAD SETTINGS
# ---------------------------------------------------------------------------
#   OUTPUT_DIR:          Download directory
#   MAX_FILE_SIZE_MB:    Skip files larger than this (MB)
#   TYPE_FILTER:         Filter: all, photo, video, audio
#   PARALLEL_DOWNLOADS:  Max concurrent downloads
# ===========================================================================

OUTPUT_DIR = environ.get("OUTPUT_DIR", "./downloads")
MAX_FILE_SIZE_MB = int(environ.get("MAX_FILE_SIZE_MB", "2048"))
TYPE_FILTER = environ.get("TYPE_FILTER", "all")
PARALLEL_DOWNLOADS = int(environ.get("PARALLEL_DOWNLOADS", "3"))

# ===========================================================================
#   BACKUP SETTINGS
# ---------------------------------------------------------------------------
#   BACKUP_TO_TELEGRAM: Enable auto-backup to channel
#   FORWARD_MODE:       Use forwarding (faster) vs re-upload
#   BACKUP_CHANNEL:     Target channel ID for backups
# ===========================================================================

BACKUP_TO_TELEGRAM = environ.get("BACKUP_TO_TELEGRAM", "true").lower() == "true"
FORWARD_MODE = environ.get("FORWARD_MODE", "true").lower() == "true"
BACKUP_CHANNEL = environ.get("BACKUP_CHANNEL", "")

# ===========================================================================
#   CAPTION SETTINGS
# ---------------------------------------------------------------------------
#   CAPTION_ENABLED:         Add captions to uploads
#   KEEP_ORIGINAL_CAPTION:   Preserve source caption
# ===========================================================================

CAPTION_ENABLED = environ.get("CAPTION_ENABLED", "true").lower() == "true"
KEEP_ORIGINAL_CAPTION = environ.get("KEEP_ORIGINAL_CAPTION", "true").lower() == "true"

# ===========================================================================
#   PREMIUM SYSTEM
# ---------------------------------------------------------------------------
#   FREE_DAILY_LIMIT:        Max downloads per day (free users)
#   FREE_MAX_FILE_SIZE_MB:   Max file size for free users (MB)
#   PREMIUM_MAX_FILE_SIZE_MB: Max file size for premium users (MB)
# ===========================================================================

FREE_DAILY_LIMIT = int(environ.get("FREE_DAILY_LIMIT", "10"))
FREE_MAX_FILE_SIZE_MB = int(environ.get("FREE_MAX_FILE_SIZE_MB", "2048"))
PREMIUM_MAX_FILE_SIZE_MB = int(environ.get("PREMIUM_MAX_FILE_SIZE_MB", "4096"))

# ===========================================================================
#   COLAB / KEEP-ALIVE SETTINGS
# ---------------------------------------------------------------------------
#   KEEP_ALIVE:           Prevent idle timeout
#   KEEP_ALIVE_INTERVAL:  Ping interval (minutes)
#   USE_CHECKPOINT:       Save progress for resume
#   SESSION_LIMIT_HOURS:  Max session duration (hours)
# ===========================================================================

KEEP_ALIVE = environ.get("KEEP_ALIVE", "true").lower() == "true"
KEEP_ALIVE_INTERVAL = int(environ.get("KEEP_ALIVE_INTERVAL", "30"))
USE_CHECKPOINT = environ.get("USE_CHECKPOINT", "true").lower() == "true"
SESSION_LIMIT_HOURS = int(environ.get("SESSION_LIMIT_HOURS", "12"))

# ===========================================================================
#   END OF CONFIG
# ===========================================================================
