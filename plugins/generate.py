import os
import re
import time
import asyncio
import logging
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import MessageMediaType
from pyrogram.errors import (
    FloodWait, UserNotParticipant, ChannelPrivate,
    UsernameNotOccupied, UsernameInvalid, PeerIdInvalid
)

from bot import bot, user_client, start_user_client
from database.db import db
from utils.progress import DownloadProgress
from utils.ui import progress_keyboard, stop_keyboard, confirm_keyboard, main_menu_keyboard
from config import (
    API_ID, API_HASH, LOGIN_SYSTEM, OUTPUT_DIR,
    WAITING_TIME, ERROR_MESSAGE, CHANNEL_ID, MAX_FILE_SIZE_MB
)

logger = logging.getLogger(__name__)

IS_BATCH = {}
USER_PROGRESS = {}


def get_message_type(msg):
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
    folders = {
        "photo": "Photos", "video": "Videos", "audio": "Audios",
        "voice": "Voice", "animation": "GIFs", "sticker": "Stickers",
        "document": "Documents",
    }
    return folders.get(msg_type, "Other")


def get_ext(msg_type):
    exts = {
        "photo": "jpg", "video": "mp4", "audio": "mp3",
        "voice": "ogg", "animation": "mp4", "document": "",
    }
    return exts.get(msg_type, "")


def make_caption(msg, folder):
    date_str = msg.date.strftime("%Y-%m-%d") if msg.date else "unknown"
    return f"{folder} | {date_str} | #{msg.id}"


def parse_channel_username(link):
    """Parse ALL Telegram link types to extract chat username and message IDs.

    Supported formats:
    - t.me/username/1001-1010     → batch range
    - t.me/username/123           → single message
    - t.me/username/s/123         → story
    - t.me/c/1234567890/123       → private channel msg
    - t.me/c/1234567890           → private channel (no msg)
    - t.me/b/botusername/123      → bot chat msg
    - t.me/b/botusername          → bot chat (no msg)
    - t.me/+invitehash            → invite link
    - t.me/joinchat/invitehash    → invite link (old format)
    - t.me/username               → channel/group/bot (no msg)
    - username                    → plain username
    - -1001234567890              → numeric chat ID
    - -1001234567890/123          → numeric chat ID + msg
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


async def get_auth_client(user_id):
    if LOGIN_SYSTEM:
        session = await db.get_session(user_id)
        if session:
            from pyrogram import Client
            client = Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=session)
            await client.start()
            return client
        return None
    else:
        await start_user_client()
        return user_client


async def download_with_retry(client, msg, dest):
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


async def forward_single(client, dest_chat, msg):
    for attempt in range(3):
        try:
            await client.forward_messages(dest_chat, msg.chat.id, msg.id)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except Exception:
            return False
    return False


async def send_with_metadata(client, chat_id, file_path, caption, msg, caption_entities=None):
    """Send file with metadata: thumbnail, duration, dimensions, caption entities."""
    for attempt in range(3):
        try:
            # Download thumbnail if available
            thumb = None
            try:
                if msg.media == MessageMediaType.VIDEO and msg.video.thumbs:
                    thumb = await client.download_media(msg.video.thumbs[0].file_id)
                elif msg.media == MessageMediaType.DOCUMENT and msg.document.thumbs:
                    thumb = await client.download_media(msg.document.thumbs[0].file_id)
                elif msg.media == MessageMediaType.AUDIO and msg.audio.thumbs:
                    thumb = await client.download_media(msg.audio.thumbs[0].file_id)
            except:
                thumb = None

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

            # Cleanup thumbnail
            if thumb and os.path.exists(thumb):
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

    # Cleanup thumbnail on failure
    if thumb and os.path.exists(thumb):
        try:
            os.remove(thumb)
        except:
            pass
    return False


async def handle_single(client, acc, message, chat_id, msg_id, forward=False, progress=None):
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

        # Check file size
        media_obj = getattr(msg, msg.media.value, None) if msg.media else None
        if media_obj and hasattr(media_obj, 'file_size'):
            if media_obj.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                await client.send_message(
                    message.chat.id,
                    f"Skipped #{msg_id}: too large ({media_obj.file_size / 1024 / 1024:.1f}MB)"
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

        caption = make_caption(msg, folder) if msg.caption else (msg.caption or "")
        caption_entities = msg.caption_entities if msg.caption_entities else None
        sent = await send_with_metadata(client, message.chat.id, file_path, caption, msg, caption_entities)

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


@bot.on_callback_query(filters.regex("cancel_download"))
async def cancel_callback(client, callback: CallbackQuery):
    user_id = callback.from_user.id
    IS_BATCH[user_id] = True
    await callback.answer("Download cancelled!")
    await callback.message.edit_text(
        "**❌ Download Cancelled**\n\nProcess stopped by user.",
        reply_markup=main_menu_keyboard()
    )


@bot.on_message(filters.command("batch") & filters.private)
async def batch_cmd(client, message: Message):
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


@bot.on_message(filters.text & filters.private, group=2)
async def save(client, message: Message):
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

    if IS_BATCH.get(user_id):
        IS_BATCH[user_id] = False
        await message.reply("**⏹ Cancelled**\nBatch processing stopped.", reply_markup=main_menu_keyboard())
        return

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
                    # Try to get story via user client
                    # In Pyrogram, stories require getting the user first
                    user = await acc.get_users(chat_username)
                    if hasattr(acc, 'get_story'):
                        story = await acc.get_story(user.id, story_id)
                        if story and story.media:
                            await handle_single(client, acc, message, chat_username, story_id, forward=False)
                        else:
                            await message.reply("**❌ Story Not Found**\n\nThis story may not exist or is no longer available.")
                    else:
                        await message.reply(
                            "**📖 Story Download**\n\n"
                            "Stories require the user client to be connected.\n"
                            "Please use /login to authenticate first.",
                            reply_markup=main_menu_keyboard()
                        )
                except Exception as e:
                    await message.reply(
                        f"**❌ Story Error**\n\n"
                        f"**Error:** {e}\n\n"
                        "Stories may not be accessible via this method.\n"
                        "Try using Plus Messenger to get story IDs.",
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
                caption = make_caption(msg, folder) if msg.caption else (msg.caption or "")
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
