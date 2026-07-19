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
import json

CHECKPOINT_FILE = "checkpoint.json"


def load_checkpoint():
    """Load checkpoint data."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"downloaded": [], "failed": [], "stats": {"downloaded": 0, "skipped": 0, "failed": 0}}


def save_checkpoint(data):
    """Save checkpoint data."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)


def clear_checkpoint():
    """Clear checkpoint data."""
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
