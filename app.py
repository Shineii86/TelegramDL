#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TelegramDL - Advanced Telegram Downloader Bot

Copyright (c) 2024-2026 Shinei Nouzen (Shineii86)
Licensed under the MIT License

Author:    Shinei Nouzen
GitHub:    https://github.com/Shineii86/TelegramDL
Telegram:  https://t.me/Shineii86
Email:     ikx7a@hotmail.com

Description:
    Advanced Telegram Restricted Content Downloader with Premium System,
    yt-dlp Integration, File Splitting, Custom Bots & More.

Framework:  Kurigram (Pyrogram Fork)

Disclaimer:
    This bot is for educational purposes only.
    Use responsibly and respect Telegram's Terms of Service.
"""

from flask import Flask, render_template
import os

app = Flask(__name__)


def detect_platform():
    if os.environ.get("RENDER"):
        return "Render"
    if os.environ.get("HEROKU"):
        return "Heroku"
    if os.environ.get("KOYEB"):
        return "Koyeb"
    if os.path.exists("/app/.dockerenv"):
        return "Docker"
    return "VPS"


@app.route("/")
def home():
    return render_template("welcome.html", platform=detect_platform())


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
