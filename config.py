from os import environ

# Telegram API Credentials
API_ID = int(environ.get("API_ID", "0"))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# User session for restricted content access
STRING_SESSION = environ.get("STRING_SESSION", "")
LOGIN_SYSTEM = environ.get("LOGIN_SYSTEM", "true").lower() == "true"

# Database
DB_URI = environ.get("DB_URI", "")
DB_NAME = environ.get("DB_NAME", "telegramdl")

# Bot settings
ADMINS_RAW = environ.get("ADMINS", "")
ADMINS = [int(x.strip()) for x in ADMINS_RAW.split(",") if x.strip().isdigit()] if ADMINS_RAW else []
CHANNEL_ID = environ.get("CHANNEL_ID", "")
WAITING_TIME = int(environ.get("WAITING_TIME", "10"))
ERROR_MESSAGE = environ.get("ERROR_MESSAGE", "true").lower() == "true"

# Download settings
OUTPUT_DIR = environ.get("OUTPUT_DIR", "./downloads")
MAX_FILE_SIZE_MB = int(environ.get("MAX_FILE_SIZE_MB", "2048"))
TYPE_FILTER = environ.get("TYPE_FILTER", "all")
PARALLEL_DOWNLOADS = int(environ.get("PARALLEL_DOWNLOADS", "3"))

# Backup settings
BACKUP_TO_TELEGRAM = environ.get("BACKUP_TO_TELEGRAM", "true").lower() == "true"
FORWARD_MODE = environ.get("FORWARD_MODE", "true").lower() == "true"
BACKUP_CHANNEL = environ.get("BACKUP_CHANNEL", "")

# Caption settings
CAPTION_ENABLED = environ.get("CAPTION_ENABLED", "true").lower() == "true"
KEEP_ORIGINAL_CAPTION = environ.get("KEEP_ORIGINAL_CAPTION", "true").lower() == "true"

# Colab settings
KEEP_ALIVE = environ.get("KEEP_ALIVE", "true").lower() == "true"
KEEP_ALIVE_INTERVAL = int(environ.get("KEEP_ALIVE_INTERVAL", "30"))
USE_CHECKPOINT = environ.get("USE_CHECKPOINT", "true").lower() == "true"
SESSION_LIMIT_HOURS = int(environ.get("SESSION_LIMIT_HOURS", "12"))
