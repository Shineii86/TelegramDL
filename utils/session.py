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


class SessionStats:
    def __init__(self, session_limit_hours=12):
        self.start_time = time.time()
        self.session_limit = session_limit_hours * 3600
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0
        self.total = 0

    def elapsed(self):
        return time.time() - self.start_time

    def remaining(self):
        return max(0, self.session_limit - self.elapsed())

    def is_session_low(self, threshold_minutes=30):
        return self.remaining() < threshold_minutes * 60

    def eta(self, files_done):
        if files_done == 0:
            return 0
        avg = self.elapsed() / files_done
        remaining_files = self.total - files_done
        return avg * remaining_files

    def format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"

    def progress_bar(self, percent, length=20):
        filled = int(length * percent / 100)
        bar = "█" * filled + "░" * (length - filled)
        return bar

    def print_stats(self):
        elapsed = self.elapsed()
        remaining = self.remaining()
        usage = (elapsed / self.session_limit) * 100 if self.session_limit > 0 else 0
        done = self.downloaded + self.skipped + self.failed
        eta = self.eta(done) if done > 0 else 0

        bar = self.progress_bar(usage)

        print(f"\n{'=' * 50}")
        print(f"  Session Stats")
        print(f"{'=' * 50}")
        print(f"  Elapsed:    {self.format_time(elapsed)}")
        print(f"  Remaining:  {self.format_time(remaining)}")
        print(f"  Usage:      [{bar}] {usage:.1f}%")
        print(f"  Downloaded: {self.downloaded}")
        print(f"  Skipped:    {self.skipped}")
        print(f"  Failed:     {self.failed}")
        if done > 0:
            print(f"  ETA:        {self.format_time(eta)}")
        print(f"{'=' * 50}\n")

        if remaining < 1800:
            print("  ⚠️  CRITICAL: Less than 30 minutes remaining!")
        elif remaining < 3600:
            print("  ⚠️  WARNING: Less than 1 hour remaining")
        elif remaining < 7200:
            print("  💡 TIP: Less than 2 hours remaining")
