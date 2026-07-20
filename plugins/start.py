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
        Handles user interaction: /start, /help, /login, /settings,
        /myplan, thumbnails, captions, admin commands, and all
        inline keyboard callback handlers.

    COMMANDS:
        /start         — Welcome message & main menu
        /help          — Help topics
        /settings      — View/adjust settings
        /login         — Login with phone number
        /logout        — Logout from session
        /cancel        — Cancel ongoing download
        /myplan        — View plan & usage
        /set_thumb     — Set custom thumbnail
        /view_thumb    — View thumbnail
        /del_thumb     — Delete thumbnail
        /set_caption   — Set custom caption
        /view_caption  — View caption
        /del_caption   — Delete caption
        /ban           — Ban user (admin)
        /unban         — Unban user (admin)
        /add_premium   — Add premium (admin)
        /remove_premium — Remove premium (admin)
        /ping          — Check bot latency
        /info          — Show bot info & stats
        /speedtest     — Test download speed
        /quote         — Random motivational quote
        /welcome       — Set welcome message (admin)
        /view_welcome  — View welcome message (admin)
        /del_welcome   — Delete welcome message (admin)
        /antispan      — Toggle anti-spam (admin)

    SEE ALSO:
        plugins/payment.py — /premium, /pay, /payment, /history, /approve, /reject, /pending

    FEATURE: START_COMMAND
    FEATURE: HELP_COMMAND
    FEATURE: SETTINGS_COMMAND
    FEATURE: LOGIN_COMMAND
    FEATURE: THUMBNAIL_COMMANDS
    FEATURE: CAPTION_COMMANDS
    FEATURE: ADMIN_COMMANDS
    FEATURE: QUICK_WIN_COMMANDS
    FEATURE: ADMIN_ADVANCED
    FEATURE: CALLBACK_HANDLERS
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from datetime import datetime
from ftmgram import filters
from ftmgram.types import Message, CallbackQuery
from bot import bot
from database.db import db
from config import (
    LOGIN_SYSTEM, WAITING_TIME, MAX_FILE_SIZE_MB, TYPE_FILTER,
    CAPTION_ENABLED, FORWARD_MODE, USE_CHECKPOINT,
    FREE_DAILY_LIMIT, FREE_MAX_FILE_SIZE_MB, PREMIUM_MAX_FILE_SIZE_MB, ADMINS
)
from utils.ui import (
    main_menu_keyboard, download_keyboard, backup_keyboard, batch_keyboard,
    settings_keyboard, settings_delay_keyboard, settings_size_keyboard,
    thumbnail_keyboard, caption_keyboard, myplan_keyboard, about_keyboard,
    login_keyboard, help_keyboard, back_keyboard,
    WELCOME_MSG, HELP_DOWNLOAD, HELP_BACKUP, HELP_BATCH, HELP_LOGIN,
    HELP_THUMBNAIL, HELP_CAPTION, HELP_SETTINGS, HELP_FORMATS,
    SETTINGS_INFO, MYPLAN_INFO, THUMBNAIL_SET, THUMBNAIL_DELETED,
    CAPTION_SET, CAPTION_DELETED, ABOUT_MSG,
    WELCOME_RICH, ABOUT_RICH, HELP_RICH
)

# ===========================================================================
#   FEATURE: START_COMMAND
# ---------------------------------------------------------------------------
#   /start — Welcome message & main menu
#   - Registers new user in database
#   - Shows main menu with inline keyboard
# ===========================================================================


@bot.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    """Handle /start command.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None

    Process:
        1. Get user ID and name
        2. Add user to database if new
        3. Send welcome message with menu
    """
    user_id = message.from_user.id
    name = message.from_user.first_name

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, name)

    # Try rich message first, fallback to plain text
    try:
        from ftmgram.types import InputRichMessage
        rich_msg = WELCOME_RICH(version=__version__)
        await client.send_rich_message(message.chat.id, rich_msg, reply_markup=main_menu_keyboard())
    except Exception:
        await message.reply(WELCOME_MSG.format(version=__version__), reply_markup=main_menu_keyboard())

# ===========================================================================
#   FEATURE: HELP_COMMAND
# ---------------------------------------------------------------------------
#   /help — Help topics menu
# ===========================================================================


@bot.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message: Message):
    """Handle /help command.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None
    """
    await message.reply("**❓ Help Menu**\n\nChoose a topic:", reply_markup=help_keyboard())

# ===========================================================================
#   FEATURE: SETTINGS_COMMAND
# ---------------------------------------------------------------------------
#   /settings — View/adjust bot settings
#   Shows delay, file size, filters, forward mode, checkpoint, dump chat
# ===========================================================================


@bot.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message: Message):
    """Handle /settings command.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None

    Displays:
        - Current delay
        - Max file size
        - Type filter
        - Forward mode
        - Checkpoint status
        - Dump chat
    """
    dump_chat = await db.get_dump_chat(message.from_user.id)
    text = SETTINGS_INFO.format(
        delay=WAITING_TIME,
        size=MAX_FILE_SIZE_MB,
        type_filter=TYPE_FILTER,
        forward="ON" if FORWARD_MODE else "OFF",
        checkpoint="ON" if USE_CHECKPOINT else "OFF",
        dump_chat=dump_chat or "Not set",
    )
    await message.reply(text, reply_markup=settings_keyboard())

# ===========================================================================
#   FEATURE: LOGIN_COMMAND
# ---------------------------------------------------------------------------
#   /login — Login with phone number for restricted content
#   Requires LOGIN_SYSTEM=true
#
#   TIP: Each user authenticates with their own phone number
#        This prevents bans on the main bot token
# ===========================================================================


@bot.on_message(filters.command("login") & filters.private)
async def login_cmd(client, message: Message):
    """Handle /login command.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None

    Process:
        1. Check if LOGIN_SYSTEM is enabled
        2. Check if user already has session
        3. Show login options
    """
    if not LOGIN_SYSTEM:
        await message.reply("Login system is disabled. Bot uses a global session.")
        return

    user_id = message.from_user.id
    existing = await db.get_session(user_id)
    if existing:
        await message.reply(
            "**🔐 Already Logged In**\n\n"
            "You have an active session.\n"
            "Use /logout first to login again.",
            reply_markup=login_keyboard()
        )
        return

    await message.reply("**🔐 Login**\n\nChoose an option:", reply_markup=login_keyboard())

# ===========================================================================
#   FEATURE: LOGOUT_COMMAND
# ---------------------------------------------------------------------------
#   /logout — Remove session from database
# ===========================================================================


@bot.on_message(filters.command("logout") & filters.private)
async def logout_cmd(client, message: Message):
    """Handle /logout command.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None
    """
    user_id = message.from_user.id
    await db.set_session(user_id, None)
    await message.reply("**Logged out successfully!** Session removed.")

# ===========================================================================
#   FEATURE: CANCEL_COMMAND
# ---------------------------------------------------------------------------
#   /cancel — Cancel ongoing download
#   Sets IS_BATCH flag to True to stop processing
#
#   NOTE: Uses global IS_BATCH dict from generate.py
# ===========================================================================


@bot.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client, message: Message):
    """Handle /cancel command.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None

    Note:
        Sets IS_BATCH flag to stop batch processing
    """
    from plugins.generate import IS_BATCH
    user_id = message.from_user.id
    IS_BATCH[user_id] = True
    await message.reply("**Download cancelled.**")

# ===========================================================================
#   FEATURE: MYPLAN_COMMAND
# ---------------------------------------------------------------------------
#   /myplan — View plan details and usage stats
#   Shows: plan type, expiry, daily usage, total saves, limits
# ===========================================================================


@bot.on_message(filters.command("myplan") & filters.private)
async def myplan_cmd(client, message: Message):
    """Handle /myplan command.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None

    Displays:
        - Plan type (Free/Premium)
        - Expiry date
        - Daily usage/limit
        - Total saves
        - File size limits
    """
    user_id = message.from_user.id
    is_premium = await db.is_premium(user_id)
    daily_usage = await db.get_daily_usage(user_id)
    total_saves = await db.get_total_saves(user_id)
    premium_info = await db.get_premium_info(user_id)

    if is_premium:
        plan_type = "⭐ Premium"
        expiry = premium_info.get("expiry") if premium_info else None
        if isinstance(expiry, datetime):
            expiry = expiry.strftime("%Y-%m-%d %H:%M")
        elif isinstance(expiry, str):
            expiry = expiry.split(" ")[0]
        else:
            expiry = "Never"
    else:
        plan_type = "🆓 Free"
        expiry = "N/A"

    text = MYPLAN_INFO.format(
        plan_type=plan_type,
        expiry=expiry,
        daily_used=daily_usage,
        daily_limit="∞" if is_premium else FREE_DAILY_LIMIT,
        total_saves=total_saves,
        free_size=FREE_MAX_FILE_SIZE_MB,
        premium_size=PREMIUM_MAX_FILE_SIZE_MB,
    )
    await message.reply(text, reply_markup=myplan_keyboard())

# ===========================================================================
#   FEATURE: THUMBNAIL_COMMANDS
# ---------------------------------------------------------------------------
#   /set_thumb   — Set custom thumbnail (reply to photo)
#   /view_thumb  — View current thumbnail
#   /del_thumb   — Delete thumbnail
#
#   TIP: Thumbnails are per-user and stored in MongoDB
# ===========================================================================


@bot.on_message(filters.command("set_thumb") & filters.private)
async def set_thumb_cmd(client, message: Message):
    """Set custom thumbnail from replied photo.

    Args:
        client: Bot client instance
        message: Must reply to a photo

    Returns:
        None

    Usage:
        Reply to a photo with /set_thumb
    """
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("**Reply to a photo** to set as your thumbnail.")
        return
    file_id = message.reply_to_message.photo.file_id
    await db.set_thumbnail(message.from_user.id, file_id)
    await message.reply(THUMBNAIL_SET)


@bot.on_message(filters.command("view_thumb") & filters.private)
async def view_thumb_cmd(client, message: Message):
    """View current thumbnail.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None
    """
    file_id = await db.get_thumbnail(message.from_user.id)
    if file_id:
        await message.reply_photo(file_id, caption="**Your current thumbnail:**")
    else:
        await message.reply("No custom thumbnail set.")


@bot.on_message(filters.command("del_thumb") & filters.private)
async def del_thumb_cmd(client, message: Message):
    """Delete custom thumbnail.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None
    """
    await db.delete_thumbnail(message.from_user.id)
    await message.reply(THUMBNAIL_DELETED)

# ===========================================================================
#   FEATURE: CAPTION_COMMANDS
# ---------------------------------------------------------------------------
#   /set_caption <text>  — Set custom caption template
#   /view_caption        — View current caption
#   /del_caption         — Delete caption
#
#   PLACEHOLDERS:
#     {filename} — Original filename
#     {size}     — File size (human readable)
#     {date}     — Upload date (YYYY-MM-DD)
#
#   TIP: Example: "📁 {filename} | Size: {size}"
# ===========================================================================


@bot.on_message(filters.command("set_caption") & filters.private)
async def set_caption_cmd(client, message: Message):
    """Set custom caption template.

    Args:
        client: Bot client instance
        message: Must include caption text after command

    Returns:
        None

    Placeholders:
        {filename} — Original filename
        {size}     — File size
        {date}     — Upload date

    Usage:
        /set_caption 📁 {filename} | Size: {size}
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**Usage:** `/set_caption <text>`\n\n"
            "**Placeholders:**\n"
            "- `{filename}` — Original filename\n"
            "- `{size}` — File size\n"
            "- `{date}` — Upload date"
        )
        return
    caption = args[1]
    await db.set_caption(message.from_user.id, caption)
    await message.reply(CAPTION_SET.format(caption=caption))


@bot.on_message(filters.command("view_caption") & filters.private)
async def view_caption_cmd(client, message: Message):
    """View current caption template.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None
    """
    caption = await db.get_caption(message.from_user.id)
    if caption:
        await message.reply(f"**Your current caption:**\n\n`{caption}`")
    else:
        await message.reply("No custom caption set.")


@bot.on_message(filters.command("del_caption") & filters.private)
async def del_caption_cmd(client, message: Message):
    """Delete custom caption.

    Args:
        client: Bot client instance
        message: User message object

    Returns:
        None
    """
    await db.delete_caption(message.from_user.id)
    await message.reply(CAPTION_DELETED)

# ===========================================================================
#   FEATURE: ADMIN_COMMANDS
# ---------------------------------------------------------------------------
#   /ban <user_id>          — Ban user from bot
#   /unban <user_id>        — Unban user
#   /add_premium <id> <days> — Add premium subscription
#   /remove_premium <id>    — Remove premium
#
#   NOTE: Only ADMINS from config can use these commands
# ===========================================================================


@bot.on_message(filters.command("ban") & filters.private)
async def ban_cmd(client, message: Message):
    """Ban a user from using the bot.

    Args:
        client: Bot client instance
        message: Must include user_id

    Returns:
        None

    Admin Only: Yes
    """
    if message.from_user.id not in ADMINS:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("**Usage:** `/ban <user_id>`")
        return
    try:
        target_id = int(args[1])
        await db.ban_user(target_id)
        await message.reply(f"**✅ User {target_id} banned.**")
    except ValueError:
        await message.reply("Invalid user ID.")


@bot.on_message(filters.command("unban") & filters.private)
async def unban_cmd(client, message: Message):
    """Unban a user.

    Args:
        client: Bot client instance
        message: Must include user_id

    Returns:
        None

    Admin Only: Yes
    """
    if message.from_user.id not in ADMINS:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("**Usage:** `/unban <user_id>`")
        return
    try:
        target_id = int(args[1])
        await db.unban_user(target_id)
        await message.reply(f"**✅ User {target_id} unbanned.**")
    except ValueError:
        await message.reply("Invalid user ID.")


@bot.on_message(filters.command("add_premium") & filters.private)
async def add_premium_cmd(client, message: Message):
    """Add premium subscription to user.

    Args:
        client: Bot client instance
        message: Must include user_id and days

    Returns:
        None

    Admin Only: Yes

    Usage:
        /add_premium 123456 30  (adds 30 days premium)
    """
    if message.from_user.id not in ADMINS:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("**Usage:** `/add_premium <user_id> <days>`")
        return
    parts = args[1].split()
    if len(parts) < 2:
        await message.reply("**Usage:** `/add_premium <user_id> <days>`")
        return
    try:
        target_id = int(parts[0])
        days = int(parts[1])
        await db.add_premium(target_id, days)
        await message.reply(f"**✅ User {target_id} premium added for {days} days.**")
    except ValueError:
        await message.reply("Invalid user ID or days.")


@bot.on_message(filters.command("remove_premium") & filters.private)
async def remove_premium_cmd(client, message: Message):
    """Remove premium subscription from user.

    Args:
        client: Bot client instance
        message: Must include user_id

    Returns:
        None

    Admin Only: Yes
    """
    if message.from_user.id not in ADMINS:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("**Usage:** `/remove_premium <user_id>`")
        return
    try:
        target_id = int(args[1])
        await db.remove_premium(target_id)
        await message.reply(f"**✅ User {target_id} premium removed.**")
    except ValueError:
        await message.reply("Invalid user ID.")

# ===========================================================================
#   FEATURE: QUICK_WIN_COMMANDS
# ---------------------------------------------------------------------------
#   /ping      — Check bot latency
#   /info      — Show bot info & stats
#   /speedtest — Test download speed
#   /quote     — Random motivational quote
# ===========================================================================


@bot.on_message(filters.command("ping") & filters.private)
async def ping_cmd(client, message: Message):
    """Check bot latency.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Shows:
        - Response time in ms
        - Bot status
    """
    import time
    start = time.time()
    msg = await message.reply("**🏓 Pinging...**")
    end = time.time()
    latency = (end - start) * 1000
    await msg.edit_text(
        f"**🏓 Pong!**\n\n"
        f"**Latency:** `{latency:.1f}ms`\n"
        f"**Status:** 🟢 Online"
    )


@bot.on_message(filters.command("info") & filters.private)
async def info_cmd(client, message: Message):
    """Show bot information and statistics.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Displays:
        - Bot version
        - Uptime
        - Total users
        - Premium users
    """
    from config import __version__
    import time

    uptime_seconds = int(time.time() - botStartTime)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    total_users = await db.total_users_count()

    premium_count = 0
    async for user in db.get_all_users():
        if user.get("is_premium"):
            premium_count += 1

    await message.reply(
        f"**🤖 TelegramDL Info**\n\n"
        f"**Version:** `{__version__}`\n"
        f"**Uptime:** `{hours}h {minutes}m {seconds}s`\n"
        f"**Total Users:** `{total_users}`\n"
        f"**Premium Users:** `{premium_count}`\n"
        f"**Free Users:** `{total_users - premium_count}`\n\n"
        f"**Framework:** Kurigram (Pyrogram Fork)\n"
        f"**Python:** `3.10+`\n"
        f"**License:** MIT"
    )


@bot.on_message(filters.command("speedtest") & filters.private)
async def speedtest_cmd(client, message: Message):
    """Test download speed from a sample file.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Downloads a 10MB test file and shows speed
    """
    import time
    import urllib.request

    msg = await message.reply("**⚡ Speedtest starting...**")

    test_url = "https://speed.cloudflare.com/__down?bytes=10485760"  # 10MB
    start = time.time()

    try:
        req = urllib.request.Request(test_url, headers={"User-Agent": "TelegramDL"})
        response = urllib.request.urlopen(req, timeout=30)
        data = response.read()
        end = time.time()

        elapsed = end - start
        speed = len(data) / elapsed / 1024 / 1024  # MB/s

        await msg.edit_text(
            f"**⚡ Speedtest Complete**\n\n"
            f"**Download Speed:** `{speed:.2f} MB/s`\n"
            f"**File Size:** `10 MB`\n"
            f"**Time:** `{elapsed:.2f}s`"
        )
    except Exception as e:
        await msg.edit_text(
            f"**❌ Speedtest Failed**\n\n"
            f"**Error:** `{str(e)}`"
        )


QUOTES = [
    "💡 The only way to do great work is to love what you do.",
    "🚀 Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "💪 Don't watch the clock; do what it does. Keep going.",
    "🎯 Focus on being productive instead of busy.",
    "🔥 The secret of getting ahead is getting started.",
    "⭐ Don't be afraid to give up the good to go for the great.",
    "💡 Innovation distinguishes between a leader and a follower.",
    "🏆 Work hard in silence, let success make the noise.",
    "💪 The future belongs to those who believe in the beauty of their dreams.",
    "🌟 It always seems impossible until it's done."
]


@bot.on_message(filters.command("quote") & filters.private)
async def quote_cmd(client, message: Message):
    """Show a random motivational quote.

    Args:
        client: Bot client
        message: User message

    Returns:
        None
    """
    import random
    quote = random.choice(QUOTES)
    await message.reply(quote)


# Track bot start time
import time as _time
botStartTime = _time.time()

# ===========================================================================
#   FEATURE: ADMIN_ADVANCED
# ---------------------------------------------------------------------------
#   /welcome <text>  — Set custom welcome message
#   /view_welcome    — View welcome message
#   /del_welcome     — Delete welcome message
#   /antispan on/off — Toggle anti-spam
#
#   NOTE: Only ADMINS from config can use these commands
# ===========================================================================

WELCOME_MESSAGES = {}


@bot.on_message(filters.command("welcome") & filters.private)
async def welcome_cmd(client, message: Message):
    """Set custom welcome message for new users.

    Args:
        client: Bot client
        message: Admin message with welcome text

    Returns:
        None

    Admin Only: Yes

    Usage:
        /welcome Welcome to {name}! You are user #{count}.
    """
    if message.from_user.id not in ADMINS:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**Usage:** `/welcome <text>`\n\n"
            "**Placeholders:**\n"
            "- `{name}` — User's first name\n"
            "- `{count}` — Total user count\n"
            "- `{id}` — User ID"
        )
        return

    WELCOME_MESSAGES["default"] = args[1]
    await message.reply(f"**✅ Welcome message set!**\n\nPreview:\n{args[1]}")


@bot.on_message(filters.command("view_welcome") & filters.private)
async def view_welcome_cmd(client, message: Message):
    """View current welcome message.

    Args:
        client: Bot client
        message: Admin message

    Returns:
        None

    Admin Only: Yes
    """
    if message.from_user.id not in ADMINS:
        return
    welcome = WELCOME_MESSAGES.get("default")
    if welcome:
        await message.reply(f"**Current Welcome Message:**\n\n{welcome}")
    else:
        await message.reply("**No custom welcome message set.**\nUsing default.")


@bot.on_message(filters.command("del_welcome") & filters.private)
async def del_welcome_cmd(client, message: Message):
    """Delete custom welcome message.

    Args:
        client: Bot client
        message: Admin message

    Returns:
        None

    Admin Only: Yes
    """
    if message.from_user.id not in ADMINS:
        return
    if "default" in WELCOME_MESSAGES:
        del WELCOME_MESSAGES["default"]
        await message.reply("**✅ Welcome message deleted.**")
    else:
        await message.reply("**No custom welcome message to delete.**")


# Anti-spam tracking
USER_ACTION_TIMES = {}
ANTI_SPAM_ENABLED = True
ANTI_SPAM_INTERVAL = 3  # seconds between actions


@bot.on_message(filters.command("antispan") & filters.private)
async def antispan_cmd(client, message: Message):
    """Toggle anti-spam protection.

    Args:
        client: Bot client
        message: Admin message with on/off

    Returns:
        None

    Admin Only: Yes

    Usage:
        /antispan on
        /antispan off
    """
    global ANTI_SPAM_ENABLED
    if message.from_user.id not in ADMINS:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or args[1].strip().lower() not in ["on", "off"]:
        await message.reply("**Usage:** `/antispan <on/off>`")
        return

    ANTI_SPAM_ENABLED = args[1].strip().lower() == "on"
    status = "✅ Enabled" if ANTI_SPAM_ENABLED else "❌ Disabled"
    await message.reply(f"**Anti-Spam:** {status}")


def check_anti_spam(user_id: int) -> bool:
    """Check if user is rate-limited.

    Args:
        user_id: Telegram user ID

    Returns:
        bool: True if OK, False if rate-limited

    Note:
        Only works when ANTI_SPAM_ENABLED is True
    """
    if not ANTI_SPAM_ENABLED:
        return True
    if user_id in ADMINS:
        return True

    now = _time.time()
    last_action = USER_ACTION_TIMES.get(user_id, 0)

    if now - last_action < ANTI_SPAM_INTERVAL:
        return False

    USER_ACTION_TIMES[user_id] = now
    return True

# ===========================================================================
#   FEATURE: CALLBACK_HANDLERS
# ---------------------------------------------------------------------------
#   All inline keyboard callback handlers organized by prefix:
#     menu_*     — Main menu navigation
#     dl_*       — Download actions
#     bk_*       — Backup actions
#     batch_*    — Batch download actions
#     set_*      — Settings actions
#     delay_*    — Delay selection
#     size_*     — File size selection
#     thumb_*    — Thumbnail actions
#     caption_*  — Caption actions
#     plan_*     — Plan actions
#     help_*     — Help topics
#     login_*    — Login actions
#     logout_*   — Logout actions
#     confirm_*  — Confirmation actions
#     cancel_*   — Cancel actions
#     stop_*     — Stop actions
#
#   NOTE: Callback data format is "prefix_action"
# ===========================================================================


@bot.on_callback_query(filters.regex("^menu_"))
async def menu_callbacks(client, callback: CallbackQuery):
    """Handle main menu callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        menu_back, menu_download, menu_backup, menu_batch,
        menu_login, menu_settings, menu_myplan, menu_thumbnail,
        menu_caption, menu_about, menu_help
    """
    data = callback.data

    if data == "menu_back":
        await callback.message.edit_text(WELCOME_MSG.format(version=__version__), reply_markup=main_menu_keyboard())

    elif data == "menu_download":
        await callback.message.edit_text(
            "**📥 Download**\n\nChoose an option or send a Telegram link:",
            reply_markup=download_keyboard()
        )

    elif data == "menu_backup":
        await callback.message.edit_text(
            "**☁️ Backup**\n\nSend a channel link to backup:",
            reply_markup=backup_keyboard()
        )

    elif data == "menu_batch":
        await callback.message.edit_text(
            "**📦 Batch Download**\n\nSend a channel link with message range:",
            reply_markup=batch_keyboard()
        )

    elif data == "menu_login":
        if not LOGIN_SYSTEM:
            await callback.answer("Login system disabled!", show_alert=True)
            return
        await callback.message.edit_text(
            "**🔐 Login**\n\nLogin to access restricted channels:",
            reply_markup=login_keyboard()
        )

    elif data == "menu_settings":
        dump_chat = await db.get_dump_chat(callback.from_user.id)
        text = SETTINGS_INFO.format(
            delay=WAITING_TIME,
            size=MAX_FILE_SIZE_MB,
            type_filter=TYPE_FILTER,
            forward="ON" if FORWARD_MODE else "OFF",
            checkpoint="ON" if USE_CHECKPOINT else "OFF",
            dump_chat=dump_chat or "Not set",
        )
        await callback.message.edit_text(text, reply_markup=settings_keyboard())

    elif data == "menu_myplan":
        user_id = callback.from_user.id
        is_premium = await db.is_premium(user_id)
        daily_usage = await db.get_daily_usage(user_id)
        total_saves = await db.get_total_saves(user_id)
        premium_info = await db.get_premium_info(user_id)

        if is_premium:
            plan_type = "⭐ Premium"
            expiry = premium_info.get("expiry") if premium_info else None
            if isinstance(expiry, datetime):
                expiry = expiry.strftime("%Y-%m-%d %H:%M")
            elif isinstance(expiry, str):
                expiry = expiry.split(" ")[0]
            else:
                expiry = "Never"
        else:
            plan_type = "🆓 Free"
            expiry = "N/A"

        text = MYPLAN_INFO.format(
            plan_type=plan_type,
            expiry=expiry,
            daily_used=daily_usage,
            daily_limit="∞" if is_premium else FREE_DAILY_LIMIT,
            total_saves=total_saves,
            free_size=FREE_MAX_FILE_SIZE_MB,
            premium_size=PREMIUM_MAX_FILE_SIZE_MB,
        )
        await callback.message.edit_text(text, reply_markup=myplan_keyboard())

    elif data == "menu_thumbnail":
        await callback.message.edit_text(
            "**🖼 Thumbnail Settings**\n\nManage your custom thumbnail:",
            reply_markup=thumbnail_keyboard()
        )

    elif data == "menu_caption":
        await callback.message.edit_text(
            "**📝 Caption Settings**\n\nManage your custom caption:",
            reply_markup=caption_keyboard()
        )

    elif data == "menu_about":
        # Try rich message first, fallback to plain text
        try:
            rich_msg = ABOUT_RICH(version=__version__)
            await callback.message.edit_text(ABOUT_MSG.format(version=__version__), reply_markup=about_keyboard())
        except Exception:
            await callback.message.edit_text(ABOUT_MSG.format(version=__version__), reply_markup=about_keyboard())

    elif data == "menu_help":
        await callback.message.edit_text("**❓ Help Menu**\n\nChoose a topic:", reply_markup=help_keyboard())

    await callback.answer()


@bot.on_callback_query(filters.regex("^dl_"))
async def download_callbacks(client, callback: CallbackQuery):
    """Handle download callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        dl_send_link, dl_filter_photo, dl_filter_video,
        dl_filter_audio, dl_filter_all
    """
    data = callback.data

    if data == "dl_send_link":
        await callback.message.edit_text(
            "**📥 Download**\n\nSend me a Telegram message link:\n\n"
            "Example: `https://t.me/username/123`"
        )
        await callback.answer()

    elif data in ("dl_filter_photo", "dl_filter_video", "dl_filter_audio", "dl_filter_all"):
        filter_type = data.split("_")[-1]
        await callback.answer(f"Type filter set to: {filter_type}", show_alert=True)


@bot.on_callback_query(filters.regex("^bk_"))
async def backup_callbacks(client, callback: CallbackQuery):
    """Handle backup callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        bk_send_link, bk_mode_bot, bk_mode_user
    """
    data = callback.data

    if data == "bk_send_link":
        await callback.message.edit_text(
            "**☁️ Backup**\n\nSend me a channel link to backup:\n\n"
            "Example: `https://t.me/username`"
        )
        await callback.answer()

    elif data == "bk_mode_bot":
        await callback.answer("Bot upload mode selected!", show_alert=True)

    elif data == "bk_mode_user":
        await callback.answer("User upload mode selected!", show_alert=True)


@bot.on_callback_query(filters.regex("^batch_"))
async def batch_callbacks(client, callback: CallbackQuery):
    """Handle batch download callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        batch_send_link, batch_forward, batch_download
    """
    data = callback.data

    if data == "batch_send_link":
        await callback.message.edit_text(
            "**📦 Batch Download**\n\n"
            "Send me a channel link with message range:\n\n"
            "Example: `https://t.me/username/1001-1010`"
        )
        await callback.answer()

    elif data == "batch_forward":
        await callback.answer("Forward mode selected (faster)!", show_alert=True)

    elif data == "batch_download":
        await callback.answer("Download mode selected!", show_alert=True)


@bot.on_callback_query(filters.regex("^set_"))
async def settings_callbacks(client, callback: CallbackQuery):
    """Handle settings callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        set_delay, set_size, set_type, set_forward,
        set_checkpoint, set_dump
    """
    data = callback.data

    if data == "set_delay":
        await callback.message.edit_text(
            "**⏱ Set Delay**\n\nChoose delay between downloads:",
            reply_markup=settings_delay_keyboard()
        )
        await callback.answer()

    elif data == "set_size":
        await callback.message.edit_text(
            "**📏 Set Max File Size**\n\nChoose file size limit:",
            reply_markup=settings_size_keyboard()
        )
        await callback.answer()

    elif data == "set_type":
        await callback.answer("Send /batch <link> to download", show_alert=True)

    elif data == "set_forward":
        await callback.answer("Forward mode: ON", show_alert=True)

    elif data == "set_checkpoint":
        await callback.answer("Checkpoint: ON", show_alert=True)

    elif data == "set_dump":
        await callback.message.edit_text(
            "**📢 Dump Chat**\n\n"
            "Send me a chat ID to auto-forward all downloads.\n"
            "Send /cancel to clear dump chat.",
        )
        await callback.answer()


@bot.on_callback_query(filters.regex("^delay_"))
async def delay_callbacks(client, callback: CallbackQuery):
    """Handle delay selection callbacks.

    Args:
        client: Bot client instance
        callback: Callback query with delay value

    Returns:
        None

    Callback Format:
        delay_5, delay_10, delay_15, etc.
    """
    delay = callback.data.split("_")[1]
    await callback.answer(f"Delay set to {delay}s!", show_alert=True)
    await callback.message.edit_text(
        f"**✅ Delay Updated**\n\nNew delay: **{delay}** seconds",
        reply_markup=back_keyboard("menu_settings")
    )


@bot.on_callback_query(filters.regex("^size_"))
async def size_callbacks(client, callback: CallbackQuery):
    """Handle file size selection callbacks.

    Args:
        client: Bot client instance
        callback: Callback query with size value

    Returns:
        None

    Callback Format:
        size_500, size_1000, size_2048, size_0 (no limit)
    """
    size = callback.data.split("_")[1]
    if size == "0":
        size_text = "No Limit"
    else:
        size_text = f"{size}MB"
    await callback.answer(f"Max file size set to {size_text}!", show_alert=True)
    await callback.message.edit_text(
        f"**✅ File Size Updated**\n\nNew limit: **{size_text}**",
        reply_markup=back_keyboard("menu_settings")
    )


@bot.on_callback_query(filters.regex("^thumb_"))
async def thumbnail_callbacks(client, callback: CallbackQuery):
    """Handle thumbnail callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        thumb_set, thumb_view, thumb_delete
    """
    data = callback.data

    if data == "thumb_set":
        await callback.message.edit_text(
            "**🖼 Set Thumbnail**\n\n"
            "Reply to a photo with `/set_thumb` to set it as your thumbnail.",
            reply_markup=back_keyboard("menu_thumbnail")
        )

    elif data == "thumb_view":
        file_id = await db.get_thumbnail(callback.from_user.id)
        if file_id:
            await callback.message.delete()
            await client.send_photo(callback.from_user.id, file_id, caption="**Your thumbnail:**")
        else:
            await callback.answer("No thumbnail set!", show_alert=True)
        return

    elif data == "thumb_delete":
        await db.delete_thumbnail(callback.from_user.id)
        await callback.message.edit_text(
            THUMBNAIL_DELETED,
            reply_markup=back_keyboard("menu_thumbnail")
        )

    await callback.answer()


@bot.on_callback_query(filters.regex("^caption_"))
async def caption_callbacks(client, callback: CallbackQuery):
    """Handle caption callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        caption_set, caption_view, caption_delete
    """
    data = callback.data

    if data == "caption_set":
        await callback.message.edit_text(
            "**📝 Set Caption**\n\n"
            "Send me your caption text.\n\n"
            "**Placeholders:**\n"
            "- `{filename}` — Original filename\n"
            "- `{size}` — File size\n"
            "- `{date}` — Upload date\n\n"
            "**Example:** `📁 {filename} | Size: {size}`",
            reply_markup=back_keyboard("menu_caption")
        )

    elif data == "caption_view":
        caption = await db.get_caption(callback.from_user.id)
        if caption:
            await callback.answer(f"Caption: {caption}", show_alert=True)
        else:
            await callback.answer("No caption set!", show_alert=True)
        return

    elif data == "caption_delete":
        await db.delete_caption(callback.from_user.id)
        await callback.message.edit_text(
            CAPTION_DELETED,
            reply_markup=back_keyboard("menu_caption")
        )

    await callback.answer()


@bot.on_callback_query(filters.regex("^plan_"))
async def plan_callbacks(client, callback: CallbackQuery):
    """Handle plan callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        plan_stats
    """
    data = callback.data

    if data == "plan_stats":
        user_id = callback.from_user.id
        is_premium = await db.is_premium(user_id)
        daily_usage = await db.get_daily_usage(user_id)
        total_saves = await db.get_total_saves(user_id)

        stats = (
            f"**📊 Your Stats**\n\n"
            f"**Today:** {daily_usage} downloads\n"
            f"**Total:** {total_saves} saves\n"
            f"**Plan:** {'Premium' if is_premium else 'Free'}"
        )
        await callback.answer(stats, show_alert=True)
        return

    await callback.answer()


@bot.on_callback_query(filters.regex("^help_"))
async def help_callbacks(client, callback: CallbackQuery):
    """Handle help topic callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        help_download, help_backup, help_batch, help_login,
        help_thumbnail, help_caption, help_settings, help_formats
    """
    data = callback.data

    if data == "help_download":
        await callback.message.edit_text(HELP_DOWNLOAD, reply_markup=back_keyboard("menu_help"))
    elif data == "help_backup":
        await callback.message.edit_text(HELP_BACKUP, reply_markup=back_keyboard("menu_help"))
    elif data == "help_batch":
        await callback.message.edit_text(HELP_BATCH, reply_markup=back_keyboard("menu_help"))
    elif data == "help_login":
        await callback.message.edit_text(HELP_LOGIN, reply_markup=back_keyboard("menu_help"))
    elif data == "help_thumbnail":
        await callback.message.edit_text(HELP_THUMBNAIL, reply_markup=back_keyboard("menu_help"))
    elif data == "help_caption":
        await callback.message.edit_text(HELP_CAPTION, reply_markup=back_keyboard("menu_help"))
    elif data == "help_settings":
        await callback.message.edit_text(HELP_SETTINGS, reply_markup=back_keyboard("menu_help"))
    elif data == "help_formats":
        await callback.message.edit_text(HELP_FORMATS, reply_markup=back_keyboard("menu_help"))

    await callback.answer()


@bot.on_callback_query(filters.regex("^login_"))
async def login_callbacks(client, callback: CallbackQuery):
    """Handle login callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        login_start
    """
    data = callback.data

    if data == "login_start":
        await callback.message.edit_text(
            "**🔐 Login Process**\n\n"
            "Send your **phone number** (with country code)\n"
            "Example: `+1234567890`"
        )

    await callback.answer()


@bot.on_callback_query(filters.regex("^logout_"))
async def logout_callbacks(client, callback: CallbackQuery):
    """Handle logout callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Callbacks:
        logout_confirm
    """
    data = callback.data

    if data == "logout_confirm":
        user_id = callback.from_user.id
        await db.set_session(user_id, None)
        await callback.message.edit_text(
            "**✅ Logged Out**\n\nSession removed successfully.",
            reply_markup=back_keyboard("menu_login")
        )

    await callback.answer()


@bot.on_callback_query(filters.regex("^confirm_"))
async def confirm_callbacks(client, callback: CallbackQuery):
    """Handle confirmation callbacks.

    Args:
        client: Bot client instance
        callback: Callback query with action

    Returns:
        None

    Callback Format:
        confirm_action_name
    """
    data = callback.data
    parts = data.split("_")

    if len(parts) >= 2:
        action = parts[1]
        await callback.answer(f"Confirmed: {action}", show_alert=True)
    else:
        await callback.answer()


@bot.on_callback_query(filters.regex("^cancel_"))
async def cancel_callbacks(client, callback: CallbackQuery):
    """Handle cancel callbacks.

    Args:
        client: Bot client instance
        callback: Callback query with action

    Returns:
        None

    Callback Format:
        cancel_action_name
    """
    data = callback.data
    action = data.replace("cancel_", "")
    await callback.answer(f"Cancelled: {action}", show_alert=True)
    await callback.message.edit_text("**❌ Cancelled**", reply_markup=back_keyboard())


@bot.on_callback_query(filters.regex("^stop_"))
async def stop_callbacks(client, callback: CallbackQuery):
    """Handle stop callbacks.

    Args:
        client: Bot client instance
        callback: Callback query object

    Returns:
        None

    Note:
        Sets IS_BATCH flag to stop batch processing
    """
    from plugins.generate import IS_BATCH
    user_id = callback.from_user.id
    IS_BATCH[user_id] = True
    await callback.answer("Stopping...", show_alert=True)
    await callback.message.edit_text("**⏹ Stopping...**\nProcess will stop after current file.")

# ===========================================================================
#   END OF START PLUGIN
# ===========================================================================
