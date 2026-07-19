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
        Premium payment system with multiple payment methods,
        request/approval workflow, and payment history.

    COMMANDS:
        /premium       — View premium plans
        /pay <plan>    — Request premium subscription
        /payment       — View payment methods
        /history       — View payment history (admin)
        /approve <id>  — Approve payment (admin)
        /reject <id>   — Reject payment (admin)
        /pending       — View pending payments (admin)

    FEATURES:
        FEATURE: PREMIUM_PLANS
        FEATURE: PAYMENT_REQUEST
        FEATURE: PAYMENT_METHODS
        FEATURE: PAYMENT_APPROVAL
        FEATURE: PAYMENT_HISTORY
        FEATURE: AUTO_APPROVE
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

import time
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot import bot
from database.db import db
from config import ADMINS, ADMIN_CONTACT

logger = logging.getLogger(__name__)

# ===========================================================================
#   CONSTANTS
# ---------------------------------------------------------------------------
#   PREMIUM_PLANS: Available subscription plans
#   PAYMENT_METHODS: Supported payment methods
# ===========================================================================

PREMIUM_PLANS = {
    "weekly": {
        "name": "Weekly",
        "days": 7,
        "price": "₹49 / $1",
        "emoji": "📅",
        "features": ["Unlimited downloads", "4GB file size", "Priority speed"]
    },
    "monthly": {
        "name": "Monthly",
        "days": 30,
        "price": "₹149 / $3",
        "emoji": "📆",
        "features": ["Unlimited downloads", "4GB file size", "Priority speed", "Custom thumbnails"]
    },
    "yearly": {
        "name": "Yearly",
        "days": 365,
        "price": "₹999 / $15",
        "emoji": "🗓",
        "features": ["Unlimited downloads", "4GB file size", "Priority speed", "Custom thumbnails", "Custom captions", "Dump chat"]
    },
    "lifetime": {
        "name": "Lifetime",
        "days": 36500,
        "price": "₹1999 / $25",
        "emoji": "♾️",
        "features": ["Everything in Yearly", "Lifetime access", "Priority support"]
    }
}

PAYMENT_METHODS = {
    "upi": {
        "name": "UPI",
        "emoji": "📱",
        "details": "`telegramdl@upi`",
        "instructions": "Send payment and screenshot"
    },
    "paypal": {
        "name": "PayPal",
        "emoji": "💳",
        "details": "`paypal.me/telegramdl`",
        "instructions": "Send payment and screenshot"
    },
    "crypto": {
        "name": "Crypto (USDT)",
        "emoji": "₿",
        "details": "`TN3Vj8qXxZQ1nH9pLmK4rT6wY2bS7dF8g`",
        "instructions": "Send TRC20 USDT and transaction ID"
    },
    "bank": {
        "name": "Bank Transfer",
        "emoji": "🏦",
        "details": "Contact admin for bank details",
        "instructions": "Send receipt screenshot"
    }
}

# ===========================================================================
#   FEATURE: PREMIUM_PLANS
# ---------------------------------------------------------------------------
#   /premium — View available plans and pricing
#   Shows all plans with features and pricing
# ===========================================================================


@bot.on_message(filters.command("premium") & filters.private)
async def premium_cmd(client, message: Message):
    """Show premium plans and pricing.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Displays:
        - All available plans
        - Pricing for each plan
        - Features included
        - Payment methods
    """
    user_id = message.from_user.id
    is_premium = await db.is_premium(user_id)
    premium_info = await db.get_premium_info(user_id)

    text = "**⭐ Premium Plans**\n\n"

    if is_premium:
        expiry = premium_info.get("expiry") if premium_info else None
        if isinstance(expiry, datetime):
            expiry = expiry.strftime("%Y-%m-%d")
        text += f"**Your Status:** ⭐ Premium\n**Expires:** {expiry}\n\n"

    for key, plan in PREMIUM_PLANS.items():
        features = "\n".join(f"  • {f}" for f in plan["features"])
        text += (
            f"{plan['emoji']} **{plan['name']}** — {plan['price']}\n"
            f"  {plan['days']} days\n"
            f"{features}\n\n"
        )

    text += "**💳 Payment Methods:**\n"
    for key, method in PAYMENT_METHODS.items():
        text += f"  {method['emoji']} {method['name']}: {method['details']}\n"

    text += f"\n**To purchase:** `/pay <plan>`\n"
    text += f"**Example:** `/pay monthly`\n\n"
    text += f"**Contact:** {ADMIN_CONTACT}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Pay Now", callback_data="pay_now"),
            InlineKeyboardButton("📋 Payment Methods", callback_data="pay_methods"),
        ],
        [
            InlineKeyboardButton("📊 My Plan", callback_data="menu_myplan"),
            InlineKeyboardButton("🔙 Back", callback_data="menu_back"),
        ],
    ])

    await message.reply(text, reply_markup=keyboard)

# ===========================================================================
#   FEATURE: PAYMENT_REQUEST
# ---------------------------------------------------------------------------
#   /pay <plan> — Request premium subscription
#   Creates payment request and notifies admin
#
#   FEATURE: PAYMENT_METHODS
# ===========================================================================


@bot.on_message(filters.command("pay") & filters.private)
async def pay_cmd(client, message: Message):
    """Request premium subscription.

    Args:
        client: Bot client
        message: User message with plan name

    Returns:
        None

    Usage:
        /pay weekly
        /pay monthly
        /pay yearly
        /pay lifetime

    Process:
        1. Validate plan name
        2. Create payment request
        3. Show payment instructions
        4. Notify admin
    """
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        plans_text = ", ".join(PREMIUM_PLANS.keys())
        await message.reply(
            f"**💳 Premium Plans**\n\n"
            f"**Available Plans:** {plans_text}\n\n"
            f"**Usage:** `/pay <plan>`\n"
            f"**Example:** `/pay monthly`"
        )
        return

    plan_key = args[1].strip().lower()

    if plan_key not in PREMIUM_PLANS:
        await message.reply(
            f"**❌ Invalid Plan**\n\n"
            f"**Available:** {', '.join(PREMIUM_PLANS.keys())}"
        )
        return

    plan = PREMIUM_PLANS[plan_key]

    # Create payment request
    request_id = f"{user_id}_{int(time.time())}"
    await db.create_payment_request(
        user_id=user_id,
        request_id=request_id,
        plan=plan_key,
        days=plan["days"],
        price=plan["price"]
    )

    # Show payment methods
    text = (
        f"**💳 Payment Request Created**\n\n"
        f"**Plan:** {plan['emoji']} {plan['name']}\n"
        f"**Duration:** {plan['days']} days\n"
        f"**Price:** {plan['price']}\n"
        f"**Request ID:** `{request_id}`\n\n"
        f"**Choose Payment Method:**\n"
    )

    for key, method in PAYMENT_METHODS.items():
        text += f"\n{method['emoji']} **{method['name']}**\n"
        text += f"  Details: {method['details']}\n"
        text += f"  {method['instructions']}\n"

    text += f"\n**After payment, send screenshot to admin:**\n{ADMIN_CONTACT}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 UPI", callback_data="pay_upi")],
        [InlineKeyboardButton("💳 PayPal", callback_data="pay_paypal")],
        [InlineKeyboardButton("₿ Crypto", callback_data="pay_crypto")],
        [InlineKeyboardButton("🏦 Bank", callback_data="pay_bank")],
        [InlineKeyboardButton("📸 Send Screenshot", callback_data="pay_screenshot")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])

    await message.reply(text, reply_markup=keyboard)

    # Notify admin
    for admin_id in ADMINS:
        try:
            await client.send_message(
                admin_id,
                f"**🔔 New Payment Request**\n\n"
                f"**User:** {message.from_user.first_name} (`{user_id}`)\n"
                f"**Plan:** {plan['name']}\n"
                f"**Price:** {plan['price']}\n"
                f"**Request ID:** `{request_id}`\n\n"
                f"**To approve:** `/approve {request_id}`\n"
                f"**To reject:** `/reject {request_id}`"
            )
        except:
            pass

# ===========================================================================
#   FEATURE: PAYMENT_METHODS
# ---------------------------------------------------------------------------
#   Shows detailed payment instructions for each method
# ===========================================================================


@bot.on_message(filters.command("payment") & filters.private)
async def payment_cmd(client, message: Message):
    """Show payment methods and instructions.

    Args:
        client: Bot client
        message: User message

    Returns:
        None

    Displays:
        - All payment methods
        - Account details
        - Instructions for each method
    """
    text = "**💳 Payment Methods**\n\n"

    for key, method in PAYMENT_METHODS.items():
        text += (
            f"{method['emoji']} **{method['name']}**\n"
            f"  Details: {method['details']}\n"
            f"  {method['instructions']}\n\n"
        )

    text += (
        f"**After payment:**\n"
        f"1. Take screenshot of payment\n"
        f"2. Send to admin: {ADMIN_CONTACT}\n"
        f"3. Include your user ID: `{message.from_user.id}`\n\n"
        f"**Or use:** `/pay <plan>` to create request"
    )

    await message.reply(text)

# ===========================================================================
#   FEATURE: PAYMENT_APPROVAL
# ---------------------------------------------------------------------------
#   /approve <request_id> — Approve payment
#   /reject <request_id>  — Reject payment
#   /pending              — View pending requests
#   /history              — View payment history
#
#   NOTE: Admin only commands
# ===========================================================================


@bot.on_message(filters.command("approve") & filters.private)
async def approve_cmd(client, message: Message):
    """Approve a payment request.

    Args:
        client: Bot client
        message: Admin message with request_id

    Returns:
        None

    Admin Only: Yes

    Process:
        1. Validate admin
        2. Find payment request
        3. Add premium to user
        4. Notify user
        5. Log to history
    """
    if message.from_user.id not in ADMINS:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("**Usage:** `/approve <request_id>`")
        return

    request_id = args[1].strip()

    # Get payment request
    request = await db.get_payment_request(request_id)
    if not request:
        await message.reply("**❌ Request not found**")
        return

    if request.get("status") == "approved":
        await message.reply("**⚠️ Already approved**")
        return

    # Approve
    user_id = request["user_id"]
    days = request["days"]
    plan = request["plan"]
    price = request["price"]

    await db.add_premium(user_id, days)
    await db.update_payment_status(request_id, "approved")
    await db.add_payment_history(
        user_id=user_id,
        request_id=request_id,
        plan=plan,
        days=days,
        price=price,
        status="approved"
    )

    # Notify user
    try:
        await client.send_message(
            user_id,
            f"**✅ Payment Approved!**\n\n"
            f"**Plan:** {PREMIUM_PLANS[plan]['name']}\n"
            f"**Duration:** {days} days\n"
            f"**Expires:** {(datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')}\n\n"
            f"**Enjoy your premium features!** 🎉"
        )
    except:
        pass

    await message.reply(
        f"**✅ Approved!**\n\n"
        f"**User:** `{user_id}`\n"
        f"**Plan:** {plan}\n"
        f"**Duration:** {days} days"
    )


@bot.on_message(filters.command("reject") & filters.private)
async def reject_cmd(client, message: Message):
    """Reject a payment request.

    Args:
        client: Bot client
        message: Admin message with request_id

    Returns:
        None

    Admin Only: Yes
    """
    if message.from_user.id not in ADMINS:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("**Usage:** `/reject <request_id>`")
        return

    request_id = args[1].strip()

    request = await db.get_payment_request(request_id)
    if not request:
        await message.reply("**❌ Request not found**")
        return

    user_id = request["user_id"]

    await db.update_payment_status(request_id, "rejected")
    await db.add_payment_history(
        user_id=user_id,
        request_id=request_id,
        plan=request["plan"],
        days=request["days"],
        price=request["price"],
        status="rejected"
    )

    # Notify user
    try:
        await client.send_message(
            user_id,
            f"**❌ Payment Rejected**\n\n"
            f"**Request ID:** `{request_id}`\n\n"
            f"Contact admin for details: {ADMIN_CONTACT}"
        )
    except:
        pass

    await message.reply(f"**❌ Rejected:** `{request_id}`")


@bot.on_message(filters.command("pending") & filters.private)
async def pending_cmd(client, message: Message):
    """View pending payment requests.

    Args:
        client: Bot client
        message: Admin message

    Returns:
        None

    Admin Only: Yes

    Displays:
        - All pending requests
        - User info
        - Plan details
    """
    if message.from_user.id not in ADMINS:
        return

    pending = await db.get_pending_payments()

    if not pending:
        await message.reply("**No pending payments**")
        return

    text = "**📋 Pending Payments**\n\n"

    for req in pending[:10]:  # Show max 10
        text += (
            f"**ID:** `{req['request_id']}`\n"
            f"**User:** `{req['user_id']}`\n"
            f"**Plan:** {req['plan']}\n"
            f"**Price:** {req['price']}\n"
            f"**Date:** {req.get('created_at', 'N/A')}\n"
            f"**Approve:** `/approve {req['request_id']}`\n\n"
        )

    await message.reply(text)


@bot.on_message(filters.command("history") & filters.private)
async def history_cmd(client, message: Message):
    """View payment history.

    Args:
        client: Bot client
        message: Admin message

    Returns:
        None

    Admin Only: Yes

    Displays:
        - All payment transactions
        - Status (approved/rejected)
        - User and plan info
    """
    if message.from_user.id not in ADMINS:
        return

    history = await db.get_payment_history()

    if not history:
        await message.reply("**No payment history**")
        return

    text = "**📜 Payment History**\n\n"

    for h in history[:20]:  # Show max 20
        status_emoji = "✅" if h["status"] == "approved" else "❌"
        text += (
            f"{status_emoji} **{h['plan']}** — {h['price']}\n"
            f"  User: `{h['user_id']}` | {h['days']} days\n"
            f"  ID: `{h['request_id']}`\n\n"
        )

    await message.reply(text)

# ===========================================================================
#   CALLBACK HANDLERS
# ===========================================================================


@bot.on_callback_query(filters.regex("^pay_"))
async def payment_callbacks(client, callback: CallbackQuery):
    """Handle payment callback queries.

    Args:
        client: Bot client
        callback: Callback query

    Returns:
        None

    Callbacks:
        pay_now, pay_methods, pay_upi, pay_paypal,
        pay_crypto, pay_bank, pay_screenshot
    """
    data = callback.data

    if data == "pay_now":
        text = "**💳 Choose Plan**\n\n"
        for key, plan in PREMIUM_PLANS.items():
            text += f"{plan['emoji']} **{plan['name']}** — {plan['price']}\n"
        text += "\n**Usage:** `/pay <plan>`"
        await callback.message.edit_text(text)

    elif data == "pay_methods":
        text = "**💳 Payment Methods**\n\n"
        for key, method in PAYMENT_METHODS.items():
            text += f"{method['emoji']} **{method['name']}**\n"
            text += f"  {method['details']}\n\n"
        await callback.message.edit_text(text)

    elif data == "pay_upi":
        await callback.answer(
            f"**📱 UPI Payment**\n\n"
            f"Send to: `telegramdl@upi`\n"
            f"Take screenshot and send to admin",
            show_alert=True
        )

    elif data == "pay_paypal":
        await callback.answer(
            f"**💳 PayPal Payment**\n\n"
            f"Send to: `paypal.me/telegramdl`\n"
            f"Take screenshot and send to admin",
            show_alert=True
        )

    elif data == "pay_crypto":
        await callback.answer(
            f"**₿ Crypto Payment**\n\n"
            f"Send USDT (TRC20) to:\n"
            f"`TN3Vj8qXxZQ1nH9pLmK4rT6wY2bS7dF8g`\n"
            f"Send transaction ID to admin",
            show_alert=True
        )

    elif data == "pay_bank":
        await callback.answer(
            f"**🏦 Bank Transfer**\n\n"
            f"Contact admin for bank details:\n"
            f"{ADMIN_CONTACT}",
            show_alert=True
        )

    elif data == "pay_screenshot":
        await callback.message.edit_text(
            "**📸 Send Payment Screenshot**\n\n"
            f"1. Take screenshot of payment\n"
            f"2. Send to admin: {ADMIN_CONTACT}\n"
            f"3. Include your user ID: `{callback.from_user.id}`\n\n"
            f"**Or forward payment confirmation here**"
        )

    await callback.answer()

# ===========================================================================
#   END OF PAYMENT PLUGIN
# ===========================================================================
