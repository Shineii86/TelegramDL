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
import os
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class DownloadProgress:
    def __init__(self, client, chat_id, message_id=None):
        self.client = client
        self.chat_id = chat_id
        self.message_id = message_id
        self.start_time = time.time()
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0
        self.total = 0
        self.current_file = ""
        self.status_msg = None
        self.last_update = 0

    def set_total(self, total):
        self.total = total

    def update(self, downloaded=None, skipped=None, failed=None, current_file=None):
        if downloaded is not None:
            self.downloaded = downloaded
        if skipped is not None:
            self.skipped = skipped
        if failed is not None:
            self.failed = failed
        if current_file is not None:
            self.current_file = current_file

    def get_eta(self):
        done = self.downloaded + self.skipped + self.failed
        if done == 0:
            return 0
        elapsed = time.time() - self.start_time
        avg = elapsed / done
        remaining = self.total - done
        return avg * remaining

    def get_speed(self):
        done = self.downloaded + self.skipped + self.failed
        if done == 0:
            return 0
        elapsed = time.time() - self.start_time
        return done / elapsed if elapsed > 0 else 0

    def format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"

    def format_size(self, size):
        if size < 1024:
            return f"{size:.1f} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / 1024 / 1024:.1f} MB"
        else:
            return f"{size / 1024 / 1024 / 1024:.2f} GB"

    def get_progress_bar(self, percent, length=15):
        filled = int(length * percent / 100)
        bar = "█" * filled + "░" * (length - filled)
        return bar

    def build_message(self):
        done = self.downloaded + self.skipped + self.failed
        if self.total > 0:
            percent = done / self.total * 100
        else:
            percent = 0

        bar = self.get_progress_bar(percent)
        eta = self.get_eta()
        elapsed = time.time() - self.start_time
        speed = self.get_speed()

        text = (
            f"**📥 Downloading...**\n\n"
            f"`[{bar}]` **{percent:.1f}%**\n\n"
            f"**Speed:** {speed:.1f} msg/s\n"
            f"**Done:** {done}/{self.total}\n"
            f"**Skipped:** {self.skipped}\n"
            f"**Failed:** {self.failed}\n"
            f"**Remaining:** {self.total - done}\n\n"
            f"**Elapsed:** {self.format_time(elapsed)}\n"
            f"**ETA:** {self.format_time(eta)}\n"
        )

        if self.current_file:
            text += f"\n**Current:** `{self.current_file}`"

        return text

    def get_cancel_keyboard(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_download")]
        ])

    async def create(self, total=None):
        if total:
            self.total = total
        self.start_time = time.time()
        self.status_msg = await self.client.send_message(
            self.chat_id,
            self.build_message(),
            reply_markup=self.get_cancel_keyboard()
        )
        return self.status_msg

    async def update_message(self):
        now = time.time()
        if now - self.last_update < 2:
            return
        self.last_update = now

        if self.status_msg:
            try:
                await self.status_msg.edit_text(
                    self.build_message(),
                    reply_markup=self.get_cancel_keyboard()
                )
            except Exception:
                pass

    async def finish(self):
        done = self.downloaded + self.skipped + self.failed
        elapsed = time.time() - self.start_time
        text = (
            f"**✅ Download Complete!**\n\n"
            f"**Total:** {self.total}\n"
            f"**Downloaded:** {self.downloaded}\n"
            f"**Skipped:** {self.skipped}\n"
            f"**Failed:** {self.failed}\n"
            f"**Time:** {self.format_time(elapsed)}"
        )
        if self.status_msg:
            try:
                await self.status_msg.edit_text(text)
            except Exception:
                await self.client.send_message(self.chat_id, text)
