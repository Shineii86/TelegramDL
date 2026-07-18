# Changelog

All notable changes to TelegramDL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
