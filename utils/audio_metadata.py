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
        Audio metadata embedding using mutagen.
        Supports MP3, M4A, FLAC formats.

    FUNCTIONS:
        embed_audio_metadata — Embed metadata into audio
        extract_audio_thumbnail — Extract album art

    FEATURES:
        FEATURE: MP3_METADATA
        FEATURE: M4A_METADATA
        FEATURE: FLAC_METADATA
        FEATURE: ALBUM_ART
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import logging

logger = logging.getLogger(__name__)

# ===========================================================================
#   FEATURE: AUDIO_METADATA
# ---------------------------------------------------------------------------
#   Embeds metadata into audio files using mutagen.
#   Supports MP3 (ID3), M4A (MP4), FLAC (Vorbis).
#
#   NOTE: mutagen is optional dependency
# ===========================================================================


def embed_audio_metadata(file_path, title=None, artist=None, album=None, thumbnail_path=None):
    """Embed metadata into audio file.

    Args:
        file_path: Path to audio file
        title: Song title
        artist: Artist name
        album: Album name
        thumbnail_path: Path to thumbnail for album art

    Returns:
        bool: True if successful

    Supported Formats:
        - .mp3 — ID3 tags
        - .m4a/.aac/.mp4 — MP4 atoms
        - .flac — Vorbis comments

    Note:
        Silently fails if mutagen not installed
    """
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
        from mutagen.mp4 import MP4, MP4Cover
        from mutagen.flac import FLAC, Picture
    except ImportError:
        logger.warning("mutagen not installed, skipping audio metadata")
        return False
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.mp3':
            return _embed_mp3(file_path, title, artist, album, thumbnail_path)
        elif ext in ('.m4a', '.aac', '.mp4'):
            return _embed_m4a(file_path, title, artist, album, thumbnail_path)
        elif ext == '.flac':
            return _embed_flac(file_path, title, artist, album, thumbnail_path)
        else:
            logger.info(f"Unsupported audio format for metadata: {ext}")
            return False
    except Exception as e:
        logger.error(f"Failed to embed metadata: {e}")
        return False


def _embed_mp3(file_path, title, artist, album, thumbnail_path):
    """Embed metadata into MP3 file.

    Args:
        file_path: Path to MP3 file
        title: Song title
        artist: Artist name
        album: Album name
        thumbnail_path: Path to thumbnail

    Returns:
        bool: True if successful

    Note:
        Uses ID3v2.3 tags
    """
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
    
    audio = MP3(file_path, ID3=ID3)
    
    if audio.tags is None:
        audio.add_tags()
    
    if title:
        audio.tags.add(TIT2(encoding=3, text=[title]))
    if artist:
        audio.tags.add(TPE1(encoding=3, text=[artist]))
    if album:
        audio.tags.add(TALB(encoding=3, text=[album]))
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        with open(thumbnail_path, 'rb') as f:
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=f.read()
            ))
    
    audio.save()
    return True


def _embed_m4a(file_path, title, artist, album, thumbnail_path):
    """Embed metadata into M4A/AAC file.

    Args:
        file_path: Path to M4A file
        title: Song title
        artist: Artist name
        album: Album name
        thumbnail_path: Path to thumbnail

    Returns:
        bool: True if successful

    Note:
        Uses iTunes-style atoms
    """
    from mutagen.mp4 import MP4, MP4Cover
    
    audio = MP4(file_path)
    
    if title:
        audio['\xa9nam'] = [title]
    if artist:
        audio['\xa9ART'] = [artist]
    if album:
        audio['\xa9alb'] = [album]
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        with open(thumbnail_path, 'rb') as f:
            audio['covr'] = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)]
    
    audio.save()
    return True


def _embed_flac(file_path, title, artist, album, thumbnail_path):
    """Embed metadata into FLAC file.

    Args:
        file_path: Path to FLAC file
        title: Song title
        artist: Artist name
        album: Album name
        thumbnail_path: Path to thumbnail

    Returns:
        bool: True if successful

    Note:
        Uses Vorbis comments
    """
    from mutagen.flac import FLAC, Picture
    
    audio = FLAC(file_path)
    
    if title:
        audio['title'] = title
    if artist:
        audio['artist'] = artist
    if album:
        audio['album'] = album
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        pic = Picture()
        pic.type = 3
        pic.mime = 'image/jpeg'
        with open(thumbnail_path, 'rb') as f:
            pic.data = f.read()
        audio.clear_pictures()
        audio.add_picture(pic)
    
    audio.save()
    return True


def extract_audio_thumbnail(audio_path, output_path=None):
    """Extract album art from audio file.

    Args:
        audio_path: Path to audio file
        output_path: Output path (optional)

    Returns:
        str: Output path or None

    Note:
        Only works with MP3 files containing APIC tags
    """
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3
        
        audio = MP3(audio_path, ID3=ID3)
        
        if audio.tags:
            for tag in audio.tags.values():
                if hasattr(tag, 'type') and tag.type == 3:  # APIC (cover)
                    if output_path is None:
                        output_path = audio_path.rsplit('.', 1)[0] + '.jpg'
                    with open(output_path, 'wb') as f:
                        f.write(tag.data)
                    return output_path
    except Exception as e:
        logger.error(f"Failed to extract thumbnail: {e}")
    
    return None

# ===========================================================================
#   END OF AUDIO_METADATA MODULE
# ===========================================================================
