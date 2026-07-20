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
        Full bot activity logging to a dedicated channel.
        Logs all user actions, downloads, errors, and admin operations.

    EVENTS LOGGED:
        - New user joins
        - /start commands
        - Download requests & completions
        - Login/logout events
        - Payment requests & approvals
        - Admin commands (ban, unban, premium)
        - Errors & exceptions

    CONFIG:
        LOG_CHANNEL — Channel ID for logs (with -100 prefix)
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import sys
import logging
from datetime import datetime
from ftmgram import filters, __version__ as ftmgram_version
from ftmgram.types import Message
from bot import bot
from database.db import db
from config import LOG_CHANNEL, ADMINS, __version__

logger = logging.getLogger(__name__)

# ===========================================================================
#   LOGGING UTILITIES
# ---------------------------------------------------------------------------
#   Helper functions to send formatted log messages
# ===========================================================================


async def log_to_channel(text: str, parse_mode: str = "markdown"):
    """Send log message to channel.

    Args:
        text: Log message text
        parse_mode: Message parse mode

    Returns:
        None

    Note:
        Silently fails if LOG_CHANNEL not set or invalid
    """
    if not LOG_CHANNEL:
        return
    try:
        await bot.send_message(
            chat_id=LOG_CHANNEL,
            text=text,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.warning(f"Failed to log to channel: {e}")


def format_user(user) -> str:
    """Format user info for logs.

    Args:
        user: Pyrogram user object

    Returns:
        str: Formatted user string
    """
    name = user.first_name or "Unknown"
    uid = user.id
    username = f"@{user.username}" if user.username else "no username"
    return f"**{name}** (`{uid}`) {username}"

# ===========================================================================
#   FEATURE: USER_ACTIVITY_LOGS
# ---------------------------------------------------------------------------
#   Log new users, /start commands, and user interactions
# ---------------------------------------------------------------------------
#   NOTE: /start logging is handled in plugins/start.py to avoid
#   duplicate handlers. Use log_to_channel() from start.py instead.
# ===========================================================================


async def log_start_event(user, is_new: bool):
    """Log /start command event (called from start.py).

    Args:
        user: User object from message.from_user
        is_new: Whether this is a new user

    Returns:
        None
    """
    status = "**🆕 New User**" if is_new else "**👤 Returning User**"

    await log_to_channel(
        f"**📡 /start Command**\n\n"
        f"{status}: {format_user(user)}\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

# ===========================================================================
#   FEATURE: DOWNLOAD_LOGS
# ---------------------------------------------------------------------------
#   Log all download activity (handled via callback)
# ===========================================================================


async def log_download_start(user, link: str):
    """Log download request start.

    Args:
        user: User object
        link: Download link

    Returns:
        None
    """
    await log_to_channel(
        f"**⬇️ Download Started**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**Link:** `{link[:80]}...`\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def log_download_complete(user, filename: str, size: str):
    """Log download completion.

    Args:
        user: User object
        filename: Downloaded file name
        size: File size

    Returns:
        None
    """
    await log_to_channel(
        f"**✅ Download Complete**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**File:** `{filename}`\n"
        f"**Size:** {size}\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def log_download_error(user, error: str):
    """Log download error.

    Args:
        user: User object
        error: Error message

    Returns:
        None
    """
    await log_to_channel(
        f"**❌ Download Error**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**Error:** `{error}`\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

# ===========================================================================
#   FEATURE: LOGIN_LOGS
# ---------------------------------------------------------------------------
#   Log login/logout events
# ===========================================================================


async def log_login(user):
    """Log user login.

    Args:
        user: User object

    Returns:
        None
    """
    await log_to_channel(
        f"**🔐 User Login**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def log_logout(user):
    """Log user logout.

    Args:
        user: User object

    Returns:
        None
    """
    await log_to_channel(
        f"**🚪 User Logout**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

# ===========================================================================
#   FEATURE: PAYMENT_LOGS
# ---------------------------------------------------------------------------
#   Log payment requests, approvals, and rejections
# ===========================================================================


async def log_payment_request(user, plan: str, price: str, request_id: str):
    """Log payment request.

    Args:
        user: User object
        plan: Plan name
        price: Plan price
        request_id: Payment request ID

    Returns:
        None
    """
    await log_to_channel(
        f"**💳 Payment Request**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**Plan:** {plan}\n"
        f"**Price:** {price}\n"
        f"**ID:** `{request_id}`\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def log_payment_approved(user, plan: str, days: int, request_id: str):
    """Log payment approval.

    Args:
        user: User object
        plan: Plan name
        days: Premium days
        request_id: Payment request ID

    Returns:
        None
    """
    await log_to_channel(
        f"**✅ Payment Approved**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**Plan:** {plan} ({days} days)\n"
        f"**ID:** `{request_id}`\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def log_payment_rejected(user, plan: str, request_id: str):
    """Log payment rejection.

    Args:
        user: User object
        plan: Plan name
        request_id: Payment request ID

    Returns:
        None
    """
    await log_to_channel(
        f"**❌ Payment Rejected**\n\n"
        f"**User:** {format_user(user)}\n"
        f"**Plan:** {plan}\n"
        f"**ID:** `{request_id}`\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

# ===========================================================================
#   FEATURE: ADMIN_LOGS
# ---------------------------------------------------------------------------
#   Log admin commands (ban, unban, premium add/remove)
# ===========================================================================


async def log_admin_ban(admin, target_id: int):
    """Log user ban.

    Args:
        admin: Admin user object
        target_id: Banned user ID

    Returns:
        None
    """
    await log_to_channel(
        f"**🚫 User Banned**\n\n"
        f"**Admin:** {format_user(admin)}\n"
        f"**Target ID:** `{target_id}`\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def log_admin_unban(admin, target_id: int):
    """Log user unban.

    Args:
        admin: Admin user object
        target_id: Unbanned user ID

    Returns:
        None
    """
    await log_to_channel(
        f"**✅ User Unbanned**\n\n"
        f"**Admin:** {format_user(admin)}\n"
        f"**Target ID:** `{target_id}`\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


async def log_admin_premium(admin, target_id: int, days: int):
    """Log premium addition.

    Args:
        admin: Admin user object
        target_id: User ID
        days: Premium days

    Returns:
        None
    """
    await log_to_channel(
        f"**⭐ Premium Added**\n\n"
        f"**Admin:** {format_user(admin)}\n"
        f"**Target ID:** `{target_id}`\n"
        f"**Duration:** {days} days\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

# ===========================================================================
#   FEATURE: ERROR_LOGS
# ---------------------------------------------------------------------------
#   Log unhandled exceptions and errors
# ===========================================================================


async def log_error(error: str, context: str = ""):
    """Log error to channel.

    Args:
        error: Error message
        context: Additional context

    Returns:
        None
    """
    text = (
        f"**🚨 Error Occurred**\n\n"
        f"**Error:** `{error}`\n"
    )
    if context:
        text += f"**Context:** `{context}`\n"
    text += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    await log_to_channel(text)


def log_exception(exc_type, exc_value, exc_tb):
    """Log Python exception.

    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_tb: Traceback object

    Returns:
        None
    """
    if LOG_CHANNEL:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(log_error(
                    str(exc_value),
                    f"Type: {exc_type.__name__}"
                ))
        except Exception:
            pass

# Install exception handler
sys.excepthook = log_exception

# ===========================================================================
#   FEATURE: BOT_STATS_LOG
# ---------------------------------------------------------------------------
#   Log bot statistics on startup
# ===========================================================================


@bot.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client, message: Message):
    """Show bot statistics.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Admin Only: Yes
    """
    if message.from_user.id not in ADMINS:
        return

    total_users = await db.total_users_count()
    is_premium_count = 0
    async for user in db.get_all_users():
        if user.get("is_premium"):
            is_premium_count += 1

    await message.reply(
        f"**📊 Bot Statistics**\n\n"
        f"**Version:** {__version__}\n"
        f"**Pyrogram:** {ftmgram_version}\n"
        f"**Total Users:** {total_users}\n"
        f"**Premium Users:** {is_premium_count}\n"
        f"**Free Users:** {total_users - is_premium_count}\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

# ===========================================================================
#   END OF LOGGING PLUGIN
# ===========================================================================
