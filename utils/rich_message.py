#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
    MODULE:  Rich Message Builders
    PURPOSE: Helper functions for creating Telegram Rich Messages (Bot API 10.1)
    AUTHOR:  Shinei Nouzen (Shineii86)
    LICENSE: MIT License (c) 2024-2026
============================================================================
    DESCRIPTION:
        Provides utilities for building rich messages using ftmgram's
        InputRichMessage API. Supports both HTML and Markdown formatting.

    RICH MESSAGE FORMATTING:
        - Headings: <h1> to <h6> (HTML) or # to ###### (Markdown)
        - Lists: <ul><li> (HTML) or - item (Markdown)
        - Tables: <table><tr><td> (HTML)
        - Code blocks: <pre><code> (HTML) or ``` (Markdown)
        - Blockquotes: <blockquote> (HTML) or > (Markdown)
        - Details: <details><summary> (HTML)
        - Dividers: <hr> (HTML) or --- (Markdown)

    REFERENCE:
        https://core.telegram.org/bots/api#rich-message-formatting-options
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from ftmgram.types import InputRichMessage

# ===========================================================================
#   HTML RICH MESSAGE BUILDERS
# ===========================================================================


def build_html_rich_message(
    title: str = None,
    content: str = None,
    footer: str = None,
    is_rtl: bool = False,
    skip_entity_detection: bool = False
) -> InputRichMessage:
    """Build a rich message using HTML formatting.

    Args:
        title: Optional heading text (rendered as <h2>)
        content: Main HTML content body
        footer: Optional footer text (rendered as <footer>)
        is_rtl: Right-to-left text direction
        skip_entity_detection: Skip auto-detection of URLs, mentions, etc.

    Returns:
        InputRichMessage with HTML content

    Example:
        msg = build_html_rich_message(
            title="Download Complete",
            content="<p>File <b>video.mp4</b> ready!</p>",
            footer="TelegramDL v2.0"
        )
        await client.send_rich_message(chat_id, msg)
    """
    parts = []
    if title:
        parts.append(f"<h2>{title}</h2>")
    if content:
        parts.append(content)
    if footer:
        parts.append(f"<footer>{footer}</footer>")

    html = "\n".join(parts) if parts else "<p>Empty message</p>"

    return InputRichMessage(
        html=html,
        is_rtl=is_rtl,
        skip_entity_detection=skip_entity_detection
    )


def build_progress_rich_message(
    filename: str,
    percent: float,
    speed: str = "",
    eta: str = "",
    status: str = "downloading"
) -> InputRichMessage:
    """Build a rich message showing download progress.

    Args:
        filename: Name of the file being downloaded
        percent: Progress percentage (0-100)
        speed: Download speed string (e.g., "1.5 MB/s")
        eta: Estimated time remaining (e.g., "00:32")
        status: Current status (downloading/uploading/merging)

    Returns:
        InputRichMessage with styled progress display

    Example:
        msg = build_progress_rich_message("video.mp4", 67.5, "2.1 MB/s", "00:15")
        await client.send_rich_message(chat_id, msg)
    """
    # Build progress bar
    bar_length = 20
    filled = int(bar_length * percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    html = f"""
<h3>⬇️ Downloading</h3>
<p><b>{filename}</b></p>
<pre>{bar} {percent:.1f}%</pre>
<p>⚡ Speed: <code>{speed}</code> | ⏱ ETA: <code>{eta}</code></p>
<footer>Status: {status}</footer>
"""
    return InputRichMessage(html=html.strip())


def build_complete_rich_message(
    filename: str,
    size: str,
    download_time: str = "",
    chat_id: str = ""
) -> InputRichMessage:
    """Build a rich message for completed download.

    Args:
        filename: Name of the downloaded file
        size: File size string (e.g., "1.2 GB")
        download_time: Time taken for download
        chat_id: Target chat for dump (if any)

    Returns:
        InputRichMessage with completion details
    """
    html = f"""
<h2>✅ Download Complete</h2>
<p><b>{filename}</b></p>
<table>
<tr><td>📦 Size</td><td><code>{size}</code></td></tr>
{"<tr><td>⏱ Time</td><td><code>" + download_time + "</code></td></tr>" if download_time else ""}
{"<tr><td>📢 Dump</td><td><code>" + chat_id + "</code></td></tr>" if chat_id else ""}
</table>
<footer>TelegramDL v2.0</footer>
"""
    return InputRichMessage(html=html.strip())


def build_error_rich_message(
    error_type: str,
    message: str,
    suggestion: str = ""
) -> InputRichMessage:
    """Build a rich message for errors.

    Args:
        error_type: Type of error (e.g., "Download Failed")
        message: Error message details
        suggestion: Optional suggestion to fix the issue

    Returns:
        InputRichMessage with error details
    """
    html = f"""
<h3>❌ {error_type}</h3>
<blockquote>{message}</blockquote>
{"<p>💡 <b>Suggestion:</b> " + suggestion + "</p>" if suggestion else ""}
<footer>Need help? Use /help</footer>
"""
    return InputRichMessage(html=html.strip())


def build_help_rich_message() -> InputRichMessage:
    """Build a rich help message with command reference.

    Returns:
        InputRichMessage with formatted help text
    """
    html = """
<h2>📖 TelegramDL Help</h2>

<h3>📥 Download Commands</h3>
<ul>
<li><code>/dl &lt;link&gt;</code> — Download from URL</li>
<li><code>/adl &lt;link&gt;</code> — Download audio only</li>
<li><code>/backup</code> — Backup your settings</li>
</ul>

<h3>👤 User Commands</h3>
<ul>
<li><code>/login</code> — Login for restricted content</li>
<li><code>/settings</code> — View your settings</li>
<li><code>/myplan</code> — View your subscription plan</li>
</ul>

<h3>🔧 Admin Commands</h3>
<ul>
<li><code>/broadcast</code> — Broadcast message to all users</li>
<li><code>/ban /unban</code> — Ban/unban users</li>
<li><code>/welcome</code> — Set welcome message</li>
</ul>

<h3>ℹ️ Info Commands</h3>
<ul>
<li><code>/ping</code> — Check bot latency</li>
<li><code>/info</code> — Bot information</li>
<li><code>/about</code> — About the bot</li>
</ul>

<footer>Supported: YouTube, Instagram, TikTok, Facebook + 100 sites via yt-dlp</footer>
"""
    return InputRichMessage(html=html.strip())


def build_about_rich_message() -> InputRichMessage:
    """Build a rich about message with bot information.

    Returns:
        InputRichMessage with bot details
    """
    html = """
<h2>🤖 About TelegramDL</h2>

<table>
<tr><td><b>Version</b></td><td><code>2.0.0</code></td></tr>
<tr><td><b>Developer</b></td><td>Shinei Nouzen</td></tr>
<tr><td><b>License</b></td><td>MIT License</td></tr>
<tr><td><b>Framework</b></td><td>ftmgram (Bot API 10.1)</td></tr>
</table>

<h3>✨ Features</h3>
<ul>
<li>📥 Download from 100+ sites</li>
<li>🔐 Restricted content support</li>
<li>💎 Premium subscription system</li>
<li>🎨 Custom thumbnails & captions</li>
<li>📊 Rich progress tracking</li>
<li>🤖 Custom bot per user</li>
</ul>

<blockquote>Built with ❤️ by <a href="https://github.com/Shineii86">Shineii86</a></blockquote>
"""
    return InputRichMessage(html=html.strip())


# ===========================================================================
#   MARKDOWN RICH MESSAGE BUILDERS
# ===========================================================================


def build_markdown_rich_message(
    title: str = None,
    content: str = None,
    footer: str = None,
    is_rtl: bool = False,
    skip_entity_detection: bool = False
) -> InputRichMessage:
    """Build a rich message using Markdown formatting.

    Args:
        title: Optional heading text (rendered as ## heading)
        content: Main Markdown content body
        footer: Optional footer text
        is_rtl: Right-to-left text direction
        skip_entity_detection: Skip auto-detection of URLs, mentions, etc.

    Returns:
        InputRichMessage with Markdown content

    Example:
        msg = build_markdown_rich_message(
            title="Download Complete",
            content="File **video.mp4** ready!",
            footer="TelegramDL v2.0"
        )
        await client.send_rich_message(chat_id, msg)
    """
    parts = []
    if title:
        parts.append(f"## {title}")
    if content:
        parts.append(content)
    if footer:
        parts.append(f"---\n*{footer}*")

    markdown = "\n\n".join(parts) if parts else "*Empty message*"

    return InputRichMessage(
        markdown=markdown,
        is_rtl=is_rtl,
        skip_entity_detection=skip_entity_detection
    )


# ===========================================================================
#   CONVENIENCE FUNCTIONS
# ===========================================================================


async def send_rich_message(client, chat_id: int, rich_message: InputRichMessage, **kwargs):
    """Send a rich message with fallback to MarkdownV2.

    Args:
        client: ftmgram Client instance
        chat_id: Target chat ID
        rich_message: InputRichMessage to send
        **kwargs: Additional arguments for send_rich_message

    Returns:
        Message object

    Fallback:
        If send_rich_message fails, falls back to send_message with MarkdownV2
    """
    try:
        return await client.send_rich_message(chat_id, rich_message, **kwargs)
    except Exception:
        # Fallback to regular message
        text = rich_message.html or rich_message.markdown or "Empty message"
        return await client.send_message(chat_id, text, **kwargs)


async def send_progress_update(
    client,
    chat_id: int,
    message_id: int,
    filename: str,
    percent: float,
    speed: str = "",
    eta: str = ""
):
    """Send a progress update as a rich message edit.

    Args:
        client: ftmgram Client instance
        chat_id: Target chat ID
        message_id: Message to edit
        filename: File being downloaded
        percent: Progress percentage (0-100)
        speed: Download speed
        eta: Estimated time remaining
    """
    rich_msg = build_progress_rich_message(filename, percent, speed, eta)
    try:
        await client.edit_message_text(
            chat_id,
            message_id,
            rich_message=rich_msg
        )
    except Exception:
        # Fallback to plain text
        bar_length = 20
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        text = f"**{filename}**\n`{bar}` {percent:.1f}%\n⚡ {speed} | ⏱ {eta}"
        await client.edit_message_text(chat_id, message_id, text)


# ===========================================================================
#   MODULE EXPORTS
# ===========================================================================

__all__ = [
    # HTML builders
    "build_html_rich_message",
    "build_progress_rich_message",
    "build_complete_rich_message",
    "build_error_rich_message",
    "build_help_rich_message",
    "build_about_rich_message",
    # Markdown builders
    "build_markdown_rich_message",
    # Convenience functions
    "send_rich_message",
    "send_progress_update",
]

# ===========================================================================
#   END OF RICH MESSAGE BUILDERS
# ===========================================================================
