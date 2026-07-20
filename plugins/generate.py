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
        Core download logic. Handles single messages, batch downloads,
        story downloads, link parsing, and content delivery.

    LINK FORMATS:
        t.me/username/1001-1010     — Batch range
        t.me/username/123           — Single message
        t.me/username/s/123         — Story
        t.me/c/1234567890/123       — Private channel
        t.me/b/botusername/123      — Bot chat
        t.me/+invitehash            — Invite link
        -1001234567890/123          — Numeric ID

    FEATURES:
        FEATURE: LINK_PARSER
        FEATURE: AUTH_CLIENT
        FEATURE: AUTO_JOIN
        FEATURE: DOWNLOAD_RETRY
        FEATURE: FORWARD_MODE
        FEATURE: SEND_WITH_METADATA
        FEATURE: BATCH_DOWNLOAD
        FEATURE: STORY_DOWNLOAD
        FEATURE: DAILY_LIMITS
        FEATURE: FILE_SIZE_CHECK

    LOGGING:
        Uses plugins.logger for download event logging
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import os
import re
import asyncio
import logging
from ftmgram import filters
from ftmgram.types import Message, CallbackQuery
from ftmgram.enums import MessageMediaType
from ftmgram.errors import (
    FloodWait, UserNotParticipant, ChannelPrivate,
    UsernameNotOccupied, UsernameInvalid, PeerIdInvalid
)

from bot import bot, user_client, start_user_client
from database.db import db
from utils.progress import DownloadProgress
from utils.ui import stop_keyboard, main_menu_keyboard
from config import (
    API_ID, API_HASH, LOGIN_SYSTEM, OUTPUT_DIR,
    WAITING_TIME, ERROR_MESSAGE, CHANNEL_ID, MAX_FILE_SIZE_MB,
    KEEP_ORIGINAL_CAPTION, FREE_MAX_FILE_SIZE_MB, PREMIUM_MAX_FILE_SIZE_MB,
    FREE_DAILY_LIMIT
)

logger = logging.getLogger(__name__)

# ===========================================================================
#   GLOBAL STATE
# ---------------------------------------------------------------------------
#   IS_BATCH:     Dict tracking batch cancel flags per user
#   USER_PROGRESS: Dict tracking progress trackers per user
#
#   NOTE: These are in-memory only, reset on bot restart
# ===========================================================================

IS_BATCH = {}
USER_PROGRESS = {}

# ===========================================================================
#   FEATURE: MEDIA_TYPE_HELPERS
# ---------------------------------------------------------------------------
#   Helper functions for media type detection and folder organization
# ===========================================================================


def get_message_type(msg):
    """Determine the type of media in a message.

    Args:
        msg: Telegram message object

    Returns:
        str: Media type (photo, video, document, audio, voice,
             animation, sticker, text) or None

    Note:
        Used for routing files to correct folders and
        determining file extensions
    """
    if msg.media:
        if msg.media == MessageMediaType.PHOTO:
            return "photo"
        elif msg.media == MessageMediaType.VIDEO:
            return "video"
        elif msg.media == MessageMediaType.DOCUMENT:
            return "document"
        elif msg.media == MessageMediaType.AUDIO:
            return "audio"
        elif msg.media == MessageMediaType.VOICE:
            return "voice"
        elif msg.media == MessageMediaType.ANIMATION:
            return "animation"
        elif msg.media == MessageMediaType.STICKER:
            return "sticker"
    elif msg.text:
        return "text"
    return None


def get_folder(msg_type):
    """Get folder name for media type.

    Args:
        msg_type: Media type string

    Returns:
        str: Folder name (Photos, Videos, Audios, etc.)

    Example:
        get_folder("video") → "Videos"
    """
    folders = {
        "photo": "Photos", "video": "Videos", "audio": "Audios",
        "voice": "Voice", "animation": "GIFs", "sticker": "Stickers",
        "document": "Documents",
    }
    return folders.get(msg_type, "Other")


def get_ext(msg_type):
    """Get file extension for media type.

    Args:
        msg_type: Media type string

    Returns:
        str: File extension (jpg, mp4, mp3, etc.)

    Example:
        get_ext("video") → "mp4"
    """
    exts = {
        "photo": "jpg", "video": "mp4", "audio": "mp3",
        "voice": "ogg", "animation": "mp4", "document": "",
    }
    return exts.get(msg_type, "")


def make_caption(msg, folder):
    """Generate default caption for a message.

    Args:
        msg: Telegram message object
        folder: Folder name (Photos, Videos, etc.)

    Returns:
        str: Formatted caption "Folder | YYYY-MM-DD | #msg_id"

    Example:
        make_caption(msg, "Videos") → "Videos | 2024-01-15 | #123"
    """
    date_str = msg.date.strftime("%Y-%m-%d") if msg.date else "unknown"
    return f"{folder} | {date_str} | #{msg.id}"

# ===========================================================================
#   FEATURE: LINK_PARSER
# ---------------------------------------------------------------------------
#   Parses ALL Telegram link types into structured data.
#   Returns tuple of (chat_username, msg_start, msg_end)
#
#   TIP: This is the most complex parser in the codebase.
#        Handles 10+ different link formats.
# ===========================================================================


def parse_channel_username(link):
    """Parse ALL Telegram link types to extract chat and message IDs.

    Args:
        link: Telegram link, username, or numeric ID

    Returns:
        tuple: (chat_username, msg_start, msg_end)
               - chat_username: str or int (chat identifier)
               - msg_start: int or None (first message ID)
               - msg_end: int or None (last message ID)

    Supported Formats:
        t.me/username/1001-1010     → batch range
        t.me/username/123           → single message
        t.me/username/s/123         → story
        t.me/c/1234567890/123       → private channel msg
        t.me/c/1234567890           → private channel (no msg)
        t.me/b/botusername/123      → bot chat msg
        t.me/b/botusername          → bot chat (no msg)
        t.me/+invitehash            → invite link
        t.me/joinchat/invitehash    → invite link (old)
        t.me/username               → channel/group (no msg)
        username                    → plain username
        -1001234567890              → numeric chat ID
        -1001234567890/123          → numeric chat ID + msg

    Note:
        Returns (link, None, None) as fallback for unrecognized formats
    """
    link = link.strip()

    # 1. Batch: t.me/username/1001-1010
    batch_match = re.search(r't\.me/([^/]+)/(\d+)-(\d+)', link)
    if batch_match:
        return batch_match.group(1), int(batch_match.group(2)), int(batch_match.group(3))

    # 2. Story: t.me/username/s/123
    story_match = re.search(r't\.me/([^/]+)/s/(\d+)', link)
    if story_match:
        return story_match.group(1), int(story_match.group(2)), int(story_match.group(2))

    # 3. Private channel: t.me/c/1234567890/123 or t.me/c/1234567890
    private_match = re.search(r't\.me/c/(\d+)(?:/(\d+))?', link)
    if private_match:
        chat_id = f"-100{private_match.group(1)}"
        msg_id = int(private_match.group(2)) if private_match.group(2) else None
        return chat_id, msg_id, msg_id

    # 4. Bot chat: t.me/b/botusername/123 or t.me/b/botusername
    bot_match = re.search(r't\.me/b/([^/]+)(?:/(\d+))?', link)
    if bot_match:
        bot_username = bot_match.group(1)
        msg_id = int(bot_match.group(2)) if bot_match.group(2) else None
        return bot_username, msg_id, msg_id

    # 5. Invite link: t.me/+hash or t.me/joinchat/hash
    invite_match = re.search(r't\.me/(?:\+|joinchat/)([^/]+)', link)
    if invite_match:
        return invite_match.group(1), None, None

    # 6. Username with message: t.me/username/123
    single_match = re.search(r't\.me/([^/]+)/(\d+)', link)
    if single_match:
        return single_match.group(1), int(single_match.group(2)), int(single_match.group(2))

    # 7. Username only: t.me/username
    username_match = re.search(r't\.me/([^/]+)', link)
    if username_match:
        return username_match.group(1), None, None

    # 8. Numeric ID: -1001234567890 or -1001234567890/123
    numeric_match = re.search(r'^(-?\d+)(?:/(\d+))?$', link)
    if numeric_match:
        chat_id = numeric_match.group(1)
        msg_id = int(numeric_match.group(2)) if numeric_match.group(2) else None
        return chat_id, msg_id, msg_id

    # 8. Plain username (no t.me prefix)
    if re.match(r'^[a-zA-Z0-9_]+$', link):
        return link, None, None

    # 9. Fallback - return as-is
    return link, None, None

# ===========================================================================
#   FEATURE: AUTH_CLIENT
# ---------------------------------------------------------------------------
#   Returns appropriate client for user based on authentication:
#   1. Custom bot (if user set one)
#   2. User session (if LOGIN_SYSTEM=true)
#   3. Global user client (if LOGIN_SYSTEM=false)
#
#   TIP: Custom bots prevent bans on main bot token
# ===========================================================================


async def get_auth_client(user_id):
    """Get authenticated client for user.

    Args:
        user_id: Telegram user ID

    Returns:
        Client: Authenticated Pyrogram client or None

    Priority:
        1. Custom bot (user's own bot token)
        2. User session (per-user login)
        3. Global user client (shared session)

    Note:
        Returns None if no authentication available
    """
    # First try custom bot
    from plugins.custom_bot import get_user_bot
    custom_bot = await get_user_bot(user_id)
    if custom_bot:
        return custom_bot

    # Then try user session
    if LOGIN_SYSTEM:
        session = await db.get_session(user_id)
        if session:
            from ftmgram import Client
            client = Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=session)
            await client.start()
            return client
        return None
    else:
        await start_user_client()
        return user_client

# ===========================================================================
#   FEATURE: AUTO_JOIN
# ---------------------------------------------------------------------------
#   Automatically joins a channel when bot can't access it.
#   Used as fallback before returning access errors.
# ===========================================================================


async def auto_join_channel(client, channel):
    """Try to join a channel if access denied.

    Args:
        client: Authenticated Pyrogram client
        channel: Channel username or invite link

    Returns:
        bool: True if joined successfully, False otherwise

    Note:
        Silently fails on any error (join may not be possible)
    """
    try:
        await client.join_chat(channel)
        return True
    except:
        return False

# ===========================================================================
#   FEATURE: DOWNLOAD_RETRY
# ---------------------------------------------------------------------------
#   Downloads file with automatic retry on FloodWait.
#   Retries up to 3 times with exponential backoff.
#
#   NOTE: FloodWait is Telegram's rate limit signal
# ===========================================================================


async def download_with_retry(client, msg, dest):
    """Download file with retry logic.

    Args:
        client: Pyrogram client
        msg: Message to download
        dest: Destination file path

    Returns:
        bool: True if download succeeded, False otherwise

    Retry Logic:
        - Up to 3 attempts
        - FloodWait: Wait required time + 5s buffer
        - Other errors: Wait 5s between retries
    """
    for attempt in range(3):
        try:
            await client.download_media(msg, file_name=dest)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except Exception as e:
            logger.error(f"Download failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)
    return False

# ===========================================================================
#   FEATURE: FORWARD_MODE
# ---------------------------------------------------------------------------
#   Forwards messages directly (fastest method).
#   No download/upload required, uses Telegram's internal transfer.
#
#   TIP: Always prefer forward mode when possible
# ===========================================================================


async def forward_single(client, dest_chat, msg):
    """Forward a single message (fastest method).

    Args:
        client: Pyrogram client
        dest_chat: Destination chat ID
        msg: Message to forward

    Returns:
        bool: True if forwarded successfully, False otherwise

    Note:
        Forwarding is faster than download+upload because
        Telegram handles the transfer internally
    """
    for attempt in range(3):
        try:
            await client.forward_messages(dest_chat, msg.chat.id, msg.id)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except Exception:
            return False
    return False

# ===========================================================================
#   FEATURE: SEND_WITH_METADATA
# ---------------------------------------------------------------------------
#   Sends file with all metadata preserved:
#   - Thumbnail (custom or original)
#   - Duration (for video/audio)
#   - Dimensions (for video)
#   - Caption entities (formatting)
#   - Custom caption templates
#
#   FEATURE: CUSTOM_THUMBNAIL
#   FEATURE: CUSTOM_CAPTION
# ===========================================================================


async def send_with_metadata(client, chat_id, file_path, caption, msg, caption_entities=None, user_id=None):
    """Send file with metadata: thumbnail, duration, dimensions, caption.

    Args:
        client: Pyrogram client
        chat_id: Destination chat ID
        file_path: Path to file
        caption: Message caption
        msg: Original message (for metadata)
        caption_entities: Original formatting entities
        user_id: User ID for custom settings

    Returns:
        bool: True if sent successfully, False otherwise

    Features:
        - Custom thumbnail from database
        - Custom caption with placeholders
        - Auto-detect file type for correct send method
        - Preserves video duration/dimensions
        - Retries up to 3 times on FloodWait

    Placeholders:
        {filename} — Original filename
        {size}     — File size (human readable)
        {date}     — Upload date (YYYY-MM-DD)
    """
    # Get custom thumbnail and caption from DB
    custom_thumb = None
    custom_caption = None
    if user_id:
        custom_thumb = await db.get_thumbnail(user_id)
        custom_caption = await db.get_caption(user_id)

    for attempt in range(3):
        try:
            # Use custom thumbnail or original
            thumb = custom_thumb
            if not thumb:
                try:
                    if msg.media == MessageMediaType.VIDEO and msg.video.thumbs:
                        thumb = await client.download_media(msg.video.thumbs[0].file_id)
                    elif msg.media == MessageMediaType.DOCUMENT and msg.document.thumbs:
                        thumb = await client.download_media(msg.document.thumbs[0].file_id)
                    elif msg.media == MessageMediaType.AUDIO and msg.audio.thumbs:
                        thumb = await client.download_media(msg.audio.thumbs[0].file_id)
                except:
                    thumb = None

            # Apply custom caption if set
            if custom_caption:
                import os as _os
                from datetime import datetime as _dt
                file_name = _os.path.basename(file_path)
                file_size = _os.path.getsize(file_path)
                size_str = f"{file_size / 1024 / 1024:.1f}MB" if file_size > 1024*1024 else f"{file_size / 1024:.1f}KB"
                date_str = _dt.now().strftime("%Y-%m-%d")
                caption = custom_caption.format(
                    filename=file_name,
                    size=size_str,
                    date=date_str
                )

            if file_path.endswith((".jpg", ".jpeg", ".png", ".webp")):
                await client.send_photo(
                    chat_id, file_path,
                    caption=caption,
                    caption_entities=caption_entities
                )
            elif file_path.endswith((".mp4", ".mkv", ".avi")):
                duration = 0
                width = 0
                height = 0
                if msg.media == MessageMediaType.VIDEO:
                    vid = getattr(msg, "video", None)
                    if vid:
                        duration = getattr(vid, "duration", 0) or 0
                        width = getattr(vid, "width", 0) or 0
                        height = getattr(vid, "height", 0) or 0
                await client.send_video(
                    chat_id, file_path,
                    caption=caption,
                    caption_entities=caption_entities,
                    duration=duration,
                    width=width,
                    height=height,
                    thumb=thumb
                )
            elif file_path.endswith((".mp3", ".ogg", ".wav")):
                duration = 0
                if msg.media == MessageMediaType.AUDIO:
                    aud = getattr(msg, "audio", None)
                    if aud:
                        duration = getattr(aud, "duration", 0) or 0
                await client.send_audio(
                    chat_id, file_path,
                    caption=caption,
                    caption_entities=caption_entities,
                    duration=duration,
                    thumb=thumb
                )
            elif file_path.endswith((".gif",)):
                await client.send_animation(
                    chat_id, file_path,
                    caption=caption,
                    caption_entities=caption_entities
                )
            else:
                await client.send_document(
                    chat_id, file_path,
                    caption=caption,
                    caption_entities=caption_entities,
                    thumb=thumb
                )

            # Cleanup thumbnail (only if not custom)
            if thumb and not custom_thumb and isinstance(thumb, str) and os.path.exists(thumb):
                try:
                    os.remove(thumb)
                except:
                    pass

            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except Exception as e:
            logger.error(f"Send failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)

    return False

# ===========================================================================
#   FEATURE: HANDLE_SINGLE
# ---------------------------------------------------------------------------
#   Processes a single message download:
#   1. Check file size limits
#   2. Try forward mode (fastest)
#   3. Fallback to download+upload
#   4. Apply custom settings
#   5. Forward to dump chat if set
#   6. Cleanup local file
#
#   FEATURE: FILE_SIZE_CHECK
#   FEATURE: DUMP_CHAT
# ===========================================================================


async def handle_single(client, acc, message, chat_id, msg_id, forward=False, progress=None):
    """Handle download of a single message.

    Args:
        client: Bot client (for sending to user)
        acc: Auth client (for accessing source)
        message: User's original message
        chat_id: Source chat ID
        msg_id: Message ID to download
        forward: Use forward mode (faster)
        progress: Progress tracker (optional)

    Returns:
        None

    Process:
        1. Convert chat_id to int if numeric
        2. Get message from source
        3. Check file size against user's limit
        4. Try forward mode if enabled
        5. Download and upload with metadata
        6. Increment daily usage
        7. Forward to dump chat if set
        8. Cleanup local file

    Errors:
        - FloodWait: Waits required time
        - UserNotParticipant: Shows access denied
        - ChannelPrivate: Shows access denied
    """
    try:
        if isinstance(chat_id, str) and (chat_id.isdigit() or chat_id.startswith("-100")):
            chat_id = int(chat_id)

        msg = await acc.get_messages(chat_id, msg_id)
        if not msg or msg.empty:
            return

        msg_type = get_message_type(msg)
        if not msg_type or msg_type == "text":
            if msg.text:
                await client.send_message(message.chat.id, msg.text)
            return

        # Check file size based on premium status
        user_id = message.from_user.id
        is_user_premium = await db.is_premium(user_id)
        max_size = PREMIUM_MAX_FILE_SIZE_MB if is_user_premium else FREE_MAX_FILE_SIZE_MB

        media_obj = getattr(msg, msg.media.value, None) if msg.media else None
        if media_obj and hasattr(media_obj, 'file_size'):
            if media_obj.file_size > max_size * 1024 * 1024:
                await client.send_message(
                    message.chat.id,
                    f"Skipped #{msg_id}: too large ({media_obj.file_size / 1024 / 1024:.1f}MB)\n"
                    f"Limit: {max_size}MB ({'Premium' if is_user_premium else 'Free'})"
                )
                return

        # File preview
        if media_obj and hasattr(media_obj, 'file_size'):
            size_mb = media_obj.file_size / 1024 / 1024
            if progress:
                progress.update(current_file=f"#{msg_id} ({msg_type}, {size_mb:.1f}MB)")

        # Forward mode (fastest)
        if forward:
            forwarded = await forward_single(client, message.chat.id, msg)
            if forwarded:
                await db.increment_daily_usage(user_id)
                # Dump chat forwarding
                dump_chat = await db.get_dump_chat(user_id)
                if dump_chat:
                    try:
                        await client.forward_messages(dump_chat, msg.chat.id, msg.id)
                    except:
                        pass
                return

        # Download + upload fallback
        folder = get_folder(msg_type)
        ext = get_ext(msg_type)
        file_name = f"{msg_id}.{ext}" if ext else str(msg_id)
        file_path = os.path.join(OUTPUT_DIR, folder, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        success = await download_with_retry(acc, msg, file_path)
        if not success:
            await client.send_message(message.chat.id, f"Failed to download #{msg_id}")
            return

        caption = msg.caption if (KEEP_ORIGINAL_CAPTION and msg.caption) else make_caption(msg, folder)
        caption_entities = msg.caption_entities if msg.caption_entities else None
        sent = await send_with_metadata(client, message.chat.id, file_path, caption, msg, caption_entities, user_id=user_id)

        # Increment daily usage
        if sent:
            await db.increment_daily_usage(user_id)

        # Dump chat forwarding
        if sent:
            dump_chat = await db.get_dump_chat(user_id)
            if dump_chat:
                try:
                    await send_with_metadata(client, dump_chat, file_path, caption, msg, caption_entities, user_id=user_id)
                except:
                    pass

        try:
            os.remove(file_path)
        except:
            pass

        if not sent:
            await client.send_message(message.chat.id, f"Failed to send #{msg_id}")

    except FloodWait as e:
        await asyncio.sleep(e.value + 5)
    except (UserNotParticipant, ChannelPrivate) as e:
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Access denied: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Error: {str(e)}")

# ===========================================================================
#   FEATURE: CANCEL_CALLBACK
# ---------------------------------------------------------------------------
#   Callback handler for cancel_download button
# ===========================================================================


@bot.on_callback_query(filters.regex("^cancel_download$"))
async def cancel_callback(client, callback: CallbackQuery):
    """Handle cancel download callback.

    Args:
        client: Bot client
        callback: Callback query object

    Returns:
        None

    Note:
        Sets IS_BATCH flag to True to stop batch processing
    """
    user_id = callback.from_user.id
    IS_BATCH[user_id] = True
    await callback.answer("Download cancelled!")
    await callback.message.edit_text(
        "**❌ Download Cancelled**\n\nProcess stopped by user.",
        reply_markup=main_menu_keyboard()
    )

# ===========================================================================
#   FEATURE: BATCH_DOWNLOAD
# ---------------------------------------------------------------------------
#   /batch <channel_url> — Download all media from channel
#   Processes message ID ranges with progress tracking
#
#   FEATURE: PROGRESS_BAR
#   FEATURE: CANCEL_SUPPORT
# ===========================================================================


@bot.on_message(filters.command("batch") & filters.private)
async def batch_cmd(client, message: Message):
    """Handle /batch command for batch downloads.

    Args:
        client: Bot client
        message: User message with channel URL

    Returns:
        None

    Usage:
        /batch https://t.me/username/1001-1010

    Process:
        1. Parse channel URL and message range
        2. Get authenticated client
        3. Create progress tracker
        4. Process each message with delay
        5. Show completion stats

    Note:
        Supports cancel via /cancel command or Stop button
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**Usage:** `/batch <channel_url>`\n\n"
            "Downloads all media from a channel."
        )
        return

    user_id = message.from_user.id
    channel_url = args[1].strip()
    chat_username, msg_start, msg_end = parse_channel_username(channel_url)

    if msg_start is None:
        await message.reply("Please provide a valid channel URL with message IDs.")
        return

    acc = await get_auth_client(user_id)
    if not acc:
        await message.reply("No user session. Use /login first.")
        return

    total = msg_end - msg_start + 1
    await message.reply(
        f"**📦 Batch Download**\n\n"
        f"**Channel:** `{chat_username}`\n"
        f"**Range:** {msg_start} → {msg_end}\n"
        f"**Total:** {total} files\n\n"
        f"Starting...",
        reply_markup=stop_keyboard()
    )

    IS_BATCH[user_id] = False

    # Create progress tracker
    progress = DownloadProgress(client, message.chat.id)
    await progress.create(total)
    USER_PROGRESS[user_id] = progress

    count = 0
    for msg_id in range(msg_start, msg_end + 1):
        if IS_BATCH.get(user_id):
            await progress.finish()
            await message.reply("**⏹ Batch Cancelled**\nProcess stopped by user.", reply_markup=main_menu_keyboard())
            break

        await handle_single(client, acc, message, chat_username, msg_id, forward=True, progress=progress)

        count += 1
        done = progress.downloaded + progress.skipped + progress.failed + count
        progress.update(downloaded=count)
        await progress.update_message()

        await asyncio.sleep(WAITING_TIME)

    if not IS_BATCH.get(user_id):
        progress.update(downloaded=count)
        await progress.finish()

    USER_PROGRESS.pop(user_id, None)

    if LOGIN_SYSTEM and acc != user_client:
        try:
            await acc.stop()
        except:
            pass

# ===========================================================================
#   FEATURE: TEXT_MESSAGE_HANDLER
# ---------------------------------------------------------------------------
#   Handles all text messages that look like Telegram links.
#   Auto-detects link type and routes to appropriate handler.
#
#   FEATURE: STORY_DOWNLOAD
#   FEATURE: CHANNEL_INFO
#   FEATURE: SINGLE_DOWNLOAD
#   FEATURE: DAILY_LIMITS
#   FEATURE: BAN_CHECK
# ===========================================================================


@bot.on_message(filters.text & filters.private, group=2)
async def save(client, message: Message):
    """Handle text messages that look like Telegram links.

    Args:
        client: Bot client
        message: User text message

    Returns:
        None

    Process:
        1. Check if message looks like a link
        2. Check if user is banned
        3. Check daily limit
        4. Parse link type
        5. Route to appropriate handler:
           - Story → story download
           - No msg ID → channel info
           - Has msg ID → single/batch download

    Link Detection:
        - Contains "t.me"
        - Starts with "http"
        - Matches numeric ID pattern (-100...)
    """
    text = message.text.strip()
    user_id = message.from_user.id

    # Check if it looks like a Telegram link, username, or numeric ID
    is_link = (
        "t.me" in text or
        text.startswith("http") or
        re.match(r'^-100\d{6,}$', text) or
        re.match(r'^-100\d{6,}/\d+$', text)
    )

    if not is_link:
        return

    # Check if user is banned
    if await db.is_banned(user_id):
        await message.reply("**❌ You are banned** from using this bot.")
        return

    # Check daily limit
    if not await db.check_daily_limit(user_id):
        is_premium = await db.is_premium(user_id)
        if not is_premium:
            await message.reply(
                f"**📊 Daily Limit Reached**\n\n"
                f"You've used all {FREE_DAILY_LIMIT} free downloads today.\n"
                f"Wait 24 hours or ask admin for premium.",
                reply_markup=main_menu_keyboard()
            )
            return

    # Clear any stale batch cancel flag
    IS_BATCH.pop(user_id, None)

    chat_username, msg_start, msg_end = parse_channel_username(text)

    # Detect story links
    is_story = '/s/' in text and 't.me/' in text

    if is_story:
        story_id = msg_start
        await message.reply(
            f"**📖 Story Detected**\n\n"
            f"**Target:** `{chat_username}`\n"
            f"**Story ID:** {story_id}\n\n"
            f"Attempting to download..."
        )
        try:
            acc = await get_auth_client(user_id)
            if acc:
                try:
                    # Use Kurigram's get_stories API
                    story = await acc.get_stories(chat_username, story_id)
                    if story:
                        # Download story media
                        os.makedirs(OUTPUT_DIR, exist_ok=True)
                        ext = "jpg" if hasattr(story, 'photo') and story.photo else "mp4"
                        file_path = os.path.join(OUTPUT_DIR, f"story_{story_id}.{ext}")
                        
                        if hasattr(story, 'download'):
                            await story.download(file_name=file_path)
                        else:
                            await acc.download_media(story, file_name=file_path)
                        
                        # Send to user
                        caption = f"📖 Story #{story_id} from @{chat_username}"
                        if hasattr(story, 'caption') and story.caption:
                            caption = story.caption
                        
                        if ext == "jpg":
                            await client.send_photo(message.chat.id, file_path, caption=caption)
                        else:
                            await client.send_video(message.chat.id, file_path, caption=caption)
                        
                        try:
                            os.remove(file_path)
                        except:
                            pass
                    else:
                        await message.reply(
                            "**❌ Story Not Found**\n\n"
                            "This story may not exist or is no longer available.\n"
                            "Stories expire after 24 hours.",
                            reply_markup=main_menu_keyboard()
                        )
                except Exception as e:
                    await message.reply(
                        f"**❌ Story Error**\n\n"
                        f"**Error:** {e}\n\n"
                        "Stories require user authentication.\n"
                        "Make sure you're following this user.",
                        reply_markup=main_menu_keyboard()
                    )
                finally:
                    if LOGIN_SYSTEM and acc != user_client:
                        try:
                            await acc.stop()
                        except:
                            pass
            else:
                await message.reply(
                    "**🔐 Login Required**\n\n"
                    "Stories require user authentication.\n"
                    "Use /login to authenticate.",
                    reply_markup=main_menu_keyboard()
                )
        except Exception as e:
            await message.reply(f"**Error:** {e}")
        return

    # If no message ID → show channel info
    if msg_start is None:
        await message.reply(
            f"**📍 Chat Detected**\n\n"
            f"**Target:** `{chat_username}`\n\n"
            f"Attempting to resolve..."
        )
        try:
            acc = await get_auth_client(user_id)
            if acc:
                try:
                    chat = await acc.get_chat(chat_username)
                    chat_type = "Channel" if chat.type.name == "CHANNEL" else "Group" if chat.type.name in ("GROUP", "SUPERGROUP") else "User"
                    member_count = getattr(chat, 'members_count', 'N/A')
                    title = getattr(chat, 'title', chat_username)

                    info = (
                        f"**{chat_type}:** {title}\n"
                        f"**Username:** @{chat_username}\n"
                        f"**Members:** {member_count}\n"
                        f"**ID:** `{chat.id}`\n\n"
                        f"Send a message link to download content.\n"
                        f"Example: `https://t.me/{chat_username}/123`"
                    )
                    await message.reply(info, reply_markup=main_menu_keyboard())

                    if LOGIN_SYSTEM and acc != user_client:
                        await acc.stop()
                except UsernameNotOccupied:
                    await message.reply(
                        f"**❌ Username Not Found**\n\n"
                        f"**Target:** `{chat_username}`\n\n"
                        f"This username doesn't exist. Check the spelling.",
                        reply_markup=main_menu_keyboard()
                    )
                except UsernameInvalid:
                    await message.reply(
                        f"**❌ Invalid Username**\n\n"
                        f"**Target:** `{chat_username}`\n\n"
                        f"This is not a valid Telegram username.",
                        reply_markup=main_menu_keyboard()
                    )
                except Exception as e:
                    try:
                        await acc.join_chat(chat_username)
                        await message.reply(
                            f"**✅ Joined Successfully!**\n\n"
                            f"**Target:** `{chat_username}`",
                            reply_markup=main_menu_keyboard()
                        )
                    except Exception as e2:
                        await message.reply(
                            f"**❌ Cannot Access**\n\n"
                            f"**Target:** `{chat_username}`\n"
                            f"**Error:** {e2}\n\n"
                            f"Make sure you're a member of this channel/group.",
                            reply_markup=main_menu_keyboard()
                        )
                    if LOGIN_SYSTEM and acc != user_client:
                        try:
                            await acc.stop()
                        except:
                            pass
            else:
                await message.reply(
                    "**🔐 Login Required**\n\n"
                    "No user session found.\n"
                    "Use /login to authenticate.",
                    reply_markup=main_menu_keyboard()
                )
        except Exception as e:
            await message.reply(f"**Error:** {e}")
        return

    # Try with bot client first (public content)
    try:
        msg = await client.get_messages(chat_username, msg_start)
        if msg and not msg.empty:
            msg_type = get_message_type(msg)
            if msg_type and msg_type != "text":
                media_obj = getattr(msg, msg.media.value, None) if msg.media else None
                if media_obj and hasattr(media_obj, 'file_size'):
                    if media_obj.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                        await message.reply(
                            f"**📏 File Too Large**\n\n"
                            f"Size: {media_obj.file_size / 1024 / 1024:.1f}MB\n"
                            f"Limit: {MAX_FILE_SIZE_MB}MB",
                            reply_markup=main_menu_keyboard()
                        )
                        return

                os.makedirs(OUTPUT_DIR, exist_ok=True)
                folder = get_folder(msg_type)
                ext = get_ext(msg_type)
                file_name = f"{msg_start}.{ext}" if ext else str(msg_start)
                file_path = os.path.join(OUTPUT_DIR, folder, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                await client.download_media(msg, file_name=file_path)
                caption = msg.caption if (KEEP_ORIGINAL_CAPTION and msg.caption) else make_caption(msg, folder)
                await send_with_metadata(client, message.chat.id, file_path, caption, msg)

                try:
                    os.remove(file_path)
                except:
                    pass
                return
            elif msg_type == "text":
                await client.send_message(message.chat.id, msg.text)
                return
    except:
        # Auto-join if bot can't access
        try:
            acc = await get_auth_client(user_id)
            if acc:
                joined = await auto_join_channel(acc, chat_username)
                if joined:
                    await message.reply("**✅ Joined Channel**\n\nRetrying download...")
                    try:
                        if acc != client:
                            await acc.stop()
                    except:
                        pass
                    return
                try:
                    if acc != client:
                        await acc.stop()
                except:
                    pass
        except:
            pass
        pass

    # Fallback to user session (restricted content)
    acc = await get_auth_client(user_id)
    if not acc:
        await message.reply(
            "**🔐 Restricted Content**\n\n"
            "Cannot access this content via bot.\n"
            "Use /login to authenticate.",
            reply_markup=main_menu_keyboard()
        )
        return

    if msg_start == msg_end:
        await handle_single(client, acc, message, chat_username, msg_start, forward=True)
    else:
        total = msg_end - msg_start + 1
        IS_BATCH[user_id] = False

        # Create progress tracker
        progress = DownloadProgress(client, message.chat.id)
        await progress.create(total)
        USER_PROGRESS[user_id] = progress

        count = 0
        for msg_id in range(msg_start, msg_end + 1):
            if IS_BATCH.get(user_id):
                await progress.finish()
                await message.reply("**⏹ Batch Cancelled**\nProcess stopped by user.", reply_markup=main_menu_keyboard())
                break

            await handle_single(client, acc, message, chat_username, msg_id, forward=True, progress=progress)

            count += 1
            progress.update(downloaded=count)
            await progress.update_message()

            await asyncio.sleep(WAITING_TIME)

        if not IS_BATCH.get(user_id):
            progress.update(downloaded=count)
            await progress.finish()

        USER_PROGRESS.pop(user_id, None)

    if LOGIN_SYSTEM and acc != user_client:
        try:
            await acc.stop()
        except:
            pass

# ===========================================================================
#   END OF GENERATE PLUGIN
# ===========================================================================
