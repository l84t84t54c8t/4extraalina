from AlinaMusic.core.mongo import mongodb

approve_collection = mongodb.approves


class Approve:
    """Class for managing Approves in Chats in Bot."""

    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id

    async def check_approve(self, user_id: int) -> bool:
        chat_data = await approve_collection.find_one({"_id": self.chat_id})
        if not chat_data or not chat_data.get("users"):
            return False
        return any(user[0] == user_id for user in chat_data["users"])

    async def add_approve(self, user_id: int, user_name: str) -> bool:
        if not await self.check_approve(user_id):
            await approve_collection.update_one(
                {"_id": self.chat_id},
                {"$push": {"users": (user_id, user_name)}},
                upsert=True,
            )
            return True
        return False

    async def remove_approve(self, user_id: int) -> bool:
        if await self.check_approve(user_id):
            await approve_collection.update_one(
                {"_id": self.chat_id},
                {"$pull": {"users": {"$elemMatch": {"0": user_id}}}},
            )
            return True
        return False

    async def unapprove_all(self):
        await approve_collection.delete_one({"_id": self.chat_id})

    async def list_approved(self):
        chat_data = await approve_collection.find_one({"_id": self.chat_id})
        return chat_data.get("users", []) if chat_data else []

    async def count_approved(self) -> int:
        approved_users = await self.list_approved()
        return len(approved_users)

    async def migrate_chat(self, new_chat_id: int):
        chat_data = await approve_collection.find_one({"_id": self.chat_id})
        if chat_data:
            chat_data["_id"] = new_chat_id
            await approve_collection.insert_one(chat_data)
            await approve_collection.delete_one({"_id": self.chat_id})

    @staticmethod
    async def count_all_approved() -> int:
        total = 0
        async for chat_data in approve_collection.find():
            total += len(chat_data.get("users", []))
        return total

    @staticmethod
    async def count_approved_chats() -> int:
        return await approve_collection.count_documents({"users.0": {"$exists": True}})

    @staticmethod
    async def repair_db():
        async for chat_data in approve_collection.find():
            if "users" not in chat_data:
                await approve_collection.update_one(
                    {"_id": chat_data["_id"]},
                    {"$set": {"users": []}},
                )
