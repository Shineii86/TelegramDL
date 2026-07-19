# 🏗️ Architecture

## Overview

TelegramDL is built on a modular architecture using the Kurigram (Pyrogram fork) library. The system uses a two-tier access pattern: bot token for public content, user session for restricted content.

## 📐 System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                    (Telegram Bot API)                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BOT CORE (bot.py)                        │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │ Bot Client   │  │ User Client │  │ Flask Server │           │
│   │ (Public)     │  │ (Restricted)│  │ (Keep-Alive) │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PLUGIN SYSTEM                              │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│   │  start.py   │ │ generate.py│ │  backup.py  │ │ payment.py  │ │
│   │  Commands   │ │ Downloads  │ │   Backup    │ │  Payments   │ │
│   └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│   │ broadcast.py│ │  ytdl.py   │ │custom_bot.py│ │  logger.py  │ │
│   │  Broadcast  │ │  yt-dlp    │ │ Custom Bot  │ │  Logging    │ │
│   └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UTILITIES LAYER                            │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│   │   ui.py     │ │ progress.py│ │  media.py   │ │  filters.py │ │
│   │  Keyboards  │ │  Progress  │ │  Detection  │ │   Filters   │ │
│   └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│   │ session.py  │ │keepalive.py│ │checkpoint.py│ │  archive.py │ │
│   │   Session   │ │ Keep-Alive │ │  Checkpoint │ │   Archive   │ │
│   └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐                 │
│   │ splitter.py │ │  ytdl.py   │ │audio_meta.py│                 │
│   │   Splitter  │ │  yt-dlp    │ │  Metadata   │                 │
│   └────────────┘ └────────────┘ └────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    MongoDB (Motor)                       │  │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│   │   │  Users    │  │ Sessions │  │ Premium  │            │  │
│   │   │  Profiles │  │  Auth    │  │ Payments │            │  │
│   │   └──────────┘  └──────────┘  └──────────┘            │  │
│   └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Download Flow

```
User Sends Link
       │
       ▼
┌──────────────┐
│  Parse Link   │
│  (Link Type)  │
└──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  Bot Client   │────▶│  Can Access? │
│  (Tier 1)     │     │              │
└──────────────┘     └──────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌──────────┐             ┌──────────┐
       │   YES    │             │    NO    │
       │  Download │             │  Try User │
       │  via Bot  │             │  Session  │
       └──────────┘             └──────────┘
              │                         │
              │                         ▼
              │                  ┌──────────┐
              │                  │  Download  │
              │                  │  via User  │
              │                  └──────────┘
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                    ┌──────────┐
                    │  Send to  │
                    │   User    │
                    └──────────┘
```

### Authentication Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User: /login │────▶│  Enter Phone │────▶│  Enter OTP   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                   │
                                                   ▼
                                            ┌──────────────┐
                                            │ Get Session   │
                                            │ String        │
                                            └──────────────┘
                                                   │
                                                   ▼
                                            ┌──────────────┐
                                            │ Store in DB   │
                                            │ (per-user)    │
                                            └──────────────┘
```

## 📦 Module Dependencies

```
bot.py
├── config.py (Configuration)
├── database/db.py (MongoDB)
├── plugins/
│   ├── start.py (Commands)
│   ├── generate.py (Downloads)
│   ├── backup.py (Backup)
│   ├── broadcast.py (Broadcast)
│   ├── payment.py (Payments)
│   ├── logger.py (Logging)
│   ├── ytdl.py (yt-dlp)
│   ├── custom_bot.py (Custom Bot)
│   └── settings.py (Settings)
└── utils/
    ├── ui.py (UI Components)
    ├── progress.py (Progress Bar)
    ├── session.py (Session Tracking)
    ├── keepalive.py (Keep-Alive)
    ├── checkpoint.py (Resume)
    ├── media.py (Media Detection)
    ├── filters.py (Filters)
    ├── archive.py (ZIP)
    ├── splitter.py (File Split)
    ├── ytdl.py (yt-dlp Wrapper)
    └── audio_metadata.py (Metadata)
```

## 🗄️ Database Schema

### Users Collection

```json
{
  "_id": "ObjectId",
  "id": 123456789,
  "name": "Username",
  "is_premium": true,
  "premium_expiry": "2026-02-19T00:00:00Z",
  "daily_usage": 5,
  "daily_reset": "2026-01-19T00:00:00Z",
  "total_saves": 150,
  "session_string": "1BVtsO8...",
  "thumbnail": "AgACAgIA...",
  "caption": "📁 {filename}",
  "dump_chat": "-1001234567890",
  "bot_token": "123456:ABC...",
  "rename_tag": "backup_",
  "delete_words": ["ad", "promo"],
  "replace_words": {"old": "new"},
  "topic_id": 123,
  "banned": false,
  "created_at": "2026-01-01T00:00:00Z"
}
```

### Payment Requests Collection

```json
{
  "_id": "ObjectId",
  "payment_request": true,
  "user_id": 123456789,
  "request_id": "1234567890_1705651200",
  "plan": "monthly",
  "days": 30,
  "price": "₹149 / $3",
  "status": "pending|approved|rejected",
  "created_at": "2026-01-19T00:00:00Z",
  "updated_at": "2026-01-19T00:00:00Z"
}
```

## 🔐 Security Model

### Two-Tier Access

| Tier | Client | Use Case |
|------|--------|----------|
| **Tier 1** | Bot Token | Public channels, unrestricted content |
| **Tier 2** | User Session | Private channels, restricted content |

### Session Storage

- **LOGIN_SYSTEM=true**: Each user authenticates separately (recommended)
- **LOGIN_SYSTEM=false**: Single global session (admin's session)

### Access Control

```
User Request
    │
    ▼
┌──────────────┐
│  Is Banned?  │──YES──▶ Block
└──────────────┘
    │ NO
    ▼
┌──────────────┐
│  Is Admin?   │──YES──▶ Full Access
└──────────────┘
    │ NO
    ▼
┌──────────────┐
│ Is Premium?  │──YES──▶ Unlimited
└──────────────┘
    │ NO
    ▼
┌──────────────┐
│ Daily Limit? │──YES──▶ Block
└──────────────┘
    │ OK
    ▼
┌──────────────┐
│  Process     │
└──────────────┘
```

## 🚀 Deployment Options

| Platform | Type | Difficulty | Cost |
|----------|------|------------|------|
| Google Colab | Notebook | ⭐ Easy | Free |
| Docker | Container | ⭐⭐ Medium | Varies |
| Heroku | PaaS | ⭐⭐ Medium | Free/Paid |
| Render | PaaS | ⭐⭐ Medium | Free/Paid |
| Koyeb | PaaS | ⭐⭐ Medium | Free/Paid |
| VPS | Self-hosted | ⭐⭐⭐ Hard | $5+/mo |

## 📊 Performance Considerations

### Rate Limiting

- **Default WAITING_TIME**: 10 seconds between messages
- **FloodWait Handling**: Automatic retry with exponential backoff
- **Concurrent Downloads**: Configurable (default: 3)

### Memory Management

- **File Splitting**: Large files (>2GB) split automatically
- **Checkpoint System**: Saves progress every 50 files
- **Auto-Cleanup**: Temporary files deleted after upload

### Database Optimization

- **Indexed Queries**: User ID indexed for fast lookups
- **Async Operations**: Motor async driver for non-blocking I/O
- **Connection Pooling**: Automatic connection management

## 🔧 Configuration Hierarchy

```
Environment Variables
        │
        ▼
┌──────────────┐
│  config.py   │
│  (Defaults)  │
└──────────────┘
        │
        ▼
┌──────────────┐
│  .env File   │
│  (Override)  │
└──────────────┘
        │
        ▼
┌──────────────┐
│  Runtime     │
│  (Colab/Docker)│
└──────────────┘
```

## 📈 Scalability

### Horizontal Scaling

- Multiple bot instances can run simultaneously
- MongoDB supports replica sets for high availability
- Load balancing via Docker Compose or Kubernetes

### Vertical Scaling

- Increase WAITING_TIME for rate limiting
- Adjust PARALLEL_DOWNLOADS for throughput
- Scale MongoDB resources for more users

## 🧪 Testing

### Manual Testing

```bash
# Test bot commands
/start
/help
/login
/dl <public_link>

# Test restricted content
/dl <private_link>

# Test admin commands
/broadcast <message>
/ban <user_id>
```

### Load Testing

```bash
# Simulate multiple users
for i in {1..100}; do
  python3 -c "import asyncio; from bot import bot; asyncio.run(bot.start())" &
done
```

---

**Last Updated**: 2026-01-19
