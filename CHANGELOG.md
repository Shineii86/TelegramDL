# Changelog

All notable changes to TelegramDL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.4.0] - 2026-07-18

### Added
- Support for ALL Telegram link types:
  - Public channels: `t.me/username`
  - Private channels: `t.me/c/CHANNEL_ID/MSG_ID`
  - Invite links: `t.me/+invitehash` and `t.me/joinchat/hash`
  - Groups & Supergroups: `t.me/groupname/123`
  - Bots: `t.me/botusername`
  - Username only: `username` or `@username`
  - Numeric IDs: `-1001234567890/123`
  - Batch ranges: `t.me/username/1001-1010`
  - Forwarded messages: `t.me/c/123/456?single`
- Chat info display — shows channel/group/bot details when no message ID
- Auto-join attempt for private channels/groups
- Updated help with complete format table

### Changed
- Rewrote `parse_channel_username()` with 8 pattern matchers
- Improved `save()` function with proper chat type detection
- Updated UI help texts with all supported formats

---

## [2.3.0] - 2026-07-18

### Added
- Modern UI/UX with inline keyboards and callback buttons
- Main menu with navigation buttons (Download, Backup, Batch, Login, Settings, Help)
- Help menu with topic-specific sections and back buttons
- Settings menu with delay, file size, type filter, captions options
- Delay selector with preset buttons (3s, 5s, 10s, 15s, 20s, 30s)
- File size selector with preset buttons (500MB, 1GB, 2GB, 5GB, 10GB, No Limit)
- Login menu with login/logout buttons
- Confirm/Cancel dialogs for dangerous actions
- Stop button for batch downloads
- Back navigation on all sub-menus
- Message templates for all user interactions (utils/ui.py)

### Changed
- Rewrote plugins/start.py with full callback handler system
- Updated plugins/generate.py with modern UI messages
- Updated help messages with formatted sections
- All messages now have inline keyboard navigation

---

## [2.2.0] - 2026-07-18

### Added
- Live progress messages — real-time progress bar with percentage in Telegram
- Download counter — shows downloaded/skipped/failed/total counts
- ETA calculation — estimated time remaining based on average speed
- File preview — shows file info (type, size) before download
- Cancel button — inline keyboard button to cancel batch downloads
- Progress bar — visual Unicode progress bar (█░) in messages
- Elapsed time tracking — shows how long download has been running

### Changed
- Rewrote utils/progress.py with DownloadProgress class
- Updated plugins/generate.py with live progress and cancel support
- Updated plugins/backup.py with progress tracking

---

## [2.1.0] - 2026-07-18

### Added
- `/backup` command — backup channel media to a Telegram backup channel
- `/batch` command — batch download all media from a channel
- Session stats — Colab time tracking with 3-tier warnings (critical/warning/tip)
- Keep-alive — thread-based ping to prevent Colab idle timeout
- Parallel downloads — configurable concurrency via semaphore
- Forward mode — direct message forwarding (fastest method)
- Caption support — auto-generated captions with folder, date, message ID
- Original caption preservation with truncation to 1024 chars
- Album handling — detect and process grouped messages
- Video metadata preservation — duration, width, height on upload
- Configurable settings: PARALLEL_DOWNLOADS, FORWARD_MODE, CAPTION_ENABLED, KEEP_ORIGINAL_CAPTION, BACKUP_CHANNEL, KEEP_ALIVE_INTERVAL, SESSION_LIMIT_HOURS

### Changed
- Updated config.py with all new environment variables
- Updated start.py help text with /backup and /batch commands
- Updated utils/__init__.py to export SessionStats and KeepAlive

---

## [2.0.0] - 2026-07-18

### Changed
- **Complete rewrite** from Telethon to Kurigram (Pyrogram fork)
- **Architecture change** from CLI tool to Telegram bot with plugin system
- **Restricted content handling** via two-tier access: bot token → user session fallback
- **Colab notebook** rewritten for bot-based workflow (4 cells: setup, config, run, session gen)
- **Dependencies** updated: kurigram, tgcrypto, motor, Flask, gunicorn
- **Configuration** simplified with environment variables

### Added
- Bot commands: `/start`, `/help`, `/login`, `/logout`, `/cancel`
- Per-user login system with OTP authentication
- MongoDB integration for session storage (via Motor async driver)
- Flask keep-alive server for Docker/Koyeb deployment
- Dockerfile and Procfile for containerized deployment
- Batch download support (message ID ranges)
- Progress tracking with real-time status
- Checkpoint system for resuming after Colab disconnects
- File size filter (skip files > 2GB by default)
- Date and media type filters
- ZIP archive creation utility
- CHANGELOG.md

### Removed
- Telethon library (replaced by Kurigram)
- CLI interface (replaced by bot commands)
- Old telegramdl/ package structure
- nest_asyncio workaround (handled via bot architecture)
