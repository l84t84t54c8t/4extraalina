from threading import RLock
from AlinaMusic.core.mongo import mongodb

# Initialize the locks collection
locksdb = mongodb.locks
INSERTION_LOCK = RLock()

lock_t = ["bot", "anti_c_send", "anti_fwd",
          "anti_fwd_u", "anti_fwd_c", "anti_links"]


class LOCKS:
    """Class to store locks"""

    def __init__(self) -> None:
        self.db = locksdb

    async def insert_lock_channel(self, chat: int, locktype: str):
        """
        locktypes: all, bot, anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        if locktype == "all":
            for i in lock_t:
                curr = await self.db.find_one({"chat_id": chat, "locktype": i})
                if curr:
                    continue
                if i in ["anti_fwd_u", "anti_fwd_c"]:
                    continue
                await self.db.insert_one({"chat_id": chat, "locktype": i})
            return True

        curr = await self.db.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            return False

        async with INSERTION_LOCK:
            hmm = await self.merge_u_and_c(chat, locktype)
            if not hmm:
                await self.db.insert_one({"chat_id": chat, "locktype": locktype})
        return True

    async def remove_lock_channel(self, chat: int, locktype: str):
        """
        locktypes: all, bot, anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        if locktype == "all":
            for i in lock_t:
                curr = await self.db.find_one({"chat_id": chat, "locktype": i})
                if curr:
                    await self.db.delete_one({"chat_id": chat, "locktype": i})
            return True

        curr = await self.db.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            async with INSERTION_LOCK:
                await self.db.delete_one({"chat_id": chat, "locktype": locktype})
            return True
        else:
            return False

    async def get_lock_channel(self, chat: int, locktype: str = "all"):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links, bot
        """
        if locktype not in lock_t + ["all"]:
            return False

        if locktype != "all":
            curr = await self.db.find_one(
                {"chat_id": chat, "locktype": locktype})
            return bool(curr)

        curr = self.db.find({"chat_id": chat})
        if not curr:
            return None

        to_return = {
            "anti_channel": False,
            "anti_fwd": {
                "user": False,
                "chat": False
            },
            "anti_links": False,
            "bot": False
        }
        async for i in curr:
            if i["locktype"] == "anti_c_send":
                to_return["anti_channel"] = True
            elif i["locktype"] == "anti_fwd":
                to_return["anti_fwd"]["user"] = to_return["anti_fwd"]["chat"] = True
            elif i["locktype"] == "anti_fwd_u":
                to_return["anti_fwd"]["user"] = True
            elif i["locktype"] == "anti_fwd_c":
                to_return["anti_fwd"]["chat"] = True
            elif i["locktype"] == "anti_links":
                to_return["anti_links"] = True
            elif i["locktype"] == "bot":
                to_return["bot"] = True
        return to_return

    async def merge_u_and_c(self, chat: int, locktype: str):
        if locktype == "anti_fwd_u":
            curr = await self.db.find_one({"chat_id": chat, "locktype": "anti_fwd_c"})
        elif locktype == "anti_fwd_c":
            curr = await self.db.find_one({"chat_id": chat, "locktype": "anti_fwd_u"})
        else:
            return False

        if curr:
            await self.db.delete_one({"chat_id": chat, "locktype": locktype})
            await self.db.insert_one({"chat_id": chat, "locktype": "anti_fwd"})
            return True
        else:
            return False

    async def is_particular_lock(self, chat: int, locktype: str):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        return bool(await self.db.find_one({"chat_id": chat, "locktype": locktype}))
