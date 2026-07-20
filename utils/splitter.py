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
        File splitting utility for files >2GB.
        Splits into 1.9GB parts for Telegram upload.

    FUNCTIONS:
        split_file     — Split file into parts
        cleanup_parts  — Remove part files after upload
        get_part_name  — Generate part filename

    FEATURES:
        FEATURE: FILE_SPLITTING
        FEATURE: PART_CLEANUP
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import math
import logging

logger = logging.getLogger(__name__)

# ===========================================================================
#   CONSTANTS
# ---------------------------------------------------------------------------
#   PART_SIZE: Maximum part size (1.9GB)
#   NOTE: Slightly under 2GB to account for metadata
# ===========================================================================

PART_SIZE = int(1.9 * 1024 * 1024 * 1024)  # 1.9GB per part

# ===========================================================================
#   FEATURE: FILE_SPLITTING
# ---------------------------------------------------------------------------
#   Splits files into parts for Telegram upload.
#   Files <2GB are returned as-is.
#
#   NOTE: Uses chunked reading for memory efficiency
# ===========================================================================


async def split_file(file_path, max_size=PART_SIZE):
    """Split file into parts if it exceeds max_size.

    Args:
        file_path: Path to file
        max_size: Maximum part size (default: 1.9GB)

    Returns:
        list: List of part file paths

    Process:
        1. Check file size
        2. Calculate number of parts
        3. Create parts directory
        4. Read and write chunks
        5. Return part paths

    Note:
        Files under max_size returned as single-item list
    """
    file_size = os.path.getsize(file_path)
    
    if file_size <= max_size:
        return [file_path]
    
    total_parts = math.ceil(file_size / max_size)
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    part_dir = os.path.join(os.path.dirname(file_path), "parts")
    os.makedirs(part_dir, exist_ok=True)
    
    part_paths = []
    
    try:
        with open(file_path, "rb") as f:
            for part_num in range(1, total_parts + 1):
                part_name = f"{name}_part{part_num}{ext}"
                part_path = os.path.join(part_dir, part_name)
                
                bytes_read = 0
                with open(part_path, "wb") as part_f:
                    while bytes_read < max_size:
                        chunk = f.read(min(8192, max_size - bytes_read))
                        if not chunk:
                            break
                        part_f.write(chunk)
                        bytes_read += len(chunk)
                
                part_paths.append(part_path)
                logger.info(f"Created part {part_num}/{total_parts}: {part_name}")
    
    except Exception as e:
        logger.error(f"File splitting failed: {e}")
        # Cleanup partial parts
        for p in part_paths:
            if os.path.exists(p):
                os.remove(p)
        return [file_path]
    
    return part_paths


def cleanup_parts(part_paths, original_path):
    """Cleanup part files after upload.

    Args:
        part_paths: List of part file paths
        original_path: Original file path

    Returns:
        None

    Note:
        Only removes part files, not original
        Also removes parts directory if empty
    """
    for p in part_paths:
        if p != original_path and os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
    
    # Cleanup parts directory
    part_dir = os.path.join(os.path.dirname(original_path), "parts")
    if os.path.exists(part_dir):
        try:
            os.rmdir(part_dir)
        except Exception:
            pass

# ===========================================================================
#   END OF SPLITTER MODULE
# ===========================================================================
