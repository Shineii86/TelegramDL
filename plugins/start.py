from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
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
    thumbnail_keyboard, caption_keyboard, myplan_keyboard,
    login_keyboard, help_keyboard, back_keyboard,
    WELCOME_MSG, HELP_DOWNLOAD, HELP_BACKUP, HELP_BATCH, HELP_LOGIN,
    HELP_THUMBNAIL, HELP_CAPTION, HELP_SETTINGS, HELP_FORMATS,
    SETTINGS_INFO, MYPLAN_INFO, THUMBNAIL_SET, THUMBNAIL_DELETED,
    CAPTION_SET, CAPTION_DELETED
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


@bot.on_message(filters.command("login") & filters.private)
async def login_cmd(client, message: Message):
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


@bot.on_message(filters.command("myplan") & filters.private)
async def myplan_cmd(client, message: Message):
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


# ============ THUMBNAIL COMMANDS ============

@bot.on_message(filters.command("set_thumb") & filters.private)
async def set_thumb_cmd(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("**Reply to a photo** to set as your thumbnail.")
        return
    file_id = message.reply_to_message.photo.file_id
    await db.set_thumbnail(message.from_user.id, file_id)
    await message.reply(THUMBNAIL_SET)


@bot.on_message(filters.command("view_thumb") & filters.private)
async def view_thumb_cmd(client, message: Message):
    file_id = await db.get_thumbnail(message.from_user.id)
    if file_id:
        await message.reply_photo(file_id, caption="**Your current thumbnail:**")
    else:
        await message.reply("No custom thumbnail set.")


@bot.on_message(filters.command("del_thumb") & filters.private)
async def del_thumb_cmd(client, message: Message):
    await db.delete_thumbnail(message.from_user.id)
    await message.reply(THUMBNAIL_DELETED)


# ============ CAPTION COMMANDS ============

@bot.on_message(filters.command("set_caption") & filters.private)
async def set_caption_cmd(client, message: Message):
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
    caption = await db.get_caption(message.from_user.id)
    if caption:
        await message.reply(f"**Your current caption:**\n\n`{caption}`")
    else:
        await message.reply("No custom caption set.")


@bot.on_message(filters.command("del_caption") & filters.private)
async def del_caption_cmd(client, message: Message):
    await db.delete_caption(message.from_user.id)
    await message.reply(CAPTION_DELETED)


# ============ ADMIN COMMANDS ============

@bot.on_message(filters.command("ban") & filters.private)
async def ban_cmd(client, message: Message):
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
        await callback.answer()

    elif data in ("dl_filter_photo", "dl_filter_video", "dl_filter_audio", "dl_filter_all"):
        filter_type = data.split("_")[-1]
        await callback.answer(f"Type filter set to: {filter_type}", show_alert=True)


@bot.on_callback_query(filters.regex("^bk_"))
async def backup_callbacks(client, callback: CallbackQuery):
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


@bot.on_callback_query(filters.regex("^thumb_"))
async def thumbnail_callbacks(client, callback: CallbackQuery):
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
    else:
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
