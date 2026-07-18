import os
import logging
from pyrogram import Client

from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global user client for restricted content (when LOGIN_SYSTEM=false)
user_client = None

if not LOGIN_SYSTEM and STRING_SESSION:
    try:
        user_client = Client(
            "user_session",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=STRING_SESSION
        )
        logger.info("User client initialized from STRING_SESSION")
    except Exception as e:
        logger.error(f"Failed to initialize user client: {e}")
        user_client = None


class Bot(Client):
    def __init__(self):
        super().__init__(
            "telegramdl_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=150,
            sleep_threshold=5
        )


bot = Bot()


async def start_user_client():
    global user_client
    if user_client and not user_client.is_connected:
        await user_client.start()
        logger.info("User client started")


async def stop_user_client():
    global user_client
    if user_client and user_client.is_connected:
        await user_client.stop()
        logger.info("User client stopped")


def main():
    os.makedirs("downloads", exist_ok=True)
    logger.info("Starting TelegramDL Bot...")
    bot.run()


if __name__ == "__main__":
    main()
