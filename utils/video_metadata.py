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
        Video metadata extraction using OpenCV.
        Extracts duration, width, height from video files.
        Generates thumbnails using ffmpeg.

    DEPENDENCIES:
        opencv-python (optional)
        ffmpeg (system dependency)

    FALLBACK:
        Returns defaults if OpenCV not installed
============================================================================
"""

import os
import logging
import subprocess

logger = logging.getLogger(__name__)

# Try importing OpenCV
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not installed. Video metadata extraction disabled.")


def get_video_metadata(file_path):
    """Extract video metadata using OpenCV.

    Args:
        file_path: Path to video file

    Returns:
        dict: {duration, width, height, fps} or defaults

    Note:
        Falls back to defaults if OpenCV not available or file invalid
    """
    defaults = {"duration": 0, "width": 0, "height": 0, "fps": 0}

    if not OPENCV_AVAILABLE:
        return defaults

    if not os.path.exists(file_path):
        return defaults

    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return defaults

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        duration = 0
        if fps > 0:
            duration = int(frame_count / fps)

        cap.release()

        return {
            "duration": duration,
            "width": width,
            "height": height,
            "fps": fps
        }
    except Exception as e:
        logger.error(f"OpenCV metadata extraction failed: {e}")
        return defaults


def generate_thumbnail(file_path, output_path=None, time_offset=None):
    """Generate thumbnail from video using ffmpeg.

    Args:
        file_path: Path to video file
        output_path: Output path for thumbnail (default: file_path.jpg)
        time_offset: Time offset in seconds (default: middle of video)

    Returns:
        str: Path to thumbnail or None

    Note:
        Falls back to None if ffmpeg not available
    """
    if not os.path.exists(file_path):
        return None

    if output_path is None:
        output_path = file_path.rsplit(".", 1)[0] + ".jpg"

    try:
        # Get video duration for middle frame
        if time_offset is None:
            duration = get_video_duration(file_path)
            if duration > 0:
                time_offset = duration // 2
            else:
                time_offset = 1

        # Generate thumbnail with ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(time_offset),
            "-i", file_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.error(f"Thumbnail generation failed: {e}")
    except Exception as e:
        logger.error(f"Thumbnail generation error: {e}")

    return None


def get_video_duration(file_path):
    """Get video duration using ffprobe.

    Args:
        file_path: Path to video file

    Returns:
        int: Duration in seconds or 0
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return int(float(result.stdout.strip()))
    except Exception:
        pass
    return 0
