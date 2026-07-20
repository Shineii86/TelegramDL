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
        UI components: inline keyboards and message templates.

    KEYBOARDS:
        main_menu_keyboard — Main menu
        download_keyboard  — Download options
        backup_keyboard    — Backup options
        batch_keyboard     — Batch options
        settings_keyboard  — Settings menu
        settings_delay_keyboard — Delay selection
        settings_size_keyboard  — Size selection
        thumbnail_keyboard — Thumbnail management
        caption_keyboard   — Caption management
        myplan_keyboard    — Plan info
        about_keyboard     — About links
        help_keyboard      — Help topics
        login_keyboard     — Login/logout
        back_keyboard      — Back navigation
        stop_keyboard      — Stop button

    MESSAGES:
        WELCOME_MSG, HELP_*, SETTINGS_INFO, MYPLAN_INFO,
        PROGRESS_MSG, BACKUP_*, THUMBNAIL_*, CAPTION_*,
        ABOUT_MSG, PROJECT_MSG, DEV_MSG
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ===========================================================================
#   KEYBOARD BUILDERS
# ---------------------------------------------------------------------------
#   Each function returns InlineKeyboardMarkup with buttons
#   All buttons use callback_data for routing
# ===========================================================================


def main_menu_keyboard():
    """Main menu keyboard.

    Returns:
        InlineKeyboardMarkup: 5 rows of buttons

    Buttons:
        Download, Backup, Batch, Login,
        Settings, My Plan, Thumbnail, Caption,
        About, Help
    """
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
            InlineKeyboardButton("👤 My Plan", callback_data="menu_myplan"),
        ],
        [
            InlineKeyboardButton("🖼 Thumbnail", callback_data="menu_thumbnail"),
            InlineKeyboardButton("📝 Caption", callback_data="menu_caption"),
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="menu_about"),
            InlineKeyboardButton("❓ Help", callback_data="menu_help"),
        ],
    ])


def download_keyboard():
    """Download options keyboard.

    Returns:
        InlineKeyboardMarkup: Filter options and back button
    """
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
    """Backup options keyboard.

    Returns:
        InlineKeyboardMarkup: Upload mode options
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📎 Send Channel Link", callback_data="bk_send_link")],
        [
            InlineKeyboardButton("🤖 Bot Upload", callback_data="bk_mode_bot"),
            InlineKeyboardButton("👤 User Upload", callback_data="bk_mode_user"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def batch_keyboard():
    """Batch download options keyboard.

    Returns:
        InlineKeyboardMarkup: Mode options
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📎 Send Channel Link", callback_data="batch_send_link")],
        [
            InlineKeyboardButton("⏭ Forward Mode", callback_data="batch_forward"),
            InlineKeyboardButton("📥 Download Mode", callback_data="batch_download"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def settings_keyboard():
    """Settings menu keyboard.

    Returns:
        InlineKeyboardMarkup: Setting options
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱ Delay", callback_data="set_delay"),
            InlineKeyboardButton("📏 File Size", callback_data="set_size"),
        ],
        [
            InlineKeyboardButton("🏷 Type Filter", callback_data="set_type"),
            InlineKeyboardButton("🔄 Forward Mode", callback_data="set_forward"),
        ],
        [
            InlineKeyboardButton("💾 Checkpoint", callback_data="set_checkpoint"),
            InlineKeyboardButton("📢 Dump Chat", callback_data="set_dump"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def settings_delay_keyboard():
    """Delay selection keyboard.

    Returns:
        InlineKeyboardMarkup: Delay options (3s to 30s)
    """
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
    """File size selection keyboard.

    Returns:
        InlineKeyboardMarkup: Size options (500MB to No Limit)
    """
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


def thumbnail_keyboard():
    """Thumbnail management keyboard.

    Returns:
        InlineKeyboardMarkup: Set/View/Delete options
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="thumb_set")],
        [
            InlineKeyboardButton("👁 View Thumbnail", callback_data="thumb_view"),
            InlineKeyboardButton("🗑 Delete Thumbnail", callback_data="thumb_delete"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def caption_keyboard():
    """Caption management keyboard.

    Returns:
        InlineKeyboardMarkup: Set/View/Delete options
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Set Caption", callback_data="caption_set")],
        [
            InlineKeyboardButton("👁 View Caption", callback_data="caption_view"),
            InlineKeyboardButton("🗑 Delete Caption", callback_data="caption_delete"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def myplan_keyboard():
    """Plan info keyboard.

    Returns:
        InlineKeyboardMarkup: Stats button
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 My Stats", callback_data="plan_stats")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def confirm_keyboard(action, target_id=""):
    """Confirmation keyboard.

    Args:
        action: Action name
        target_id: Target ID (optional)

    Returns:
        InlineKeyboardMarkup: Confirm/Cancel buttons
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{target_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{action}"),
        ],
    ])


def progress_keyboard():
    """Progress cancel keyboard.

    Returns:
        InlineKeyboardMarkup: Cancel button
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_download")],
    ])


def stop_keyboard():
    """Stop process keyboard.

    Returns:
        InlineKeyboardMarkup: Stop button
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏹ Stop", callback_data="stop_process")],
    ])


def help_keyboard():
    """Help topics keyboard.

    Returns:
        InlineKeyboardMarkup: Help topic buttons
    """
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
            InlineKeyboardButton("🖼 Thumbnail", callback_data="help_thumbnail"),
            InlineKeyboardButton("📝 Caption", callback_data="help_caption"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_settings"),
            InlineKeyboardButton("🔗 Formats", callback_data="help_formats"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def login_keyboard():
    """Login/logout keyboard.

    Returns:
        InlineKeyboardMarkup: Login/Logout buttons
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Login with Phone", callback_data="login_start")],
        [InlineKeyboardButton("🚪 Logout", callback_data="logout_confirm")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])


def back_keyboard(target="menu_back"):
    """Back navigation keyboard.

    Args:
        target: Callback data for back button

    Returns:
        InlineKeyboardMarkup: Back button
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=target)],
    ])


def about_keyboard():
    """About page keyboard.

    Returns:
        InlineKeyboardMarkup: External links
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Shineii86")],
        [InlineKeyboardButton("📂 GitHub", url="https://github.com/Shineii86/TelegramDL")],
        [
            InlineKeyboardButton("📢 Updates Channel", url="https://t.me/Shineii86"),
            InlineKeyboardButton("💬 Support Group", url="https://t.me/Shineii86"),
        ],
        [InlineKeyboardButton("⭐ Star on GitHub", url="https://github.com/Shineii86/TelegramDL")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_back")],
    ])

# ===========================================================================
#   MESSAGE TEMPLATES
# ---------------------------------------------------------------------------
#   All user-facing messages as constants
# ===========================================================================


WELCOME_MSG = """
┌─────────────────────────────────┐
│    🤖 **TelegramDL Bot** v{version}   │
└─────────────────────────────────┘

📥 Download restricted content from **channels, groups, bots & stories**

> 💡 **How it works:**
> Send any Telegram link → Bot downloads → Files sent to you

┌─────────────── **Quick Start** ───────────────┐
│                                               │
│  1️⃣  Send a Telegram link or username          │
│  2️⃣  Bot downloads the content                │
│  3️⃣  Files delivered to you here              │
│                                               │
└───────────────────────────────────────────────┘

🔗 **Supported:** Channels · Groups · Bots · Stories · Invite Links

⚡ Use the buttons below to navigate
"""


HELP_DOWNLOAD = """
┌─────────────────────────────────┐
│    📥 **Download Help**          │
└─────────────────────────────────┘

> Send any Telegram link or username to download

┌────────── **Supported Formats** ──────────┐
│                                           │
│  📢 **Public Channel**                    │
│     `t.me/username/123`                   │
│                                           │
│  🔒 **Private Channel**                   │
│     `t.me/c/1234567890/123`               │
│                                           │
│  📖 **Story**                             │
│     `t.me/username/s/123`                 │
│                                           │
│  📦 **Batch Range**                       │
│     `t.me/username/1001-1010`             │
│                                           │
│  🤖 **Bot Chat**                          │
│     `t.me/b/botusername/123`              │
│                                           │
│  🔗 **Invite Link**                       │
│     `t.me/+invitehash`                    │
│                                           │
│  👥 **Group**                             │
│     `t.me/groupname/123`                  │
│                                           │
│  🆔 **Numeric ID**                        │
│     `-1001234567890/123`                  │
│                                           │
└───────────────────────────────────────────┘

> 💡 For bot chats, use Plus Messenger to get message ID
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
2. Enter phone number
3. Enter OTP code
"""


HELP_THUMBNAIL = """
**🖼 Thumbnail Help**

Set a custom thumbnail for your uploads.

**Commands:**
- `/set_thumb` — Reply to a photo to set as thumbnail
- `/view_thumb` — View your current thumbnail
- `/del_thumb` — Delete your thumbnail

**Note:** Custom thumbnail is used for all your uploads. If not set, original thumbnail is used.
"""


HELP_CAPTION = """
**📝 Caption Help**

Set a custom caption for your uploads.

**Commands:**
- `/set_caption <text>` — Set custom caption
- `/view_caption` — View your current caption
- `/del_caption` — Delete your caption

**Placeholders:**
- `{filename}` — Original filename
- `{size}` — File size
- `{date}` — Upload date

**Example:** `📁 {filename} | Size: {size} | Date: {date}`
"""


HELP_SETTINGS = """
**⚙️ Settings Help**

Adjust bot behavior:

- **Delay** — Time between downloads (flood protection)
- **File Size** — Max file size limit
- **Type Filter** — Download only specific media
- **Forward Mode** — Use forwarding (faster)
- **Checkpoint** — Save progress for resume
- **Dump Chat** — Auto-forward downloads to a channel
"""


HELP_FORMATS = """
**🔗 All Supported Formats**

**Channels:**
- `t.me/username/123` — Public channel
- `t.me/c/1234567890/123` — Private channel
- `t.me/+invitehash` — Invite link
- `t.me/joinchat/hash` — Old invite format

**Stories:**
- `t.me/username/s/123` — Download story

**Groups & Supergroups:**
- `t.me/groupname/123` — Public group
- `t.me/c/GROUP_ID/123` — Private group
- `-1001234567890/123` — Numeric group ID

**Bots:**
- `t.me/b/botusername/123` — Bot chat
- `t.me/b/botusername` — Bot chat (no specific message)
- `t.me/botusername` — Bot link

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
**Forward Mode:** {forward}
**Checkpoint:** {checkpoint}
**Dump Chat:** {dump_chat}
"""


MYPLAN_INFO = """
┌─────────────────────────────────┐
│    👤 **My Plan**                │
└─────────────────────────────────┘

┌─────────── **Status** ───────────┐
│ 🏷️ **Plan:** {plan_type}          │
│ 📅 **Expires:** {expiry}          │
└──────────────────────────────────┘

┌─────────── **Usage** ────────────┐
│ 📊 **Today:** `{daily_used}/{daily_limit}` │
│ 💾 **Total:** `{total_saves}` saved        │
└──────────────────────────────────┘

┌─────────── **Limits** ───────────┐
│ 🆓 **Free:** {daily_limit}/day, {free_size}MB  │
│ ⭐ **Premium:** Unlimited, {premium_size}MB    │
└──────────────────────────────────┘

💡 Upgrade with `/premium` for unlimited access!
"""


PROGRESS_MSG = """
📥 **Downloading...**

`[{bar}]` **{percent}%**

┌─────────── **Stats** ───────────┐
│ ⚡ **Speed:** `{speed}/s`         │
│ ✅ **Done:** `{done}/{total}`     │
│ ❌ **Failed:** `{failed}`         │
│ ⏳ **Remaining:** `{remaining}`   │
└──────────────────────────────────┘

⏱ **Elapsed:** `{elapsed}`
📡 **ETA:** `{eta}`

📄 `{current}`
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


THUMBNAIL_SET = """
**🖼 Thumbnail Updated!**

Your custom thumbnail has been set.
All future uploads will use this thumbnail.
"""


THUMBNAIL_DELETED = """
**🗑 Thumbnail Deleted!**

Your custom thumbnail has been removed.
Original thumbnails will be used.
"""


CAPTION_SET = """
**📝 Caption Updated!**

Your custom caption has been set.
**Preview:** {caption}

**Placeholders:**
- `{{filename}}` — Original filename
- `{{size}}` — File size
- `{{date}}` — Upload date
"""


CAPTION_DELETED = """
**🗑 Caption Deleted!**

Your custom caption has been removed.
Original captions will be used.
"""


ABOUT_MSG = """
┌─────────────────────────────────┐
│    ℹ️ **About TelegramDL**       │
└─────────────────────────────────┘

> 📦 **Version:** `{version}`
> 📚 **Library:** Kurigram (Pyrogram Fork)
> 👨‍💻 **Developer:** [@Shineii86](https://t.me/Shineii86)

┌─────────────── **Features** ───────────────┐
│                                             │
│  📥 Download restricted content             │
│  📦 Batch download with progress bar        │
│  🖼 Custom thumbnails per user              │
│  📝 Custom captions with placeholders       │
│  ⭐ Premium system with daily limits        │
│  📢 Dump chat auto-forward                  │
│  🎬 yt-dlp (YouTube, Instagram, TikTok)     │
│  🔐 Secure login system                     │
│                                             │
└─────────────────────────────────────────────┘

┌─────────── **Supported Content** ───────────┐
│                                             │
│  ✅ Public & Private Channels               │
│  ✅ Groups & Supergroups                    │
│  ✅ Bot Chats                               │
│  ✅ Stories                                 │
│  ✅ Invite Links                            │
│  ✅ YouTube, Instagram, Facebook, TikTok    │
│                                             │
└─────────────────────────────────────────────┘

🔗 **Stats:** `11+ link formats` · `Rich progress bar` · `Checkpoint resume`

💡 Built with ❤️ by [@Shineii86](https://t.me/Shineii86)
📂 Source: [GitHub](https://github.com/Shineii86/TelegramDL)
"""


PROJECT_MSG = """
┌─────────────────────────────────┐
│    📂 **TelegramDL Project**     │
└─────────────────────────────────┘

> Open-source Telegram downloader bot built with Kurigram

┌─────────── **What It Does** ──────────┐
│                                       │
│  Download any content from Telegram:  │
│  • Channels (public & private)        │
│  • Groups & Supergroups               │
│  • Bot Chats                          │
│  • Stories                            │
│  • Even restricted content!           │
│                                       │
└───────────────────────────────────────┘

┌─────────── **How It Works** ──────────┐
│                                       │
│  1️⃣  User logs in with phone number   │
│  2️⃣  Bot uses session to access       │
│  3️⃣  Content re-uploaded to user      │
│                                       │
└───────────────────────────────────────┘

┌─────────── **Tech Stack** ────────────┐
│                                       │
│  🐍 **Language:** Python 3.10+        │
│  📚 **Library:** Kurigram             │
│  🗄️ **Database:** MongoDB (Motor)     │
│  🚀 **Deploy:** Colab, Docker, VPS    │
│                                       │
└───────────────────────────────────────┘

> 🆓 **Free to use** · **Free to modify** · **Free to deploy**
> 📜 **License:** MIT
"""


DEV_MSG = """
┌─────────────────────────────────┐
│    👨‍💻 **Developer**              │
└─────────────────────────────────┘

> 📛 **Name:** Shinei Nouzen
> 🆔 **Username:** [@Shineii86](https://t.me/Shineii86)
> 💻 **GitHub:** [Shineii86](https://github.com/Shineii86)

┌─────────── **Projects** ───────────┐
│                                    │
│  🤖 TelegramDL — Download bot     │
│  📦 More coming soon...           │
│                                    │
└────────────────────────────────────┘

┌─────────── **Contact** ────────────┐
│                                    │
│  📱 Telegram: [@Shineii86](https://t.me/Shineii86)  │
│  🐛 Issues: [Report Bug](https://github.com/Shineii86/TelegramDL/issues) │
│                                    │
└────────────────────────────────────┘

> ⭐ If you like this bot, star the repo on GitHub!
"""

# ===========================================================================
#   END OF UI MODULE
# ===========================================================================
