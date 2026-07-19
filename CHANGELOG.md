# 📋 Changelog

All notable changes to TelegramDL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-01-19

### 🚀 Major Release

Complete rewrite from Telethon to Kurigram with premium features.

### ✨ Added

#### Core Features
- **Premium System** — Daily limits, file size limits, subscription management
- **Payment Integration** — UPI, PayPal, Crypto, Telegram Stars
- **Custom Thumbnails** — Per-user thumbnail storage
- **Custom Captions** — Placeholder support ({filename}, {size}, {date})
- **Dump Chat** — Auto-forward downloads to channel
- **Ban System** — Admin ban/unban users
- **File Splitting** — Auto-split files >2GB
- **yt-dlp Integration** — YouTube, Instagram, Facebook, TikTok support
- **Audio Metadata** — Embed title/artist/album art
- **Custom Bot** — Per-user bot token support
- **Topic Group** — Support for topic-based groups
- **Logging** — Full activity logging to channel

#### UI/UX
- Modern inline keyboards
- Progress bar with ETA
- Callback handlers for all actions
- Back navigation

#### Deployment
- Docker & Docker Compose
- Heroku (Procfile, heroku.yml, app.json)
- Render
- Koyeb
- VPS (systemd, screen, nohup)
- Flask status page

#### Documentation
- Comprehensive README
- Architecture docs
- FAQ with troubleshooting
- Deployment guide for all platforms
- Security policy
- Code of conduct
- Contributing guidelines

### 🔧 Changed
- Migrated from Telethon to Kurigram (Pyrogram fork)
- Improved error handling with retry logic
- Enhanced FloodWait handling

### 🐛 Fixed
- Session expiration handling
- Rate limiting issues
- Memory leaks in batch downloads

---

## [1.0.0] - 2025-12-01

### 🚀 Initial Release

#### Features
- Basic download functionality
- Public channel support
- Session string authentication
- Google Colab notebook

#### Deployment
- Google Colab support
- Basic Docker support

---

## [Unreleased]

### 🔮 Planned Features

#### v2.1.0
- [ ] Web dashboard for user management
- [ ] API endpoint for external integrations
- [ ] Multi-language support
- [ ] Download queue system
- [ ] Webhook notifications

#### v2.2.0
- [ ] Plugin system for custom extensions
- [ ] Download history and statistics
- [ ] Scheduled downloads
- [ ] Cloud storage integration (Google Drive, Dropbox)

#### v3.0.0
- [ ] Web UI with React frontend
- [ ] REST API for mobile apps
- [ ] Distributed download system
- [ ] AI-powered content categorization

---

## 📊 Version Statistics

| Version | Files Changed | Contributors | Downloads |
|---------|---------------|--------------|-----------|
| 2.0.0 | 22+ | 1 | Growing |
| 1.0.0 | 10 | 1 | 100+ |

---

## 🔗 Links

- [Releases](https://github.com/Shineii86/TelegramDL/releases)
- [Milestones](https://github.com/Shineii86/TelegramDL/milestones)
- [Roadmap](https://github.com/Shineii86/TelegramDL/projects)

---

**Maintained by**: [Shinei Nouzen](https://github.com/Shineii86)
