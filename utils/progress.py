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
        Download progress tracker with rich progress bar,
        speed calculation, and ETA estimation.

    CLASS:
        DownloadProgress — Main progress tracker

    FEATURES:
        FEATURE: PROGRESS_BAR
        FEATURE: SPEED_CALCULATION
        FEATURE: ETA_ESTIMATION
        FEATURE: RATE_LIMITING
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import time
from ftmgram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ===========================================================================
#   FEATURE: DOWNLOAD_PROGRESS
# ---------------------------------------------------------------------------
#   Tracks download progress with:
#   - Visual progress bar
#   - Speed calculation (msg/s)
#   - ETA estimation
#   - Rate limiting (2s between updates)
#
#   NOTE: Rate limiting prevents Telegram API flood
# ===========================================================================


class DownloadProgress:
    def __init__(self, client, chat_id, message_id=None):
        """Initialize progress tracker.

        Args:
            client: Pyrogram client
            chat_id: Chat ID to send updates
            message_id: Optional message ID to edit

        Returns:
            None

        Note:
            Starts timer on initialization
        """
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
        """Set total file count.

        Args:
            total: Total number of files

        Returns:
            None
        """
        self.total = total

    def update(self, downloaded=None, skipped=None, failed=None, current_file=None):
        """Update progress counters.

        Args:
            downloaded: Downloaded count
            skipped: Skipped count
            failed: Failed count
            current_file: Current file description

        Returns:
            None

        Note:
            Only updates provided values (None skips)
        """
        if downloaded is not None:
            self.downloaded = downloaded
        if skipped is not None:
            self.skipped = skipped
        if failed is not None:
            self.failed = failed
        if current_file is not None:
            self.current_file = current_file

    def get_eta(self):
        """Calculate estimated time remaining.

        Returns:
            float: ETA in seconds

        Formula:
            elapsed / done * remaining
        """
        done = self.downloaded + self.skipped + self.failed
        if done == 0:
            return 0
        elapsed = time.time() - self.start_time
        avg = elapsed / done
        remaining = self.total - done
        return avg * remaining

    def get_speed(self):
        """Calculate processing speed.

        Returns:
            float: Messages per second
        """
        done = self.downloaded + self.skipped + self.failed
        if done == 0:
            return 0
        elapsed = time.time() - self.start_time
        return done / elapsed if elapsed > 0 else 0

    def format_time(self, seconds):
        """Format seconds to human readable time.

        Args:
            seconds: Time in seconds

        Returns:
            str: Formatted time (e.g., "5m 30s", "1h 15m")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"

    def format_size(self, size):
        """Format bytes to human readable size.

        Args:
            size: Size in bytes

        Returns:
            str: Formatted size (e.g., "1.5 MB")
        """
        if size < 1024:
            return f"{size:.1f} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / 1024 / 1024:.1f} MB"
        else:
            return f"{size / 1024 / 1024 / 1024:.2f} GB"

    def get_progress_bar(self, percent, length=15):
        """Generate visual progress bar.

        Args:
            percent: Completion percentage (0-100)
            length: Bar length in characters

        Returns:
            str: Progress bar (e.g., "██████░░░░░░░░░")
        """
        filled = int(length * percent / 100)
        bar = "█" * filled + "░" * (length - filled)
        return bar

    def build_message(self):
        """Build progress message text.

        Returns:
            str: Formatted progress message

        Includes:
            - Progress bar with percentage
            - Speed (msg/s)
            - Done/Total count
            - Skipped/Failed counts
            - Elapsed time
            - ETA
            - Current file
        """
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
        """Get cancel button keyboard.

        Returns:
            InlineKeyboardMarkup: Cancel button
        """
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_download")]
        ])

    async def create(self, total=None):
        """Create initial progress message.

        Args:
            total: Total file count (optional)

        Returns:
            Message: Status message

        Note:
            Sends message with cancel button
        """
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
        """Update progress message.

        Returns:
            None

        Note:
            Rate limited to 1 update per 2 seconds
            to prevent Telegram API flood
        """
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
        """Show completion message.

        Returns:
            None

        Displays:
            - Total files processed
            - Downloaded/Skipped/Failed counts
            - Total time taken
        """
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

# ===========================================================================
#   END OF PROGRESS MODULE
# ===========================================================================
