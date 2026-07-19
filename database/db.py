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

Version:    2.0.0
Python:     3.10+
Framework:  Kurigram (Pyrogram Fork)

Disclaimer:
    This bot is for educational purposes only.
    Use responsibly and respect Telegram's Terms of Service.
"""

from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME


class Database:
    def __init__(self, uri, db_name):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.users = self.db.users

    # ============ USER MANAGEMENT ============

    async def add_user(self, id, name):
        await self.users.update_one(
            {"id": id},
            {"$setOnInsert": {
                "id": id,
                "name": name,
                "session": None,
                "is_premium": False,
                "premium_expiry": None,
                "is_banned": False,
                "daily_usage": 0,
                "limit_reset_time": datetime.now(),
                "total_saves": 0,
                "thumbnail": None,
                "caption": None,
                "dump_chat": None,
                "bot_token": None,
                "bot_client": None,
                "rename_tag": None,
                "delete_words": [],
                "replace_words": {},
                "topic_id": None,
            }},
            upsert=True
        )

    async def is_user_exist(self, id):
        user = await self.users.find_one({"id": id})
        return bool(user)

    async def delete_user(self, id):
        await self.users.delete_one({"id": id})

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def get_all_users(self):
        return self.users.find({})

    # ============ SESSION MANAGEMENT ============

    async def set_session(self, id, session):
        await self.users.update_one({"id": id}, {"$set": {"session": session}})

    async def get_session(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("session")
        return None

    # ============ PREMIUM SYSTEM ============

    async def is_premium(self, id):
        user = await self.users.find_one({"id": id})
        if not user:
            return False
        if not user.get("is_premium"):
            return False
        expiry = user.get("premium_expiry")
        if expiry:
            if isinstance(expiry, str):
                expiry = datetime.fromisoformat(expiry)
            if expiry < datetime.now():
                await self.users.update_one({"id": id}, {"$set": {"is_premium": False, "premium_expiry": None}})
                return False
        return True

    async def add_premium(self, id, days):
        user = await self.users.find_one({"id": id})
        if user and user.get("is_premium"):
            expiry = user.get("premium_expiry")
            if isinstance(expiry, str):
                expiry = datetime.fromisoformat(expiry)
            if expiry and expiry > datetime.now():
                new_expiry = expiry + timedelta(days=days)
            else:
                new_expiry = datetime.now() + timedelta(days=days)
        else:
            new_expiry = datetime.now() + timedelta(days=days)
        await self.users.update_one(
            {"id": id},
            {"$set": {"is_premium": True, "premium_expiry": new_expiry}}
        )

    async def remove_premium(self, id):
        await self.users.update_one(
            {"id": id},
            {"$set": {"is_premium": False, "premium_expiry": None}}
        )

    async def get_premium_info(self, id):
        user = await self.users.find_one({"id": id})
        if not user:
            return None
        return {
            "is_premium": user.get("is_premium", False),
            "expiry": user.get("premium_expiry"),
        }

    # ============ DAILY LIMITS ============

    async def check_daily_limit(self, id):
        user = await self.users.find_one({"id": id})
        if not user:
            return True
        if user.get("is_premium"):
            return True
        reset_time = user.get("limit_reset_time")
        if isinstance(reset_time, str):
            reset_time = datetime.fromisoformat(reset_time)
        if reset_time and datetime.now() - reset_time > timedelta(hours=24):
            await self.users.update_one(
                {"id": id},
                {"$set": {"daily_usage": 0, "limit_reset_time": datetime.now()}}
            )
            return True
        daily_usage = user.get("daily_usage", 0)
        return daily_usage < 10

    async def increment_daily_usage(self, id):
        await self.users.update_one(
            {"id": id},
            {"$inc": {"daily_usage": 1, "total_saves": 1}}
        )

    async def get_daily_usage(self, id):
        user = await self.users.find_one({"id": id})
        if not user:
            return 0
        return user.get("daily_usage", 0)

    # ============ BAN SYSTEM ============

    async def is_banned(self, id):
        user = await self.users.find_one({"id": id})
        if not user:
            return False
        return user.get("is_banned", False)

    async def ban_user(self, id):
        await self.users.update_one({"id": id}, {"$set": {"is_banned": True}})

    async def unban_user(self, id):
        await self.users.update_one({"id": id}, {"$set": {"is_banned": False}})

    # ============ THUMBNAIL ============

    async def set_thumbnail(self, id, file_id):
        await self.users.update_one({"id": id}, {"$set": {"thumbnail": file_id}})

    async def get_thumbnail(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("thumbnail")
        return None

    async def delete_thumbnail(self, id):
        await self.users.update_one({"id": id}, {"$set": {"thumbnail": None}})

    # ============ CUSTOM CAPTION ============

    async def set_caption(self, id, caption):
        await self.users.update_one({"id": id}, {"$set": {"caption": caption}})

    async def get_caption(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("caption")
        return None

    async def delete_caption(self, id):
        await self.users.update_one({"id": id}, {"$set": {"caption": None}})

    # ============ DUMP CHAT ============

    async def set_dump_chat(self, id, chat_id):
        await self.users.update_one({"id": id}, {"$set": {"dump_chat": chat_id}})

    async def get_dump_chat(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("dump_chat")
        return None

    async def delete_dump_chat(self, id):
        await self.users.update_one({"id": id}, {"$set": {"dump_chat": None}})

    # ============ TRAFFIC STATS ============

    async def add_traffic(self, id, size):
        await self.users.update_one(
            {"id": id},
            {"$inc": {"total_saves": 1}}
        )

    async def get_total_saves(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("total_saves", 0)
        return 0

    # ============ CUSTOM BOT ============

    async def set_bot_token(self, id, bot_token):
        await self.users.update_one({"id": id}, {"$set": {"bot_token": bot_token}})

    async def get_bot_token(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("bot_token")
        return None

    async def delete_bot_token(self, id):
        await self.users.update_one({"id": id}, {"$set": {"bot_token": None}})

    # ============ RENAME TAG ============

    async def set_rename_tag(self, id, tag):
        await self.users.update_one({"id": id}, {"$set": {"rename_tag": tag}})

    async def get_rename_tag(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("rename_tag")
        return None

    async def delete_rename_tag(self, id):
        await self.users.update_one({"id": id}, {"$set": {"rename_tag": None}})

    # ============ WORD RULES ============

    async def set_delete_words(self, id, words):
        await self.users.update_one({"id": id}, {"$set": {"delete_words": words}})

    async def get_delete_words(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("delete_words", [])
        return []

    async def set_replace_words(self, id, replacements):
        await self.users.update_one({"id": id}, {"$set": {"replace_words": replacements}})

    async def get_replace_words(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("replace_words", {})
        return {}

    # ============ TOPIC GROUP ============

    async def set_topic_id(self, id, topic_id):
        await self.users.update_one({"id": id}, {"$set": {"topic_id": topic_id}})

    async def get_topic_id(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("topic_id")
        return None

    async def delete_topic_id(self, id):
        await self.users.update_one({"id": id}, {"$set": {"topic_id": None}})


class MockDatabase:
    """Fallback when no DB_URI is configured. All operations are no-ops."""
    async def add_user(self, id, name): pass
    async def is_user_exist(self, id): return False
    async def set_session(self, id, session): pass
    async def get_session(self, id): return None
    async def delete_user(self, id): pass
    async def total_users_count(self): return 0
    async def get_all_users(self):
        if False:
            yield
    async def is_premium(self, id): return True
    async def add_premium(self, id, days): pass
    async def remove_premium(self, id): pass
    async def get_premium_info(self, id): return None
    async def check_daily_limit(self, id): return True
    async def increment_daily_usage(self, id): pass
    async def get_daily_usage(self, id): return 0
    async def is_banned(self, id): return False
    async def ban_user(self, id): pass
    async def unban_user(self, id): pass
    async def set_thumbnail(self, id, file_id): pass
    async def get_thumbnail(self, id): return None
    async def delete_thumbnail(self, id): pass
    async def set_caption(self, id, caption): pass
    async def get_caption(self, id): return None
    async def delete_caption(self, id): pass
    async def set_dump_chat(self, id, chat_id): pass
    async def get_dump_chat(self, id): return None
    async def delete_dump_chat(self, id): pass
    async def add_traffic(self, id, size): pass
    async def get_total_saves(self, id): return 0
    async def set_bot_token(self, id, bot_token): pass
    async def get_bot_token(self, id): return None
    async def delete_bot_token(self, id): pass
    async def set_rename_tag(self, id, tag): pass
    async def get_rename_tag(self, id): return None
    async def delete_rename_tag(self, id): pass
    async def set_delete_words(self, id, words): pass
    async def get_delete_words(self, id): return []
    async def set_replace_words(self, id, replacements): pass
    async def get_replace_words(self, id): return {}
    async def set_topic_id(self, id, topic_id): pass
    async def get_topic_id(self, id): return None
    async def delete_topic_id(self, id): pass


if DB_URI:
    db = Database(DB_URI, DB_NAME)
else:
    db = MockDatabase()
