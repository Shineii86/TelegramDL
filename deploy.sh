#!/bin/bash

# TelegramDL VPS Deployment Script
# Run: bash deploy.sh

set -e

echo "========================================="
echo "   TelegramDL - VPS Deployment Setup"
echo "========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[*] Installing Python3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "[*] Installing ffmpeg..."
    sudo apt update
    sudo apt install -y ffmpeg
fi

# Check git
if ! command -v git &> /dev/null; then
    echo "[*] Installing git..."
    sudo apt update
    sudo apt install -y git
fi

echo "[*] Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[*] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[*] Creating .env file if not exists..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
API_ID=
API_HASH=
BOT_TOKEN=
MONGO_DB=
OWNER_ID=
LOG_GROUP=
FORCE_SUB=
STRING=
LOGIN_SYSTEM=True
FREE_DAILY_LIMIT=10
FREE_MAX_FILE_SIZE_MB=2000
PREMIUM_MAX_FILE_SIZE_MB=4000
ADMIN_CONTACT=
JOIN_LINK=
EOF
    echo "[!] Please edit .env file with your credentials"
    nano .env
fi

echo "[*] Creating systemd service..."
sudo tee /etc/systemd/system/telegramdl.service > /dev/null << EOF
[Unit]
Description=TelegramDL Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "[*] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable telegramdl
sudo systemctl start telegramdl

echo "========================================="
echo "   Deployment Complete!"
echo "========================================="
echo ""
echo "Service Status: sudo systemctl status telegramdl"
echo "View Logs:      sudo journalctl -u telegramdl -f"
echo "Restart:        sudo systemctl restart telegramdl"
echo "Stop:           sudo systemctl stop telegramdl"
echo ""
echo "Flask status page: http://localhost:5000"
echo "========================================="
