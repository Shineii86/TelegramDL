from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📥 Download", callback_data="menu_download"),
            InlineKeyboardButton("☁️ Backup", callback_data="menu_backup"),
        ],
        [
            InlineKeyboardButton("📦 Batch", callback_data="menu_batch"),
            InlineKeyboardButton("🔐 Login", callback_data="menu_login"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("❓ Help", callback_data="menu_help"),
        ],
    ])


def download_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📎 Send Link", callback_data="dl_send_link")],
        [
            InlineKeyboardButton("🖼 Photos Only", callback_data="dl_filter_photo"),
            InlineKeyboardButton("🎬 Videos Only", callback_data="dl_filter_video"),
        ],
        [
            InlineKeyboardButton("🎵 Audio Only", callback_data="dl_filter_audio"),
            InlineKeyboardButton("📄 All Media", callback_data="dl_filter_all"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def backup_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📎 Send Channel Link", callback_data="bk_send_link")],
        [
            InlineKeyboardButton("🤖 Bot Upload", callback_data="bk_mode_bot"),
            InlineKeyboardButton("👤 User Upload", callback_data="bk_mode_user"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def batch_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📎 Send Channel Link", callback_data="batch_send_link")],
        [
            InlineKeyboardButton("⏭ Forward Mode", callback_data="batch_forward"),
            InlineKeyboardButton("📥 Download Mode", callback_data="batch_download"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def settings_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱ Delay", callback_data="set_delay"),
            InlineKeyboardButton("📏 File Size", callback_data="set_size"),
        ],
        [
            InlineKeyboardButton("🏷 Type Filter", callback_data="set_type"),
            InlineKeyboardButton("📝 Captions", callback_data="set_captions"),
        ],
        [
            InlineKeyboardButton("🔄 Forward Mode", callback_data="set_forward"),
            InlineKeyboardButton("💾 Checkpoint", callback_data="set_checkpoint"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def settings_delay_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("3s", callback_data="delay_3"),
            InlineKeyboardButton("5s", callback_data="delay_5"),
            InlineKeyboardButton("10s", callback_data="delay_10"),
        ],
        [
            InlineKeyboardButton("15s", callback_data="delay_15"),
            InlineKeyboardButton("20s", callback_data="delay_20"),
            InlineKeyboardButton("30s", callback_data="delay_30"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_settings")],
    ])


def settings_size_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("500MB", callback_data="size_500"),
            InlineKeyboardButton("1GB", callback_data="size_1024"),
            InlineKeyboardButton("2GB", callback_data="size_2048"),
        ],
        [
            InlineKeyboardButton("5GB", callback_data="size_5120"),
            InlineKeyboardButton("10GB", callback_data="size_10240"),
            InlineKeyboardButton("No Limit", callback_data="size_0"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_settings")],
    ])


def confirm_keyboard(action, target_id=""):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{target_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{action}"),
        ],
    ])


def progress_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_download")],
    ])


def stop_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏹ Stop", callback_data="stop_process")],
    ])


def help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📥 Download", callback_data="help_download"),
            InlineKeyboardButton("☁️ Backup", callback_data="help_backup"),
        ],
        [
            InlineKeyboardButton("📦 Batch", callback_data="help_batch"),
            InlineKeyboardButton("🔐 Login", callback_data="help_login"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_settings"),
            InlineKeyboardButton("🔗 Formats", callback_data="help_formats"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def login_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Login with Phone", callback_data="login_start")],
        [InlineKeyboardButton("🚪 Logout", callback_data="logout_confirm")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def back_keyboard(target="menu_back"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=target)],
    ])


WELCOME_MSG = """
**Welcome to TelegramDL Bot!**

Download restricted content from Telegram channels, groups, and bots.

**How to use:**
1. Send a Telegram link or username
2. Bot downloads the content
3. Files sent to you here

**Supported:**
Channels · Groups · Supergroups · Bots
Public · Private · Invite Links
"""


HELP_DOWNLOAD = """
**📥 Download Help**

Send any Telegram link or username to download.

**Supported Formats:**

| Type | Format | Example |
|------|--------|---------|
| Public Channel | `t.me/username/123` | `t.me/durov/1` |
| Batch Range | `t.me/username/1001-1010` | `t.me/durov/1-50` |
| Private Channel | `t.me/c/1234567890/123` | `t.me/c/123456/1` |
| Invite Link | `t.me/+invitehash` | `t.me/+abc123` |
| Join Chat | `t.me/joinchat/hash` | `t.me/joinchat/xyz` |
| Group | `t.me/groupname/123` | `t.me/mygroup/1` |
| Supergroup | `t.me/groupname/123` | `t.me/supergroup/1` |
| Bot Link | `t.me/botusername` | `t.me/botfather` |
| Username Only | `username` | `durov` |
| Numeric ID | `-1001234567890/123` | `-1001234567890/1` |
| Forwarded | `t.me/c/123/456?single` | Auto-detected |

**How it works:**
1. Bot tries via bot token (public)
2. If restricted → uses your session
3. File sent to you

**Note:** For restricted content, use /login first.
"""


HELP_BACKUP = """
**☁️ Backup Help**

`/backup <channel_url>` — Backup channel to a new channel.

**Features:**
- Auto-creates backup channel
- Preserves captions
- Resume after disconnect
- Progress tracking
"""


HELP_BATCH = """
**📦 Batch Help**

`/batch <channel_url>` — Download all media from channel.

**Features:**
- Process message ID ranges
- Forward mode (fastest)
- Cancel anytime
- Progress bar with ETA
"""


HELP_LOGIN = """
**🔐 Login Help**

`/login` — Login with your phone number.

**Why login?**
- Access restricted channels
- Download private content
- Your session stays secure

**Steps:**
1. Click Login button
2. Enter API ID & Hash
3. Enter phone number
4. Enter OTP code
"""


HELP_SETTINGS = """
**⚙️ Settings Help**

Adjust bot behavior:

- **Delay** — Time between downloads (flood protection)
- **File Size** — Max file size limit
- **Type Filter** — Download only specific media
- **Captions** — Enable/disable captions
- **Forward Mode** — Use forwarding (faster)
- **Checkpoint** — Save progress for resume
"""


HELP_FORMATS = """
**🔗 All Supported Formats**

**Channels:**
- `t.me/username/123` — Public channel
- `t.me/c/1234567890/123` — Private channel
- `t.me/+invitehash` — Invite link
- `t.me/joinchat/hash` — Old invite format

**Groups & Supergroups:**
- `t.me/groupname/123` — Public group
- `t.me/c/GROUP_ID/123` — Private group
- `-1001234567890/123` — Numeric group ID

**Bots:**
- `t.me/botusername` — Bot link
- `@botusername` — Bot username

**Users:**
- `t.me/username` — User profile
- `username` — Plain username

**Batch:**
- `t.me/username/1001-1010` — ID range
"""


SETTINGS_INFO = """
**⚙️ Current Settings**

**Delay:** {delay}s between downloads
**File Size:** {size}MB max
**Type Filter:** {type_filter}
**Captions:** {captions}
**Forward Mode:** {forward}
**Checkpoint:** {checkpoint}
"""


PROGRESS_MSG = """
**📥 Downloading...**

`[{bar}]` **{percent}%**

**Total:** {total}
**Done:** {done}
**Failed:** {failed}
**Remaining:** {remaining}

**Elapsed:** {elapsed}
**ETA:** {eta}

**Current:** `{current}`
"""


BACKUP_START = """
**☁️ Starting Backup**

**Source:** `{channel}`
**Total:** {total} files

Processing...
"""


BACKUP_COMPLETE = """
**✅ Backup Complete!**

**Downloaded:** {downloaded}
**Skipped:** {skipped}
**Failed:** {failed}
**Total:** {total}
**Time:** {time}
"""
