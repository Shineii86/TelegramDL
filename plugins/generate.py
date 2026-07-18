import os
import re
import time
import asyncio
import logging
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait, UserNotParticipant, ChannelPrivate

from bot import bot, user_client, start_user_client
from database.db import db
from config import (
    API_ID, API_HASH, LOGIN_SYSTEM, OUTPUT_DIR,
    WAITING_TIME, ERROR_MESSAGE, CHANNEL_ID, MAX_FILE_SIZE_MB
)

logger = logging.getLogger(__name__)

IS_BATCH = {}
USER_STATUS = {}
SEMAPHORE = asyncio.Semaphore(3)


def progress_callback(current, total, user_id, msg_id):
    pct = current / total * 100
    status_file = f"progress_{user_id}_{msg_id}.txt"
    with open(status_file, "w") as f:
        f.write(str(int(pct)))


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
    link = link.strip()
    batch_match = re.search(r't\.me/([^/]+)/(\d+)-(\d+)', link)
    if batch_match:
        return batch_match.group(1), int(batch_match.group(2)), int(batch_match.group(3))
    single_match = re.search(r't\.me/(?:c/)?([^/]+)/(\d+)', link)
    if single_match:
        username = single_match.group(1)
        msg_id = int(single_match.group(2))
        if "/c/" in link:
            username = f"-100{username}"
        return username, msg_id, msg_id
    invite_match = re.search(r't\.me/\+([^/]+)', link)
    if invite_match:
        return invite_match.group(1), None, None
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


async def send_with_metadata(client, chat_id, file_path, caption, msg):
    for attempt in range(3):
        try:
            if file_path.endswith((".jpg", ".jpeg", ".png", ".webp")):
                await client.send_photo(chat_id, file_path, caption=caption)
            elif file_path.endswith((".mp4", ".mkv", ".avi")):
                duration = 0
                if msg.media == MessageMediaType.VIDEO:
                    vid = getattr(msg, "video", None)
                    if vid and hasattr(vid, "duration"):
                        duration = vid.duration
                await client.send_video(chat_id, file_path, caption=caption, duration=duration)
            elif file_path.endswith((".mp3", ".ogg", ".wav")):
                await client.send_audio(chat_id, file_path, caption=caption)
            else:
                await client.send_document(chat_id, file_path, caption=caption)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except Exception as e:
            logger.error(f"Send failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)
    return False


async def handle_single(client, acc, message, chat_id, msg_id, forward=False):
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
        sent = await send_with_metadata(client, message.chat.id, file_path, caption, msg)

        try:
            os.remove(file_path)
        except:
            pass
        try:
            os.remove(f"progress_{message.chat.id}_{msg_id}.txt")
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


async def handle_album(client, acc, message, chat_id, first_msg_id, last_msg_id):
    """Handle album (grouped messages)."""
    try:
        if isinstance(chat_id, str) and (chat_id.isdigit() or chat_id.startswith("-100")):
            chat_id = int(chat_id)

        messages = []
        for mid in range(first_msg_id, last_msg_id + 1):
            msg = await acc.get_messages(chat_id, mid)
            if msg and msg.media and msg.grouped_id:
                messages.append(msg)
            elif msg and not messages:
                messages.append(msg)

        if not messages:
            return

        media_list = []
        for msg in messages:
            msg_type = get_message_type(msg)
            if msg_type:
                folder = get_folder(msg_type)
                ext = get_ext(msg_type)
                file_name = f"{msg.id}.{ext}" if ext else str(msg.id)
                file_path = os.path.join(OUTPUT_DIR, folder, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                success = await download_with_retry(acc, msg, file_path)
                if success:
                    media_list.append(file_path)

        if media_list:
            caption = make_caption(messages[0], get_folder(get_message_type(messages[0]))) if messages[0].caption else ""
            try:
                await client.send_media_group(message.chat.id, [
                    (await _media_input(client, f, caption if i == 0 else ""))
                    for i, f in enumerate(media_list)
                ])
            except:
                for f in media_list:
                    await client.send_document(message.chat.id, f)

            for f in media_list:
                try:
                    os.remove(f)
                except:
                    pass

    except Exception as e:
        logger.error(f"Album error: {e}")


async def _media_input(client, file_path, caption):
    from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio
    if file_path.endswith((".jpg", ".jpeg", ".png", ".webp")):
        return InputMediaPhoto(file_path, caption=caption)
    elif file_path.endswith((".mp4", ".mkv")):
        return InputMediaVideo(file_path, caption=caption)
    elif file_path.endswith((".mp3", ".ogg")):
        return InputMediaAudio(file_path, caption=caption)
    else:
        return InputMediaDocument(file_path, caption=caption)


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

    await message.reply(f"Starting batch download from {msg_start} to {msg_end}...")

    IS_BATCH[user_id] = False
    count = 0

    for msg_id in range(msg_start, msg_end + 1):
        if IS_BATCH.get(user_id):
            await message.reply("Batch cancelled.")
            break

        await handle_single(client, acc, message, chat_username, msg_id, forward=True)
        count += 1

        if count % 10 == 0:
            await message.reply(f"Progress: {count}/{msg_end - msg_start + 1}")

        await asyncio.sleep(WAITING_TIME)

    await message.reply(f"Batch complete! Processed {count} messages.")

    if LOGIN_SYSTEM and acc != user_client:
        try:
            await acc.stop()
        except:
            pass


@bot.on_message(filters.text & filters.private, group=2)
async def save(client, message: Message):
    text = message.text.strip()
    user_id = message.from_user.id

    if not text.startswith("http") and "t.me" not in text:
        return

    if IS_BATCH.get(user_id):
        IS_BATCH[user_id] = False
        await message.reply("Batch processing cancelled.")
        return

    chat_username, msg_start, msg_end = parse_channel_username(text)

    if msg_start is None:
        try:
            acc = await get_auth_client(user_id)
            if acc:
                try:
                    await acc.join_chat(text)
                    await message.reply("Joined the channel successfully!")
                except Exception as e:
                    await message.reply(f"Failed to join: {e}")
                if LOGIN_SYSTEM and acc != user_client:
                    await acc.stop()
            else:
                await message.reply("No user session. Use /login first.")
        except Exception as e:
            await message.reply(f"Error: {e}")
        return

    # Try with bot client first
    try:
        msg = await client.get_messages(chat_username, msg_start)
        if msg and not msg.empty:
            msg_type = get_message_type(msg)
            if msg_type and msg_type != "text":
                media_obj = getattr(msg, msg.media.value, None) if msg.media else None
                if media_obj and hasattr(media_obj, 'file_size'):
                    if media_obj.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                        await message.reply(f"File too large ({media_obj.file_size / 1024 / 1024:.1f}MB)")
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

    # Fallback to user session
    acc = await get_auth_client(user_id)
    if not acc:
        await message.reply("Cannot access restricted content.\nUse /login to authenticate.")
        return

    if msg_start == msg_end:
        await handle_single(client, acc, message, chat_username, msg_start, forward=True)
    else:
        IS_BATCH[user_id] = False
        for msg_id in range(msg_start, msg_end + 1):
            if IS_BATCH.get(user_id):
                await message.reply("Batch cancelled.")
                break
            await handle_single(client, acc, message, chat_username, msg_id, forward=True)
            await asyncio.sleep(WAITING_TIME)

    if LOGIN_SYSTEM and acc != user_client:
        try:
            await acc.stop()
        except:
            pass
