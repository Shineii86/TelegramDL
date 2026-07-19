# 🏗️ Architecture

## Overview

TelegramDL is built on a modular architecture using the Kurigram (Pyrogram fork) library. The system uses a two-tier access pattern: bot token for public content, user session for restricted content.

## 📐 System Design

```mermaid
graph TB
    subgraph UI["📱 User Interface"]
        TG["Telegram Bot API"]
    end

    subgraph CORE["🤖 Bot Core (bot.py)"]
        BOT["Bot Client<br/>Public Access"]
        USER["User Client<br/>Restricted Access"]
        FLASK["Flask Server<br/>Keep-Alive"]
    end

    subgraph PLUGINS["🔌 Plugin System"]
        START["start.py<br/>Commands"]
        GEN["generate.py<br/>Downloads"]
        BACKUP["backup.py<br/>Backup"]
        PAY["payment.py<br/>Payments"]
        BCAST["broadcast.py<br/>Broadcast"]
        YTDL["ytdl.py<br/>yt-dlp"]
        CBOT["custom_bot.py<br/>Custom Bot"]
        LOG["logger.py<br/>Logging"]
    end

    subgraph UTILS["🔧 Utilities Layer"]
        UI["ui.py<br/>Keyboards"]
        PROG["progress.py<br/>Progress Bar"]
        MEDIA["media.py<br/>Detection"]
        FILTER["filters.py<br/>Filters"]
        SESS["session.py<br/>Session"]
        ALIVE["keepalive.py<br/>Keep-Alive"]
        CP["checkpoint.py<br/>Resume"]
        ARCH["archive.py<br/>ZIP"]
        SPLIT["splitter.py<br/>File Split"]
        YTDLU["ytdl.py<br/>yt-dlp Wrapper"]
        META["audio_meta.py<br/>Metadata"]
    end

    subgraph DATA["💾 Data Layer"]
        MONGO["MongoDB (Motor)"]
        USERS["Users Collection"]
        SESSIONS["Sessions Collection"]
        PREMIUM["Premium Collection"]
    end

    TG --> CORE
    CORE --> PLUGINS
    PLUGINS --> UTILS
    UTILS --> DATA
    MONGO --> USERS
    MONGO --> SESSIONS
    MONGO --> PREMIUM

    style UI fill:#1a1a2e,stroke:#e94560,color:#fff
    style CORE fill:#16213e,stroke:#0f3460,color:#fff
    style PLUGINS fill:#0f3460,stroke:#533483,color:#fff
    style UTILS fill:#533483,stroke:#e94560,color:#fff
    style DATA fill:#1a1a2e,stroke:#16213e,color:#fff
```

## 🔄 Data Flow

### Download Flow

```mermaid
flowchart TD
    A["👤 User Sends Link"] --> B["🔍 Parse Link Type"]
    B --> C["🤖 Bot Client (Tier 1)"]
    C --> D{"Can Bot Access?"}
    
    D -->|"✅ Yes"| E["📥 Download via Bot"]
    D -->|"❌ No"| F["🔐 User Session (Tier 2)"]
    F --> G["📥 Download via User"]
    
    E --> H["📤 Send to User"]
    G --> H
    
    H --> I{"Has Dump Chat?"}
    I -->|"✅ Yes"| J["📢 Forward to Dump Chat"]
    I -->|"❌ No"| K["✅ Complete"]
    J --> K

    style A fill:#1a1a2e,stroke:#e94560,color:#fff
    style D fill:#16213e,stroke:#f39c12,color:#fff
    style E fill:#27ae60,stroke:#2ecc71,color:#fff
    style F fill:#e74c3c,stroke:#c0392b,color:#fff
    style G fill:#3498db,stroke:#2980b9,color:#fff
    style H fill:#9b59b6,stroke:#8e44ad,color:#fff
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant B as 🤖 Bot
    participant T as 📱 Telegram
    participant DB as 💾 Database

    U->>B: /login
    B->>U: Enter phone number
    U->>B: +1234567890
    B->>T: Send OTP
    T->>U: OTP Code
    U->>B: Enter OTP
    B->>T: Verify OTP
    T->>B: Session String
    B->>DB: Store session
    B->>U: ✅ Login successful!
```

### Payment Flow

```mermaid
flowchart LR
    A["👤 User"] -->|"/pay monthly"| B["🤖 Bot"]
    B --> C["📋 Create Request"]
    C --> D["💳 Show Payment Methods"]
    D --> E["💵 User Pays"]
    E --> F["📸 Send Proof"]
    F --> G["👨‍💼 Admin Reviews"]
    G -->|"✅ Approve"| H["⭐ Add Premium"]
    G -->|"❌ Reject"| I["❌ Notify User"]
    H --> J["🎉 User Notified"]

    style A fill:#3498db,stroke:#2980b9,color:#fff
    style B fill:#2ecc71,stroke:#27ae60,color:#fff
    style G fill:#f39c12,stroke:#f1c40f,color:#fff
    style H fill:#27ae60,stroke:#2ecc71,color:#fff
    style I fill:#e74c3c,stroke:#c0392b,color:#fff
```

### Batch Download Flow

```mermaid
flowchart TD
    A["👤 /batch 1001-1010"] --> B["🔢 Parse Range"]
    B --> C["📊 Create Queue"]
    C --> D["📥 Download 1001"]
    D --> E["📤 Upload 1001"]
    E --> F{"More Files?"}
    F -->|"✅ Yes"| G["⏱ Wait DELAY"]
    G --> D
    F -->|"❌ No"| H["✅ Complete"]
    
    D --> I{"Error?"}
    I -->|"🔄 FloodWait"| J["⏳ Wait & Retry"]
    J --> D
    I -->|"❌ Failed"| K["📝 Log Error"]
    K --> F

    style A fill:#3498db,stroke:#2980b9,color:#fff
    style H fill:#27ae60,stroke:#2ecc71,color:#fff
    style I fill:#e74c3c,stroke:#c0392b,color:#fff
    style J fill:#f39c12,stroke:#f1c40f,color:#fff
```

## 📦 Module Dependencies

```mermaid
graph TD
    BOT["🤖 bot.py<br/>Main Entry"] --> CONFIG["⚙️ config.py<br/>Configuration"]
    BOT --> DB["💾 database/db.py<br/>MongoDB"]
    
    BOT --> PLUGINS["🔌 plugins/"]
    BOT --> UTILS["🔧 utils/"]
    
    PLUGINS --> PSTART["start.py<br/>Commands"]
    PLUGINS --> PGEN["generate.py<br/>Downloads"]
    PLUGINS --> PBACKUP["backup.py<br/>Backup"]
    PLUGINS --> PBCAST["broadcast.py<br/>Broadcast"]
    PLUGINS --> PPAY["payment.py<br/>Payments"]
    PLUGINS --> PLOG["logger.py<br/>Logging"]
    PLUGINS --> PYTDL["ytdl.py<br/>yt-dlp"]
    PLUGINS --> PCBOT["custom_bot.py<br/>Custom Bot"]
    PLUGINS --> PSET["settings.py<br/>Settings"]
    
    UTILS --> UUI["ui.py<br/>Keyboards"]
    UTILS --> UPROG["progress.py<br/>Progress"]
    UTILS --> USESS["session.py<br/>Session"]
    UTILS --> UALIVE["keepalive.py<br/>Keep-Alive"]
    UTILS --> UCP["checkpoint.py<br/>Resume"]
    UTILS --> UMEDIA["media.py<br/>Detection"]
    UTILS --> UFILTER["filters.py<br/>Filters"]
    UTILS --> UARCH["archive.py<br/>ZIP"]
    UTILS --> USPLIT["splitter.py<br/>File Split"]
    UTILS --> UYTDL["ytdl.py<br/>yt-dlp Wrapper"]
    UTILS --> UMETA["audio_meta.py<br/>Metadata"]

    style BOT fill:#e94560,stroke:#c0392b,color:#fff
    style CONFIG fill:#f39c12,stroke:#f1c40f,color:#fff
    style DB fill:#3498db,stroke:#2980b9,color:#fff
    style PLUGINS fill:#9b59b6,stroke:#8e44ad,color:#fff
    style UTILS fill:#2ecc71,stroke:#27ae60,color:#fff
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

```mermaid
graph LR
    A["👤 User Request"] --> B{"Content Type?"}
    B -->|"🌐 Public"| C["🤖 Bot Token<br/>Tier 1"]
    B -->|"🔒 Restricted"| D["🔐 User Session<br/>Tier 2"]
    
    C --> E["✅ Download"]
    D --> E
    
    style A fill:#3498db,stroke:#2980b9,color:#fff
    style C fill:#27ae60,stroke:#2ecc71,color:#fff
    style D fill:#e74c3c,stroke:#c0392b,color:#fff
    style E fill:#2ecc71,stroke:#27ae60,color:#fff
```

### Session Storage

- **LOGIN_SYSTEM=true**: Each user authenticates separately (recommended)
- **LOGIN_SYSTEM=false**: Single global session (admin's session)

### Access Control

```mermaid
flowchart TD
    A["👤 User Request"] --> B{"🚫 Is Banned?"}
    B -->|"✅ Yes"| C["❌ Block"]
    B -->|"❌ No"| D{"👑 Is Admin?"}
    D -->|"✅ Yes"| E["🌟 Full Access"]
    D -->|"❌ No"| F{"⭐ Is Premium?"}
    F -->|"✅ Yes"| G["🚀 Unlimited"]
    F -->|"❌ No"| H{"📊 Daily Limit?"}
    H -->|"❌ Exceeded"| I["⏳ Wait Tomorrow"]
    H -->|"✅ OK"| J["📥 Process"]
    
    J --> K["📥 Download"]
    K --> L["📤 Upload"]
    L --> M["✅ Complete"]

    style A fill:#3498db,stroke:#2980b9,color:#fff
    style C fill:#e74c3c,stroke:#c0392b,color:#fff
    style E fill:#f39c12,stroke:#f1c40f,color:#fff
    style G fill:#9b59b6,stroke:#8e44ad,color:#fff
    style I fill:#e67e22,stroke:#d35400,color:#fff
    style M fill:#27ae60,stroke:#2ecc71,color:#fff
```

## 🚀 Deployment Options

```mermaid
graph TD
    A["🚀 Deployment"] --> B["📱 Google Colab<br/>Free · Easy"]
    A --> C["🐳 Docker<br/>Flexible · Medium"]
    A --> D["🔶 Heroku<br/>PaaS · Easy"]
    A --> E["🟣 Render<br/>PaaS · Easy"]
    A --> F["🔵 Koyeb<br/>PaaS · Easy"]
    A --> G["🖥️ VPS<br/>Self-hosted · Hard"]
    
    B --> B1["Notebook<br/>12hr session"]
    C --> C1["Container<br/>24/7 uptime"]
    D --> D1["Free tier<br/>Limited"]
    E --> E1["Free tier<br/>Sleeps"]
    F --> F1["Free tier<br/>Global"]
    G --> G1["Full control<br/>$5+/mo"]

    style A fill:#e94560,stroke:#c0392b,color:#fff
    style B fill:#f39c12,stroke:#f1c40f,color:#fff
    style C fill:#3498db,stroke:#2980b9,color:#fff
    style D fill:#9b59b6,stroke:#8e44ad,color:#fff
    style E fill:#e74c3c,stroke:#c0392b,color:#fff
    style F fill:#1abc9c,stroke:#16a085,color:#fff
    style G fill:#34495e,stroke:#2c3e50,color:#fff
```

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

```mermaid
flowchart TD
    A["📋 Environment Variables"] --> B["⚙️ config.py<br/>Defaults"]
    B --> C["📄 .env File<br/>Override"]
    C --> D["🖥️ Runtime<br/>Colab/Docker"]
    
    D --> E["🤖 Bot Running"]
    
    style A fill:#f39c12,stroke:#f1c40f,color:#fff
    style B fill:#3498db,stroke:#2980b9,color:#fff
    style C fill:#9b59b6,stroke:#8e44ad,color:#fff
    style D fill:#2ecc71,stroke:#27ae60,color:#fff
    style E fill:#e94560,stroke:#c0392b,color:#fff
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
