import os
import time
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from bot import bot, user_client
from database.db import db
from config import ADMINS, LOGIN_SYSTEM, OUTPUT_DIR, WAITING_TIME, MAX_FILE_SIZE_MB, TYPE_FILTER, CAPTION_ENABLED, FORWARD_MODE, USE_CHECKPOINT, KEEP_ALIVE
from utils.ui import (
    main_menu_keyboard, download_keyboard, backup_keyboard, batch_keyboard,
    settings_keyboard, settings_delay_keyboard, settings_size_keyboard,
    login_keyboard, help_keyboard, back_keyboard,
    WELCOME_MSG, HELP_DOWNLOAD, HELP_BACKUP, HELP_BATCH, HELP_LOGIN,
    HELP_SETTINGS, HELP_FORMATS, SETTINGS_INFO
)


@bot.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, name)

    await message.reply(WELCOME_MSG, reply_markup=main_menu_keyboard())


@bot.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message: Message):
    await message.reply("**❓ Help Menu**\n\nChoose a topic:", reply_markup=help_keyboard())


@bot.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message: Message):
    text = SETTINGS_INFO.format(
        delay=WAITING_TIME,
        size=MAX_FILE_SIZE_MB,
        type_filter=TYPE_FILTER,
        captions="ON" if CAPTION_ENABLED else "OFF",
        forward="ON" if FORWARD_MODE else "OFF",
        checkpoint="ON" if USE_CHECKPOINT else "OFF",
    )
    await message.reply(text, reply_markup=settings_keyboard())


@bot.on_message(filters.command("login") & filters.private)
async def login_cmd(client, message: Message):
    if not LOGIN_SYSTEM:
        await message.reply("Login system is disabled. Bot uses a global session.")
        return
    await message.reply("**🔐 Login**\n\nChoose an option:", reply_markup=login_keyboard())


@bot.on_message(filters.command("logout") & filters.private)
async def logout_cmd(client, message: Message):
    user_id = message.from_user.id
    await db.set_session(user_id, None)
    await message.reply("**Logged out successfully!** Session removed.")


@bot.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client, message: Message):
    from plugins.generate import IS_BATCH
    user_id = message.from_user.id
    IS_BATCH[user_id] = True
    await message.reply("**Download cancelled.**")


@bot.on_message(filters.command("batch") & filters.private)
async def batch_cmd(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**📦 Batch Download**\n\n"
            "Usage: `/batch <channel_url>`\n\n"
            "Downloads all media from a channel.",
            reply_markup=batch_keyboard()
        )
        return


@bot.on_message(filters.command("backup") & filters.private)
async def backup_cmd(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**☁️ Backup**\n\n"
            "Usage: `/backup <channel_url>`\n\n"
            "Backs up channel to a backup channel.",
            reply_markup=backup_keyboard()
        )
        return


# ============ CALLBACK HANDLERS ============

@bot.on_callback_query(filters.regex("^menu_"))
async def menu_callbacks(client, callback: CallbackQuery):
    data = callback.data

    if data == "menu_back":
        await callback.message.edit_text(WELCOME_MSG, reply_markup=main_menu_keyboard())

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
        text = SETTINGS_INFO.format(
            delay=WAITING_TIME,
            size=MAX_FILE_SIZE_MB,
            type_filter=TYPE_FILTER,
            captions="ON" if CAPTION_ENABLED else "OFF",
            forward="ON" if FORWARD_MODE else "OFF",
            checkpoint="ON" if USE_CHECKPOINT else "OFF",
        )
        await callback.message.edit_text(text, reply_markup=settings_keyboard())

    elif data == "menu_help":
        await callback.message.edit_text("**❓ Help Menu**\n\nChoose a topic:", reply_markup=help_keyboard())

    await callback.answer()


@bot.on_callback_query(filters.regex("^dl_"))
async def download_callbacks(client, callback: CallbackQuery):
    data = callback.data

    if data == "dl_send_link":
        await callback.message.edit_text(
            "**📥 Download**\n\nSend me a Telegram message link:\n\n"
            "Example: `https://t.me/username/123`"
        )

    elif data in ("dl_filter_photo", "dl_filter_video", "dl_filter_audio", "dl_filter_all"):
        filter_type = data.split("_")[-1]
        if filter_type == "all":
            filter_type = "all"
        await callback.answer(f"Type filter set to: {filter_type}", show_alert=True)

    await callback.answer()


@bot.on_callback_query(filters.regex("^bk_"))
async def backup_callbacks(client, callback: CallbackQuery):
    data = callback.data

    if data == "bk_send_link":
        await callback.message.edit_text(
            "**☁️ Backup**\n\nSend me a channel link to backup:\n\n"
            "Example: `https://t.me/username`"
        )

    elif data == "bk_mode_bot":
        await callback.answer("Bot upload mode selected!", show_alert=True)

    elif data == "bk_mode_user":
        await callback.answer("User upload mode selected!", show_alert=True)

    await callback.answer()


@bot.on_callback_query(filters.regex("^batch_"))
async def batch_callbacks(client, callback: CallbackQuery):
    data = callback.data

    if data == "batch_send_link":
        await callback.message.edit_text(
            "**📦 Batch Download**\n\n"
            "Send me a channel link with message range:\n\n"
            "Example: `https://t.me/username/1001-1010`"
        )

    elif data == "batch_forward":
        await callback.answer("Forward mode selected (faster)!", show_alert=True)

    elif data == "batch_download":
        await callback.answer("Download mode selected!", show_alert=True)

    await callback.answer()


@bot.on_callback_query(filters.regex("^set_"))
async def settings_callbacks(client, callback: CallbackQuery):
    data = callback.data

    if data == "set_delay":
        await callback.message.edit_text(
            "**⏱ Set Delay**\n\nChoose delay between downloads:",
            reply_markup=settings_delay_keyboard()
        )

    elif data == "set_size":
        await callback.message.edit_text(
            "**📏 Set Max File Size**\n\nChoose file size limit:",
            reply_markup=settings_size_keyboard()
        )

    elif data == "set_type":
        await callback.answer("Send /batch <link> to download", show_alert=True)

    elif data == "set_captions":
        await callback.answer("Captions: ON", show_alert=True)

    elif data == "set_forward":
        await callback.answer("Forward mode: ON", show_alert=True)

    elif data == "set_checkpoint":
        await callback.answer("Checkpoint: ON", show_alert=True)

    await callback.answer()


@bot.on_callback_query(filters.regex("^delay_"))
async def delay_callbacks(client, callback: CallbackQuery):
    delay = callback.data.split("_")[1]
    await callback.answer(f"Delay set to {delay}s!", show_alert=True)
    await callback.message.edit_text(
        f"**✅ Delay Updated**\n\nNew delay: **{delay}** seconds",
        reply_markup=back_keyboard("menu_settings")
    )


@bot.on_callback_query(filters.regex("^size_"))
async def size_callbacks(client, callback: CallbackQuery):
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


@bot.on_callback_query(filters.regex("^help_"))
async def help_callbacks(client, callback: CallbackQuery):
    data = callback.data

    if data == "help_download":
        await callback.message.edit_text(HELP_DOWNLOAD, reply_markup=back_keyboard("menu_help"))
    elif data == "help_backup":
        await callback.message.edit_text(HELP_BACKUP, reply_markup=back_keyboard("menu_help"))
    elif data == "help_batch":
        await callback.message.edit_text(HELP_BATCH, reply_markup=back_keyboard("menu_help"))
    elif data == "help_login":
        await callback.message.edit_text(HELP_LOGIN, reply_markup=back_keyboard("menu_help"))
    elif data == "help_settings":
        await callback.message.edit_text(HELP_SETTINGS, reply_markup=back_keyboard("menu_help"))
    elif data == "help_formats":
        await callback.message.edit_text(HELP_FORMATS, reply_markup=back_keyboard("menu_help"))

    await callback.answer()


@bot.on_callback_query(filters.regex("^login_"))
async def login_callbacks(client, callback: CallbackQuery):
    data = callback.data

    if data == "login_start":
        await callback.message.edit_text(
            "**🔐 Login Process**\n\n"
            "Send your **API ID** (from my.telegram.org)\n"
            "Or send /skip to use bot's API ID."
        )

    await callback.answer()


@bot.on_callback_query(filters.regex("^logout_"))
async def logout_callbacks(client, callback: CallbackQuery):
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
    data = callback.data
    parts = data.split("_")

    if len(parts) >= 2:
        action = parts[1]
        await callback.answer(f"Confirmed: {action}", show_alert=True)

    await callback.answer()


@bot.on_callback_query(filters.regex("^cancel_"))
async def cancel_callbacks(client, callback: CallbackQuery):
    data = callback.data
    action = data.replace("cancel_", "")
    await callback.answer(f"Cancelled: {action}", show_alert=True)
    await callback.message.edit_text("**❌ Cancelled**", reply_markup=back_keyboard())


@bot.on_callback_query(filters.regex("^stop_"))
async def stop_callbacks(client, callback: CallbackQuery):
    from plugins.generate import IS_BATCH
    user_id = callback.from_user.id
    IS_BATCH[user_id] = True
    await callback.answer("Stopping...", show_alert=True)
    await callback.message.edit_text("**⏹ Stopping...**\nProcess will stop after current file.")
