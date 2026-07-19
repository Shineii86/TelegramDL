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
        Flask web server for keep-alive and status page.
        Runs alongside the bot in Docker/VPS deployments.

    ROUTES:
        /        — Status landing page
        /health  — Health check endpoint
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from flask import Flask, render_template
import os

# ===========================================================================
#   FLASK APP INITIALIZATION
# ===========================================================================

app = Flask(__name__)

# ===========================================================================
#   PLATFORM DETECTION
# ---------------------------------------------------------------------------
#   Detects deployment platform for status page display.
#   Returns platform name as string.
# ===========================================================================


def detect_platform():
    """Detect current deployment platform.

    Returns:
        str: Platform name (Heroku, Render, Koyeb, Docker, VPS)

    Priority:
        1. Heroku (HEROKU env var)
        2. Render (RENDER env var)
        3. Koyeb (KOYEB env var)
        4. Docker (.dockerenv exists)
        5. VPS (default)
    """
    if os.environ.get("HEROKU"):
        return "Heroku"
    if os.environ.get("RENDER"):
        return "Render"
    if os.environ.get("KOYEB"):
        return "Koyeb"
    if os.path.exists("/app/.dockerenv"):
        return "Docker"
    return "VPS"

# ===========================================================================
#   ROUTES
# ===========================================================================


@app.route("/")
def home():
    """Render status landing page.

    Returns:
        HTML: Welcome page with bot status and platform info
    """
    return render_template("welcome.html", platform=detect_platform())


@app.route("/health")
def health():
    """Health check endpoint for load balancers.

    Returns:
        str: "OK" if server is running

    Tip:
        Use this endpoint for Docker HEALTHCHECK or
        load balancer health checks.
    """
    return "OK"

# ===========================================================================
#   SCRIPT ENTRY POINT
# ---------------------------------------------------------------------------
#   Runs Flask server on port from PORT env var (default: 5000).
# ===========================================================================


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ===========================================================================
#   END OF APP
# ===========================================================================
