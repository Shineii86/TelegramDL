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
        ZIP archive creation utility.

    FUNCTIONS:
        create_zip — Create ZIP from files

    FEATURES:
        FEATURE: ZIP_CREATION
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os

# ===========================================================================
#   FEATURE: ZIP_CREATION
# ---------------------------------------------------------------------------
#   Creates ZIP archives from files
#   Used for batch downloads
# ===========================================================================


def create_zip(files, zip_name):
    """Create a zip archive from files.

    Args:
        files: List of file paths
        zip_name: Output ZIP filename

    Returns:
        str: Path to created ZIP file

    Note:
        Only includes existing files
        Uses DEFLATED compression
    """
    import zipfile
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))
    return zip_name

# ===========================================================================
#   END OF ARCHIVE MODULE
# ===========================================================================
