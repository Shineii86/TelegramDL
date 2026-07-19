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

import time
import threading


class KeepAlive:
    def __init__(self, interval_minutes=30):
        self.interval = interval_minutes * 60
        self.running = False
        self.thread = None
        self.ping_count = 0

    def _ping_loop(self):
        while self.running:
            time.sleep(self.interval)
            if self.running:
                self.ping_count += 1
                ts = time.strftime("%H:%M:%S")
                print(f"  [Keep-Alive] Ping #{self.ping_count} at {ts}")

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.thread.start()
            print(f"  [Keep-Alive] Started (interval: {self.interval // 60}min)")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("  [Keep-Alive] Stopped")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
