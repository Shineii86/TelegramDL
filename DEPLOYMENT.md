# 🚀 Deployment Guide

Complete deployment guide for all supported platforms.

---

## 📱 Google Colab (Easiest)

### Prerequisites
- Google Account
- Chrome browser

### Steps

1. **Click the Colab Badge**

[![Open in Colab](https://img.shields.io/badge/Google_Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=black)](https://colab.research.google.com/github/Shineii86/TelegramDL/blob/main/notebook/TelegramDL.ipynb)

2. **Step 1 — Setup**
   - Click "Run All" or run each cell individually
   - Installs dependencies automatically (~30 seconds)

3. **Step 2 — Configuration**
   - Fill in your credentials:
     - `API_ID` — from [my.telegram.org](https://my.telegram.org)
     - `API_HASH` — from [my.telegram.org](https://my.telegram.org)
     - `BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
     - `STRING_SESSION` — (optional) for restricted content

4. **Step 3 — Run**
   - Click "Run" to start the bot
   - Bot will show "Bot is running!" when ready

5. **Step 4 — Generate Session (Optional)**
   - Run this cell if you need restricted content access
   - Enter phone number and OTP
   - Copy session string back to Step 2

### Tips

| Tip | Description |
|-----|-------------|
| Use Checkpoint | Auto-saves every 50 files, resume after disconnect |
| Set STRING_SESSION | For restricted content access |
| Mount Google Drive | For persistent storage across sessions |
| Use Forward Mode | Faster than download+upload |

---

## 🐳 Docker

### Prerequisites
- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))

### Method 1: Docker Run

```bash
# Build the image
docker build -t telegramdl .

# Run the container
docker run -d \
  --name telegramdl \
  --restart unless-stopped \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e DB_URI=your_mongodb_uri \
  -e ADMINS=your_user_id \
  -e CHANNEL_ID=-1001234567890 \
  telegramdl

# View logs
docker logs -f telegramdl

# Stop
docker stop telegramdl
```

### Method 2: Docker Compose

```bash
# Create .env file
cp .env.example .env
nano .env  # Fill in your credentials

# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

### Docker Environment Variables

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
DB_URI=mongodb://mongo:27017
DB_NAME=telegramdl
ADMINS=your_user_id
CHANNEL_ID=-1001234567890
WAITING_TIME=10
LOGIN_SYSTEM=true
KEEP_ALIVE=true
```

---

## 🔶 Heroku

### Method 1: Deploy Button

[![Deploy](https://img.shields.io/badge/Deploy-Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white)](https://heroku.com/deploy)

### Method 2: Container Registry

```bash
# Login to Heroku
heroku login
heroku container:login

# Create app
heroku create your-app-name

# Build and push
heroku container:push worker --app your-app-name
heroku container:release worker --app your-app-name

# Set config vars
heroku config:set \
  API_ID=your_api_id \
  API_HASH=your_api_hash \
  BOT_TOKEN=your_bot_token \
  DB_URI=your_mongodb_uri \
  ADMINS=your_user_id \
  --app your-app-name

# View logs
heroku logs --tail --app your-app-name
```

### Method 3: Git Deploy

```bash
# Clone and login
git clone https://github.com/Shineii86/TelegramDL.git
cd TelegramDL
heroku create your-app-name

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1

# Set config
heroku config:set API_ID=your_api_id API_HASH=your_api_hash BOT_TOKEN=your_bot_token --app your-app-name
```

---

## 🟣 Render

### Steps

1. Go to [render.com](https://render.com)
2. Click **New Web Service**
3. Connect your GitHub repository
4. Select **Docker** as build type
5. Choose **Free** plan (or paid for better performance)
6. Add environment variables:

| Variable | Value |
|----------|-------|
| `API_ID` | Your API ID |
| `API_HASH` | Your API Hash |
| `BOT_TOKEN` | Your Bot Token |
| `DB_URI` | MongoDB URI |
| `ADMINS` | Your User ID |

7. Click **Create Web Service**

### Notes
- Free tier has 15-minute idle timeout
- Use `KEEP_ALIVE=true` to prevent sleeping
- Upgrade to paid plan for 24/7 uptime

---

## 🔵 Koyeb

### Steps

1. Go to [koyeb.com](https://koyeb.com)
2. Click **Create New Service**
3. Select **Dockerfile** as build type
4. Connect your GitHub repository
5. Add environment variables:

| Variable | Value |
|----------|-------|
| `API_ID` | Your API ID |
| `API_HASH` | Your API Hash |
| `BOT_TOKEN` | Your Bot Token |
| `DB_URI` | MongoDB URI |
| `ADMINS` | Your User ID |

6. Click **Deploy**

### Notes
- Free tier available
- Automatic SSL
- Global edge network

---

## 🖥️ VPS (Ubuntu/Debian)

### Prerequisites
- Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Python 3.10+

### Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# Clone repository
git clone https://github.com/Shineii86/TelegramDL.git
cd TelegramDL

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Fill in your credentials
```

### Running with systemd (Recommended)

```bash
# Create service file
sudo tee /etc/systemd/system/telegramdl.service <<EOF
[Unit]
Description=TelegramDL Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python3 bot.py
Restart=always
RestartSec=10
Environment=PATH=$(pwd)/venv/bin

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable telegramdl
sudo systemctl start telegramdl

# View logs
sudo journalctl -u telegramdl -f

# Restart
sudo systemctl restart telegramdl

# Stop
sudo systemctl stop telegramdl
```

### Running with screen

```bash
# Start screen session
screen -S telegramdl

# Run bot
python3 bot.py

# Detach: Ctrl+A, then Ctrl+D

# Re-attach
screen -r telegramdl
```

### Running with nohup

```bash
# Run in background
nohup python3 bot.py > bot.log 2>&1 &

# View logs
tail -f bot.log

# Stop
pkill -f "python3 bot.py"
```

---

## 📊 Platform Comparison

| Platform | Difficulty | Cost | Uptime | Best For |
|----------|------------|------|--------|----------|
| Colab | ⭐ Easy | Free | 12hrs | Testing, Small tasks |
| Docker | ⭐⭐ Medium | Varies | 24/7 | Self-hosted |
| Heroku | ⭐⭐ Medium | Free/Paid | 24/7 | Quick deploy |
| Render | ⭐⭐ Medium | Free/Paid | 24/7 | Easy setup |
| Koyeb | ⭐⭐ Medium | Free/Paid | 24/7 | Global access |
| VPS | ⭐⭐⭐ Hard | $5+/mo | 24/7 | Full control |

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Bot not starting | Check API_ID, API_HASH, BOT_TOKEN |
| FloodWaitError | Increase WAITING_TIME |
| Session expired | Regenerate with `/login` |
| MongoDB connection | Check DB_URI is correct |
| Port already in use | Change port or kill process |

### Logs Location

| Platform | How to View |
|----------|-------------|
| Docker | `docker logs -f telegramdl` |
| Heroku | `heroku logs --tail` |
| VPS (systemd) | `sudo journalctl -u telegramdl -f` |
| VPS (screen) | `screen -r telegramdl` |

---

## 🔄 Updates

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt

# Restart bot
# Docker: docker-compose restart
# VPS: sudo systemctl restart telegramdl
# Heroku: git push heroku main
```

---

**Last Updated**: 2026-01-19
