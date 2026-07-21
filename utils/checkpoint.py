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
        Checkpoint system for resuming downloads.
        Saves progress to JSON file.

    FUNCTIONS:
        load_checkpoint  — Load saved progress
        save_checkpoint  — Save progress
        clear_checkpoint — Clear saved progress

    FEATURES:
        FEATURE: CHECKPOINT_SAVE
        FEATURE: CHECKPOINT_LOAD
        FEATURE: CHECKPOINT_CLEAR
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import json

# ===========================================================================
#   CONSTANTS
# ---------------------------------------------------------------------------

CHECKPOINT_FILE = "checkpoint.json"
ACTIVE_USERS_FILE = "active_users.json"

# ===========================================================================
#   FEATURE: CHECKPOINT_LOAD
# ---------------------------------------------------------------------------
#   Loads checkpoint data from JSON file
#   Returns empty structure if file doesn't exist
# ===========================================================================


def load_checkpoint():
    """Load checkpoint data.

    Returns:
        dict: Checkpoint data with downloaded/failed IDs

    Structure:
        {
            "downloaded": [123, 456, ...],
            "failed": [789, ...],
            "stats": {"downloaded": 10, "skipped": 2, "failed": 1}
        }

    Note:
        Returns empty structure if no checkpoint exists
    """
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"downloaded": [], "failed": [], "stats": {"downloaded": 0, "skipped": 0, "failed": 0}}

# ===========================================================================
#   FEATURE: CHECKPOINT_SAVE
# ---------------------------------------------------------------------------
#   Saves checkpoint data to JSON file
#   Called periodically during batch operations
#
#   NOTE: Saves every 50 files to balance performance
# ===========================================================================


def save_checkpoint(data):
    """Save checkpoint data.

    Args:
        data: Checkpoint data to save

    Returns:
        None

    Note:
        Overwrites existing checkpoint file
    """
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)

# ===========================================================================
#   FEATURE: CHECKPOINT_CLEAR
# ---------------------------------------------------------------------------
#   Clears checkpoint file
#   Called after successful completion
# ===========================================================================


def clear_checkpoint():
    """Clear checkpoint data.

    Returns:
        None

    Note:
        Removes checkpoint file entirely
    """
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

# ===========================================================================
#   FEATURE: ACTIVE_USERS_PERSISTENCE
# ---------------------------------------------------------------------------
#   Persists active batch/backup state to JSON file
#   Enables recovery across bot restarts
# ===========================================================================


def load_active_users():
    """Load active users state.

    Returns:
        dict: Active users with their batch/backup state
    """
    if os.path.exists(ACTIVE_USERS_FILE):
        with open(ACTIVE_USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_active_users(data):
    """Save active users state.

    Args:
        data: Active users state to save

    Returns:
        None
    """
    with open(ACTIVE_USERS_FILE, "w") as f:
        json.dump(data, f)


def clear_active_users():
    """Clear active users state.

    Returns:
        None
    """
    if os.path.exists(ACTIVE_USERS_FILE):
        os.remove(ACTIVE_USERS_FILE)

# ===========================================================================
#   END OF CHECKPOINT MODULE
# ===========================================================================
