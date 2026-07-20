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

from ftmgram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
> 📚 **Library:** ftmgram (Bot API 10.1)
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

> Open-source Telegram downloader bot built with ftmgram

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
│  📚 **Library:** ftmgram              │
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
#   RICH MESSAGE TEMPLATES (Bot API 10.1)
# ---------------------------------------------------------------------------
#   HTML-based rich messages for send_rich_message()
#   Use with ftmgram's InputRichMessage type
# ===========================================================================

from ftmgram.types import InputRichMessage


def WELCOME_RICH(version: str = "2.0.0") -> InputRichMessage:
    """Build welcome rich message with HTML formatting.

    Args:
        version: Bot version string

    Returns:
        InputRichMessage with styled welcome content
    """
    html = f"""
<h2>🤖 TelegramDL Bot v{version}</h2>
<p>📥 Download restricted content from <b>channels, groups, bots & stories</b></p>

<blockquote>💡 <b>How it works:</b>
Send any Telegram link → Bot downloads → Files sent to you</blockquote>

<h3>⚡ Quick Start</h3>
<ol>
<li>Send a Telegram link or username</li>
<li>Bot downloads the content</li>
<li>Files delivered to you here</li>
</ol>

<p>🔗 <b>Supported:</b> Channels · Groups · Bots · Stories · Invite Links</p>
<footer>Use the buttons below to navigate</footer>
"""
    return InputRichMessage(html=html.strip())


def ABOUT_RICH(version: str = "2.0.0") -> InputRichMessage:
    """Build about rich message with HTML formatting.

    Args:
        version: Bot version string

    Returns:
        InputRichMessage with styled about content
    """
    html = f"""
<h2>ℹ️ About TelegramDL</h2>

<table>
<tr><td><b>Version</b></td><td><code>{version}</code></td></tr>
<tr><td><b>Library</b></td><td>ftmgram (Bot API 10.1)</td></tr>
<tr><td><b>Developer</b></td><td><a href="https://t.me/Shineii86">@Shineii86</a></td></tr>
</table>

<h3>✨ Features</h3>
<ul>
<li>📥 Download restricted content</li>
<li>📦 Batch download with progress bar</li>
<li>🖼 Custom thumbnails per user</li>
<li>📝 Custom captions with placeholders</li>
<li>⭐ Premium system with daily limits</li>
<li>📢 Dump chat auto-forward</li>
<li>🎬 yt-dlp (YouTube, Instagram, TikTok)</li>
<li>🔐 Secure login system</li>
</ul>

<h3>🔗 Supported Content</h3>
<ul>
<li>✅ Public & Private Channels</li>
<li>✅ Groups & Supergroups</li>
<li>✅ Bot Chats</li>
<li>✅ Stories</li>
<li>✅ Invite Links</li>
<li>✅ YouTube, Instagram, Facebook, TikTok</li>
</ul>

<footer>Built with ❤️ by <a href="https://t.me/Shineii86">@Shineii86</a></footer>
"""
    return InputRichMessage(html=html.strip())


def MYPLAN_RICH(plan_type: str, expiry: str, daily_used: int, daily_limit: int,
                total_saves: int, free_size: int, premium_size: int) -> InputRichMessage:
    """Build plan info rich message with HTML formatting.

    Args:
        plan_type: Current plan type (Free/Premium)
        expiry: Plan expiry date
        daily_used: Downloads used today
        daily_limit: Daily download limit
        total_saves: Total files saved
        free_size: Free user file size limit
        premium_size: Premium user file size limit

    Returns:
        InputRichMessage with styled plan info
    """
    html = f"""
<h2>👤 My Plan</h2>

<h3>Status</h3>
<table>
<tr><td>🏷️ <b>Plan</b></td><td>{plan_type}</td></tr>
<tr><td>📅 <b>Expires</b></td><td>{expiry}</td></tr>
</table>

<h3>Usage</h3>
<table>
<tr><td>📊 <b>Today</b></td><td><code>{daily_used}/{daily_limit}</code></td></tr>
<tr><td>💾 <b>Total</b></td><td><code>{total_saves}</code> saved</td></tr>
</table>

<h3>Limits</h3>
<table>
<tr><td>🆓 <b>Free</b></td><td>{daily_limit}/day, {free_size}MB</td></tr>
<tr><td>⭐ <b>Premium</b></td><td>Unlimited, {premium_size}MB</td></tr>
</table>

<footer>💡 Upgrade with /premium for unlimited access!</footer>
"""
    return InputRichMessage(html=html.strip())


def PROGRESS_RICH(bar: str, percent: float, speed: str, done: str, total: str,
                  failed: str, remaining: str, elapsed: str, eta: str,
                  current: str) -> InputRichMessage:
    """Build progress rich message with HTML formatting.

    Args:
        bar: Progress bar string
        percent: Progress percentage
        speed: Download speed
        done: Bytes downloaded
        total: Total bytes
        failed: Failed count
        remaining: Remaining count
        elapsed: Elapsed time
        eta: Estimated time remaining
        current: Current file name

    Returns:
        InputRichMessage with styled progress display
    """
    html = f"""
<h3>📥 Downloading...</h3>
<pre>[{bar}] {percent:.1f}%</pre>

<table>
<tr><td>⚡ <b>Speed</b></td><td><code>{speed}/s</code></td></tr>
<tr><td>✅ <b>Done</b></td><td><code>{done}/{total}</code></td></tr>
<tr><td>❌ <b>Failed</b></td><td><code>{failed}</code></td></tr>
<tr><td>⏳ <b>Remaining</b></td><td><code>{remaining}</code></td></tr>
</table>

<p>⏱ <b>Elapsed:</b> <code>{elapsed}</code> | 📡 <b>ETA:</b> <code>{eta}</code></p>
<footer>📄 {current}</footer>
"""
    return InputRichMessage(html=html.strip())


def HELP_RICH() -> InputRichMessage:
    """Build help rich message with HTML formatting.

    Returns:
        InputRichMessage with styled help content
    """
    html = """
<h2>📖 TelegramDL Help</h2>

<h3>📥 Download Commands</h3>
<ul>
<li><code>/dl &lt;link&gt;</code> — Download from URL</li>
<li><code>/adl &lt;link&gt;</code> — Download audio only</li>
<li><code>/backup</code> — Backup your settings</li>
</ul>

<h3>👤 User Commands</h3>
<ul>
<li><code>/login</code> — Login for restricted content</li>
<li><code>/settings</code> — View your settings</li>
<li><code>/myplan</code> — View your subscription plan</li>
</ul>

<h3>🔧 Admin Commands</h3>
<ul>
<li><code>/broadcast</code> — Broadcast message to all users</li>
<li><code>/ban /unban</code> — Ban/unban users</li>
<li><code>/welcome</code> — Set welcome message</li>
</ul>

<h3>ℹ️ Info Commands</h3>
<ul>
<li><code>/ping</code> — Check bot latency</li>
<li><code>/info</code> — Bot information</li>
<li><code>/about</code> — About the bot</li>
</ul>

<footer>Supported: YouTube, Instagram, TikTok, Facebook + 100 sites via yt-dlp</footer>
"""
    return InputRichMessage(html=html.strip())


def ERROR_RICH(error_type: str, message: str, suggestion: str = "") -> InputRichMessage:
    """Build error rich message with HTML formatting.

    Args:
        error_type: Type of error
        message: Error message details
        suggestion: Optional suggestion to fix

    Returns:
        InputRichMessage with styled error content
    """
    html = f"""
<h3>❌ {error_type}</h3>
<blockquote>{message}</blockquote>
{"<p>💡 <b>Suggestion:</b> " + suggestion + "</p>" if suggestion else ""}
<footer>Need help? Use /help</footer>
"""
    return InputRichMessage(html=html.strip())


# ===========================================================================
#   END OF UI MODULE
# ===========================================================================
