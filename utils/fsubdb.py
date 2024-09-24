from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from config import CHANNEL as CHANNELOWNER
from config import GROUP as GROUPOWNER
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
        bot = await groupdb.find_one({"chat_id": chat_id})
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
        bot = await channeldb.find_one({"chat_id": chat_id})
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
        bot = await mustdb.find_one({"chat_id": chat_id})  # Ensure awaiting here
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
    # Fetch bot's username using the Pyrogram app instance
    me = await app.get_me()  # This returns the bot's information
    username = me.username  # Extract the bot's username

    ii = await must_join(username)  # Use the bot's username in must_join
    if ii == "off":
        return

    cch = await get_channel(username)  # Use the bot's username to get the channel
    ch = cch.replace("https://t.me/", "")

    try:
        # Check if the user is a participant in the channel
        await app.get_chat_member(ch, message.from_user.id)
    except UserNotParticipant:
        try:
            # If the user isn't a participant, send a message with a link to the channel
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
