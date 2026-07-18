from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME


class Database:
    def __init__(self, uri, db_name):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.users = self.db.users

    async def add_user(self, id, name):
        await self.users.insert_one({"id": id, "name": name, "session": None})

    async def is_user_exist(self, id):
        user = await self.users.find_one({"id": id})
        return bool(user)

    async def set_session(self, id, session):
        await self.users.update_one({"id": id}, {"$set": {"session": session}})

    async def get_session(self, id):
        user = await self.users.find_one({"id": id})
        if user:
            return user.get("session")
        return None

    async def delete_user(self, id):
        await self.users.delete_one({"id": id})

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def get_all_users(self):
        return self.users.find({})


if DB_URI:
    db = Database(DB_URI, DB_NAME)
else:
    db = None
