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
        MongoDB database layer using Motor async driver.
        Handles all user data, sessions, settings, and statistics.

    COLLECTIONS:
        users — User profiles, sessions, settings, stats

    FEATURES:
        FEATURE: USER_MANAGEMENT
        FEATURE: SESSION_MANAGEMENT
        FEATURE: PREMIUM_SYSTEM
        FEATURE: DAILY_LIMITS
        FEATURE: BAN_SYSTEM
        FEATURE: THUMBNAIL_STORAGE
        FEATURE: CAPTION_STORAGE
        FEATURE: DUMP_CHAT
        FEATURE: CUSTOM_BOT
        FEATURE: RENAME_TAG
        FEATURE: WORD_RULES
        FEATURE: TOPIC_GROUP
        FEATURE: PAYMENT_SYSTEM
============================================================================
"""

# ===========================================================================
#   IMPORTS
# ===========================================================================

from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME, FREE_DAILY_LIMIT

# ===========================================================================
#   DATABASE CLASS
# ---------------------------------------------------------------------------
#   Main database class with all CRUD operations.
#   Uses Motor for async MongoDB operations.
#
#   NOTE: All methods are async for non-blocking I/O
# ===========================================================================


class Database:
    def __init__(self, uri, db_name):
        """Initialize database connection.

        Args:
            uri: MongoDB connection string
            db_name: Database name

        Returns:
            None

        Note:
            Creates connection pool on initialization
        """
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.users = self.db.users

    # =======================================================================
    #   FEATURE: USER_MANAGEMENT
    # =======================================================================

    async def add_user(self, id, name):
        """Add new user to database.

        Args:
            id: Telegram user ID
            name: User's first name

        Returns:
            None

        Note:
            Uses $setOnInsert to avoid overwriting existing data
        """
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
        """Check if user exists.

        Args:
            id: Telegram user ID

        Returns:
            bool: True if user exists
        """
        user = await self.users.find_one({"id": id})
        return bool(user)

    async def delete_user(self, id):
        """Delete user from database.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.delete_one({"id": id})

    async def total_users_count(self):
        """Get total user count.

        Returns:
            int: Total number of users
        """
        return await self.users.count_documents({})

    async def get_all_users(self):
        """Get all users cursor.

        Returns:
            AsyncIOMotorCursor: Cursor for iterating users
        """
        return self.users.find({})

    # =======================================================================
    #   FEATURE: SESSION_MANAGEMENT
    # =======================================================================

    async def set_session(self, id, session):
        """Set user session string (encrypted).

        Args:
            id: Telegram user ID
            session: Pyrogram session string or None

        Returns:
            None
        """
        from utils.encrypt import encrypt_session
        encrypted = encrypt_session(session) if session else None
        await self.users.update_one({"id": id}, {"$set": {"session": encrypted}})

    async def get_session(self, id):
        """Get user session string (decrypted).

        Args:
            id: Telegram user ID

        Returns:
            str: Session string or None
        """
        user = await self.users.find_one({"id": id})
        if user:
            encrypted = user.get("session")
            if encrypted:
                from utils.encrypt import decrypt_session
                try:
                    return decrypt_session(encrypted)
                except Exception:
                    return encrypted
        return None

    # =======================================================================
    #   FEATURE: PREMIUM_SYSTEM
    # =======================================================================

    async def is_premium(self, id):
        """Check if user has active premium.

        Args:
            id: Telegram user ID

        Returns:
            bool: True if premium and not expired

        Note:
            Auto-deactivates expired premium
        """
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
        """Add premium subscription.

        Args:
            id: Telegram user ID
            days: Number of days to add

        Returns:
            None

        Note:
            Extends existing premium if active
        """
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
        """Remove premium subscription.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one(
            {"id": id},
            {"$set": {"is_premium": False, "premium_expiry": None}}
        )

    async def get_premium_info(self, id):
        """Get premium information.

        Args:
            id: Telegram user ID

        Returns:
            dict: Premium info (is_premium, expiry) or None
        """
        user = await self.users.find_one({"id": id})
        if not user:
            return None
        return {
            "is_premium": user.get("is_premium", False),
            "expiry": user.get("premium_expiry"),
        }

    # =======================================================================
    #   FEATURE: DAILY_LIMITS
    # =======================================================================

    async def check_daily_limit(self, id):
        """Check if user exceeded daily limit.

        Args:
            id: Telegram user ID

        Returns:
            bool: True if within limit

        Note:
            Resets counter after 24 hours
            Premium users have unlimited
        """
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
        return daily_usage < FREE_DAILY_LIMIT

    async def increment_daily_usage(self, id):
        """Increment daily usage counter.

        Args:
            id: Telegram user ID

        Returns:
            None

        Note:
            Also increments total_saves
        """
        await self.users.update_one(
            {"id": id},
            {"$inc": {"daily_usage": 1, "total_saves": 1}}
        )

    async def get_daily_usage(self, id):
        """Get current daily usage.

        Args:
            id: Telegram user ID

        Returns:
            int: Number of downloads today
        """
        user = await self.users.find_one({"id": id})
        if not user:
            return 0
        return user.get("daily_usage", 0)

    # =======================================================================
    #   FEATURE: BAN_SYSTEM
    # =======================================================================

    async def is_banned(self, id):
        """Check if user is banned.

        Args:
            id: Telegram user ID

        Returns:
            bool: True if banned
        """
        user = await self.users.find_one({"id": id})
        if not user:
            return False
        return user.get("is_banned", False)

    async def ban_user(self, id):
        """Ban a user.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"is_banned": True}})

    async def unban_user(self, id):
        """Unban a user.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"is_banned": False}})

    # =======================================================================
    #   FEATURE: THUMBNAIL_STORAGE
    # =======================================================================

    async def set_thumbnail(self, id, file_id):
        """Set custom thumbnail.

        Args:
            id: Telegram user ID
            file_id: Telegram file_id of photo

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"thumbnail": file_id}})

    async def get_thumbnail(self, id):
        """Get custom thumbnail.

        Args:
            id: Telegram user ID

        Returns:
            str: file_id or None
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("thumbnail")
        return None

    async def delete_thumbnail(self, id):
        """Delete custom thumbnail.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"thumbnail": None}})

    # =======================================================================
    #   FEATURE: CAPTION_STORAGE
    # =======================================================================

    async def set_caption(self, id, caption):
        """Set custom caption template.

        Args:
            id: Telegram user ID
            caption: Caption template string

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"caption": caption}})

    async def get_caption(self, id):
        """Get custom caption template.

        Args:
            id: Telegram user ID

        Returns:
            str: Caption template or None
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("caption")
        return None

    async def delete_caption(self, id):
        """Delete custom caption.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"caption": None}})

    # =======================================================================
    #   FEATURE: DUMP_CHAT
    # =======================================================================

    async def set_dump_chat(self, id, chat_id):
        """Set dump chat for auto-forward.

        Args:
            id: Telegram user ID
            chat_id: Target chat ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"dump_chat": chat_id}})

    async def get_dump_chat(self, id):
        """Get dump chat.

        Args:
            id: Telegram user ID

        Returns:
            str: Chat ID or None
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("dump_chat")
        return None

    async def delete_dump_chat(self, id):
        """Delete dump chat.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"dump_chat": None}})

    # =======================================================================
    #   FEATURE: TRAFFIC_STATS
    # =======================================================================

    async def add_traffic(self, id, size):
        """Increment total saves.

        Args:
            id: Telegram user ID
            size: File size (unused, for compatibility)

        Returns:
            None
        """
        await self.users.update_one(
            {"id": id},
            {"$inc": {"total_saves": 1}}
        )

    async def get_total_saves(self, id):
        """Get total saves count.

        Args:
            id: Telegram user ID

        Returns:
            int: Total files saved
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("total_saves", 0)
        return 0

    # =======================================================================
    #   FEATURE: CUSTOM_BOT
    # =======================================================================

    async def set_bot_token(self, id, bot_token):
        """Set custom bot token.

        Args:
            id: Telegram user ID
            bot_token: Bot token string

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"bot_token": bot_token}})

    async def get_bot_token(self, id):
        """Get custom bot token.

        Args:
            id: Telegram user ID

        Returns:
            str: Bot token or None
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("bot_token")
        return None

    async def delete_bot_token(self, id):
        """Delete custom bot token.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"bot_token": None}})

    # =======================================================================
    #   FEATURE: RENAME_TAG
    # =======================================================================

    async def set_rename_tag(self, id, tag):
        """Set rename tag.

        Args:
            id: Telegram user ID
            tag: Rename tag string

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"rename_tag": tag}})

    async def get_rename_tag(self, id):
        """Get rename tag.

        Args:
            id: Telegram user ID

        Returns:
            str: Rename tag or None
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("rename_tag")
        return None

    async def delete_rename_tag(self, id):
        """Delete rename tag.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"rename_tag": None}})

    # =======================================================================
    #   FEATURE: WORD_RULES
    # =======================================================================

    async def set_delete_words(self, id, words):
        """Set words to delete from captions.

        Args:
            id: Telegram user ID
            words: List of words to delete

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"delete_words": words}})

    async def get_delete_words(self, id):
        """Get words to delete.

        Args:
            id: Telegram user ID

        Returns:
            list: List of words
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("delete_words", [])
        return []

    async def set_replace_words(self, id, replacements):
        """Set word replacements.

        Args:
            id: Telegram user ID
            replacements: Dict of {old: new} replacements

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"replace_words": replacements}})

    async def get_replace_words(self, id):
        """Get word replacements.

        Args:
            id: Telegram user ID

        Returns:
            dict: Replacements dict
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("replace_words", {})
        return {}

    # =======================================================================
    #   FEATURE: TOPIC_GROUP
    # =======================================================================

    async def set_topic_id(self, id, topic_id):
        """Set topic ID.

        Args:
            id: Telegram user ID
            topic_id: Topic ID string

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"topic_id": topic_id}})

    async def get_topic_id(self, id):
        """Get topic ID.

        Args:
            id: Telegram user ID

        Returns:
            str: Topic ID or None
        """
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("topic_id")
        return None

    async def delete_topic_id(self, id):
        """Delete topic ID.

        Args:
            id: Telegram user ID

        Returns:
            None
        """
        await self.users.update_one({"id": id}, {"$set": {"topic_id": None}})

    # =======================================================================
    #   FEATURE: PAYMENT_SYSTEM
    # =======================================================================

    async def create_payment_request(self, user_id, request_id, plan, days, price):
        """Create a new payment request.

        Args:
            user_id: Telegram user ID
            request_id: Unique request identifier
            plan: Plan name (weekly/monthly/yearly/lifetime)
            days: Number of premium days
            price: Plan price

        Returns:
            None
        """
        await self.users.insert_one({
            "payment_request": True,
            "user_id": user_id,
            "request_id": request_id,
            "plan": plan,
            "days": days,
            "price": price,
            "status": "pending",
            "created_at": datetime.now()
        })

    async def get_payment_request(self, request_id):
        """Get payment request by ID.

        Args:
            request_id: Unique request identifier

        Returns:
            dict: Payment request or None
        """
        return await self.users.find_one({
            "payment_request": True,
            "request_id": request_id
        })

    async def update_payment_status(self, request_id, status):
        """Update payment request status.

        Args:
            request_id: Unique request identifier
            status: New status (approved/rejected/pending)

        Returns:
            None
        """
        await self.users.update_one(
            {"payment_request": True, "request_id": request_id},
            {"$set": {"status": status, "updated_at": datetime.now()}}
        )

    async def get_pending_payments(self):
        """Get all pending payment requests.

        Returns:
            list: List of pending requests
        """
        cursor = self.users.find({
            "payment_request": True,
            "status": "pending"
        })
        return await cursor.to_list(length=50)

    async def add_payment_history(self, user_id, request_id, plan, days, price, status):
        """Add entry to payment history.

        Args:
            user_id: Telegram user ID
            request_id: Unique request identifier
            plan: Plan name
            days: Number of premium days
            price: Plan price
            status: Payment status (approved/rejected)

        Returns:
            None
        """
        await self.users.insert_one({
            "payment_history": True,
            "user_id": user_id,
            "request_id": request_id,
            "plan": plan,
            "days": days,
            "price": price,
            "status": status,
            "created_at": datetime.now()
        })

    async def get_payment_history(self, user_id=None):
        """Get payment history.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            list: List of payment history entries
        """
        query = {"payment_history": True}
        if user_id:
            query["user_id"] = user_id
        cursor = self.users.find(query).sort("created_at", -1)
        return await cursor.to_list(length=50)

    async def get_user_payments(self, user_id):
        """Get all payments for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            list: List of user's payments
        """
        cursor = self.users.find({
            "payment_history": True,
            "user_id": user_id
        }).sort("created_at", -1)
        return await cursor.to_list(length=20)

    # =======================================================================
    #   MOCK DATABASE
    # =======================================================================
#   Fallback when no DB_URI is configured.
#   All operations are no-ops.
#
#   NOTE: Allows bot to run without database
# ===========================================================================


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
    async def create_payment_request(self, user_id, request_id, plan, days, price): pass
    async def get_payment_request(self, request_id): return None
    async def update_payment_status(self, request_id, status): pass
    async def get_pending_payments(self): return []
    async def add_payment_history(self, user_id, request_id, plan, days, price, status): pass
    async def get_payment_history(self, user_id=None): return []
    async def get_user_payments(self, user_id): return []

# ===========================================================================
#   DATABASE INSTANCE
# ---------------------------------------------------------------------------
#   Uses real Database if DB_URI is set, otherwise MockDatabase
# ===========================================================================


if DB_URI:
    db = Database(DB_URI, DB_NAME)
else:
    db = MockDatabase()

# ===========================================================================
#   END OF DATABASE MODULE
# ===========================================================================
