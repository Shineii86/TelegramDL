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

import os
import logging

logger = logging.getLogger(__name__)


def embed_audio_metadata(file_path, title=None, artist=None, album=None, thumbnail_path=None):
    """Embed metadata into audio file (MP3, M4A, etc.).
    
    Args:
        file_path: Path to audio file
        title: Song title
        artist: Artist name
        album: Album name
        thumbnail_path: Path to thumbnail image for album art
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
    """Embed metadata into MP3 file."""
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
    """Embed metadata into M4A/AAC file."""
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
    """Embed metadata into FLAC file."""
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
    """Extract album art from audio file."""
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
