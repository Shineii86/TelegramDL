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
        Session time tracking for Colab deployments.
        Tracks elapsed time and warns before session expires.

    CLASS:
        SessionStats — Session time tracker

    FEATURES:
        FEATURE: TIME_TRACKING
        FEATURE: EXPIRY_WARNING
        FEATURE: PROGRESS_DISPLAY
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import time

# ===========================================================================
#   FEATURE: SESSION_STATS
# ---------------------------------------------------------------------------
#   Tracks session time and displays statistics
#   Used primarily for Google Colab deployments
#
#   NOTE: Helps prevent unexpected session termination
# ===========================================================================


class SessionStats:
    def __init__(self, session_limit_hours=12):
        """Initialize session tracker.

        Args:
            session_limit_hours: Session duration limit in hours

        Returns:
            None

        Note:
            Default limit is 12 hours (Colab free tier)
        """
        self.start_time = time.time()
        self.session_limit = session_limit_hours * 3600
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0
        self.total = 0

    def elapsed(self):
        """Get elapsed time in seconds.

        Returns:
            float: Seconds since start
        """
        return time.time() - self.start_time

    def remaining(self):
        """Get remaining time in seconds.

        Returns:
            float: Seconds remaining (0 if expired)
        """
        return max(0, self.session_limit - self.elapsed())

    def is_session_low(self, threshold_minutes=30):
        """Check if session time is low.

        Args:
            threshold_minutes: Warning threshold in minutes

        Returns:
            bool: True if below threshold

        Note:
            Default threshold is 30 minutes
        """
        return self.remaining() < threshold_minutes * 60

    def eta(self, files_done):
        """Calculate ETA for remaining files.

        Args:
            files_done: Number of files processed

        Returns:
            float: ETA in seconds

        Formula:
            elapsed / done * remaining
        """
        if files_done == 0:
            return 0
        avg = self.elapsed() / files_done
        remaining_files = self.total - files_done
        return avg * remaining_files

    def format_time(self, seconds):
        """Format seconds to human readable time.

        Args:
            seconds: Time in seconds

        Returns:
            str: Formatted time
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"

    def progress_bar(self, percent, length=20):
        """Generate progress bar.

        Args:
            percent: Completion percentage
            length: Bar length

        Returns:
            str: Progress bar string
        """
        filled = int(length * percent / 100)
        bar = "█" * filled + "░" * (length - filled)
        return bar

    def print_stats(self):
        """Print session statistics to console.

        Displays:
            - Elapsed time
            - Remaining time
            - Usage percentage with bar
            - Download/Skipped/Failed counts
            - ETA
            - Warning messages

        Note:
            Shows warnings at 2h, 1h, and 30min
        """
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

# ===========================================================================
#   END OF SESSION MODULE
# ===========================================================================
