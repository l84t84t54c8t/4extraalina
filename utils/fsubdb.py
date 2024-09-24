from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from config import CHANNEL as CHANNELOWNER
from config import GROUP as GROUPOWNER

channeldb = mongodb.ch
CHANNEL = {}
groupdb = mongodb.gr
GROUP = {}
mustdb = mongodb.must
must = {}


# Bot group
async def get_group(chat_id):
    name = GROUP.get(chat_id)
    if not name:
        bot = groupdb.find_one({"chat_id": chat_id})
        if not bot:
            return GROUPOWNER
        GROUP[chat_id] = bot["group"]
        return bot["group"]
    return name


async def set_group(chat_id: str, group: str):
    GROUP[chat_id] = group
    groupdb.update_one({"chat_id": chat_id}, {"$set": {"group": group}}, upsert=True)


# Bot channel
async def get_channel(chat_id):
    name = CHANNEL.get(chat_id)
    if not name:
        bot = channeldb.find_one({"chat_id": chat_id})
        if not bot:
            return CHANNELOWNER
        CHANNEL[chat_id] = bot["channel"]
        return bot["channel"]
    return name


async def set_channel(chat_id: str, channel: str):
    CHANNEL[chat_id] = channel
    channeldb.update_one(
        {"chat_id": chat_id}, {"$set": {"channel": channel}}, upsert=True
    )


async def must_join(chat_id):
    name = must.get(chat_id)
    if not name:
        bot = mustdb.find_one({"chat_id": chat_id})
        if not bot:
            return "off"
        must[chat_id] = bot["getmust"]
        return bot["getmust"]
    return name


async def set_must(chat_id: str, m: str):
    if m == "• ناچالاککردنی جۆینی ناچاری •":
        ii = "off"
    else:
        ii = "on"
    must[chat_id] = ii
    mustdb.update_one({"chat_id": chat_id}, {"$set": {"getmust": ii}}, upsert=True)


async def joinch(message):
    ii = await must_join(message._app.username)
    if ii == "off":
        return
    cch = await get_channel(message._app.username)
    ch = cch.replace("https://t.me/", "")
    try:
        await app.get_chat_member(ch, message.from_user.id)
    except UserNotParticipant:
        try:
            await message.reply(
                f"**◗⋮◖ پێویستە جۆینی کەناڵ بکەیت\n\n◗⋮◖ کەناڵی بۆت : « {cch} »**",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("جۆینی کەناڵ بکە ◗⋮◖", url=f"{cch}"),
                        ],
                    ]
                ),
            )
            return True
        except Exception as a:
            print(a)
    except Exception as a:
        print(a)
