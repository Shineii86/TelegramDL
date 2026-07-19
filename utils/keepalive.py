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
        Keep-alive utility for Colab/VPS deployments.
        Prevents idle timeout with periodic pings.

    CLASS:
        KeepAlive — Keep-alive manager

    FEATURES:
        FEATURE: PERIODIC_PING
        FEATURE: THREAD_BASED
        FEATURE: CONTEXT_MANAGER
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import time
import threading

# ===========================================================================
#   FEATURE: KEEP_ALIVE
# ---------------------------------------------------------------------------
#   Prevents idle timeout with periodic console pings.
#   Runs in background thread.
#
#   NOTE: Useful for Colab (90min idle limit) and VPS
# ===========================================================================


class KeepAlive:
    def __init__(self, interval_minutes=30):
        """Initialize keep-alive manager.

        Args:
            interval_minutes: Ping interval in minutes

        Returns:
            None

        Note:
            Default interval is 30 minutes
        """
        self.interval = interval_minutes * 60
        self.running = False
        self.thread = None
        self.ping_count = 0

    def _ping_loop(self):
        """Background ping loop.

        Runs until stopped, printing ping messages
        at configured interval.
        """
        while self.running:
            time.sleep(self.interval)
            if self.running:
                self.ping_count += 1
                ts = time.strftime("%H:%M:%S")
                print(f"  [Keep-Alive] Ping #{self.ping_count} at {ts}")

    def start(self):
        """Start keep-alive background thread.

        Returns:
            None

        Note:
            Daemon thread (stops when main thread exits)
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.thread.start()
            print(f"  [Keep-Alive] Started (interval: {self.interval // 60}min)")

    def stop(self):
        """Stop keep-alive thread.

        Returns:
            None
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("  [Keep-Alive] Stopped")

    def __enter__(self):
        """Context manager entry.

        Returns:
            KeepAlive: Self instance
        """
        self.start()
        return self

    def __exit__(self, *args):
        """Context manager exit.

        Stops keep-alive on context exit.
        """
        self.stop()

# ===========================================================================
#   END OF KEEPALIVE MODULE
# ===========================================================================
