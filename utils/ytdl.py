import os
import re
import asyncio
import logging
import tempfile

logger = logging.getLogger(__name__)

# Supported URL patterns
YT_DLP_PATTERNS = [
    r'youtube\.com',
    r'youtu\.be',
    r'instagram\.com',
    r'facebook\.com',
    r'fb\.watch',
    r'tiktok\.com',
    r'twitter\.com',
    r'x\.com',
    r'vimeo\.com',
    r'dailymotion\.com',
    r'reddit\.com',
    r'soundcloud\.com',
    r'twitch\.tv',
    r'streamable\.com',
    r'vine\.co',
    r'v\.kuaishou\.com',
    r'douyin\.com',
    r'bilibili\.com',
    r'nicovideo\.jp',
    r'v.qq.com',
    r'hotstar\.com',
    r'jioSaavn\.com',
    r'spotify\.com',
    r'scn\.link',
    r'youtube\.com/shorts',
]


def is_ytdl_url(url):
    """Check if URL is supported by yt-dlp."""
    for pattern in YT_DLP_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False


async def download_with_ytdl(url, output_dir, audio_only=False, progress_callback=None):
    """Download media using yt-dlp.
    
    Args:
        url: URL to download
        output_dir: Directory to save files
        audio_only: If True, extract audio only
        progress_callback: Optional callback for progress
    
    Returns:
        List of downloaded file paths
    """
    try:
        import yt_dlp
    except ImportError:
        logger.error("yt-dlp not installed")
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'no_warnings': True,
        'quiet': True,
    }
    
    if audio_only:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'best[ext<=mp4]/best',
        })
    
    # Add cookies if available
    cookie_file = os.environ.get('COOKIES_FILE')
    if cookie_file and os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file
    
    downloaded_files = []
    
    def progress_hook(d):
        if d['status'] == 'finished':
            filename = d.get('filename', '')
            if filename and os.path.exists(filename):
                downloaded_files.append(filename)
                logger.info(f"Downloaded: {filename}")
    
    ydl_opts['progress_hooks'] = [progress_hook]
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        logger.error(f"yt-dlp download failed: {e}")
        return []
    
    return downloaded_files


async def get_video_info(url):
    """Get video metadata without downloading."""
    try:
        import yt_dlp
    except ImportError:
        return None
    
    ydl_opts = {
        'noplaylist': True,
        'no_warnings': True,
        'quiet': True,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail', ''),
                'filesize': info.get('filesize', 0) or info.get('filesize_approx', 0),
            }
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        return None
