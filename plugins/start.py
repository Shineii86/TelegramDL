from pyrogram import filters
from pyrogram.types import Message
from bot import bot, user_client
from database.db import db
from config import ADMINS, LOGIN_SYSTEM

WELCOME = """
**Welcome to TelegramDL Bot!**

Download restricted content from Telegram channels.

**Commands:**
/start - Start the bot
/help - Show help message
/login - Login with your phone number
/logout - Logout from your session
/batch <channel_url> - Batch download all media
/backup <channel_url> - Backup channel to backup channel
/cancel - Cancel ongoing download

**Usage:**
Just send a Telegram message link and the bot will download it.

**Supported formats:**
- `https://t.me/username/123`
- `https://t.me/username/1001-1010` (batch)
- `https://t.me/c/1234567890/123`
- `https://t.me/+invitehash`
- Forward a message to the bot
"""


@bot.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, name)

    await message.reply(WELCOME)


@bot.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message: Message):
    await message.reply(WELCOME)


@bot.on_message(filters.command("login") & filters.private)
async def login(client, message: Message):
    if not LOGIN_SYSTEM:
        await message.reply("Login system is disabled. Bot uses a global session.")
        return

    user_id = message.from_user.id
    await message.reply(
        "**Login Process**\n\n"
        "Send your API ID (get it from https://my.telegram.org)\n"
        "Or send /skip to use bot's own API ID (not recommended)."
    )

    try:
        response = await client.ask(
            chat_id=user_id,
            text="Send your API ID or /skip:",
            filters=filters.text,
            timeout=120
        )

        if response.text and response.text.startswith("/skip"):
            from config import API_ID, API_HASH
            api_id = API_ID
            api_hash = API_HASH
        else:
            api_id = int(response.text.strip())

            response2 = await client.ask(
                chat_id=user_id,
                text="Send your API Hash:",
                filters=filters.text,
                timeout=120
            )
            api_hash = response2.text.strip()

        response3 = await client.ask(
            chat_id=user_id,
            text="Send your phone number (with country code, e.g. +1234567890):",
            filters=filters.text,
            timeout=120
        )
        phone = response3.text.strip()

        from pyrogram import Client as PyrogramClient
        temp_client = PyrogramClient(":memory:", api_id=api_id, api_hash=api_hash)
        await temp_client.start()

        code = await temp_client.send_code(phone)
        response4 = await client.ask(
            chat_id=user_id,
            text=f"Sent code to {phone}. Send the code (format: 1 2 3 4 5):",
            filters=filters.text,
            timeout=120
        )
        code_str = response4.text.strip().replace(" ", "")

        try:
            await temp_client.sign_in(phone, code.phone_code_hash, code_str)
        except Exception:
            password = await client.ask(
                chat_id=user_id,
                text="Two-step verification enabled. Send your password:",
                filters=filters.text,
                timeout=120
            )
            await temp_client.check_password(password.text.strip())

        session_string = await temp_client.export_session_string()
        await temp_client.stop()

        if len(session_string) < 351:
            await message.reply("Invalid session string generated. Try again.")
            return

        await db.set_session(user_id, session_string)
        await message.reply("**Login successful!** Session saved.")

    except Exception as e:
        await message.reply(f"Login failed: {e}")


@bot.on_message(filters.command("logout") & filters.private)
async def logout(client, message: Message):
    user_id = message.from_user.id
    await db.set_session(user_id, None)
    await message.reply("Logged out successfully.")


@bot.on_message(filters.command("cancel") & filters.private)
async def cancel(client, message: Message):
    from plugins.generate import IS_BATCH
    user_id = message.from_user.id
    IS_BATCH[user_id] = True
    await message.reply("Download cancelled.")
