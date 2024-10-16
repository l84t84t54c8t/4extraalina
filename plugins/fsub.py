import asyncio

from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from config import MONGO_DB_URI
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

fsubdb = MongoClient(MONGO_DB_URI)
forcesub_collection = fsubdb.status_db.status

DEFAULT_WARN_MESSAGE = (
    "**✧¦ تۆ ئەندام نیت لەم کەناڵە {name}•\n\n\n**"
    "**✧¦ ناتوانی چات بکەیت لەم گرووپە•\n\n**"
    "**✧¦ سەرەتا پێویستە جۆینی کەناڵ بکەیت•\n\n**"
    "**✧¦ ئەگەر جۆین نەکەیت ئەوا چاتەکەت دەسڕمەوە و ئاگادارتەکەمەوە•\n\n\n**"
    "**✧¦ کەناڵی گرووپ {channel_username} ♥️•**"
)


@app.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def set_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Check if the user is an owner, admin, or in SUDOERS
    member = await client.get_chat_member(chat_id, user_id)
    if not (
        member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or user_id in SUDOERS
    ):
        return await message.reply_text(
            "**Only the group owner, admins, or SUDOERS can use this command.**"
        )

    if len(message.command) == 2 and message.command[1].lower() in ["off", "disable"]:
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text(
            "**ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**"
        )

    if len(message.command) != 2:
        return await message.reply_text(
            "**ᴜsᴀɢᴇ: /ғsᴜʙ <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ> ᴏʀ /ғsᴜʙ ᴏғғ ᴛᴏ ᴅɪsᴀʙʟᴇ**"
        )

    channel_input = message.command[1]

    try:
        channel_info = await client.get_chat(channel_input)
        channel_id = channel_info.id
        channel_title = channel_info.title
        channel_link = await app.export_chat_invite_link(channel_id)
        channel_username = (
            f"{channel_info.username}" if channel_info.username else channel_link
        )
        channel_members_count = channel_info.members_count

        bot_id = (await client.get_me()).id
        bot_is_admin = False

        async for admin in app.get_chat_members(
            channel_id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            if admin.user.id == bot_id:
                bot_is_admin = True
                break

        if not bot_is_admin:
            await asyncio.sleep(1)
            return await message.reply_photo(
                photo="https://envs.sh/TnZ.jpg",
                caption=(
                    "**• ئەدمین نیم لەو کەناڵە 🚫.**\n\n"
                    "- تکایە بمکە ئەدمین\n"
                    "- لە ڕێگای دووگمەی خوارەوە\n"
                    "- دواتر فەرمانی جۆین دووبارە بکەوە\n\n"
                    "**• /fsub + یوزەری کەناڵت**"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "๏ زیادم بکە بۆ کەناڵ وەک ئەدمین ๏",
                                url=f"https://t.me/{app.username}?startchannel=s&admin=invite_users+manage_video_chats",
                            )
                        ]
                    ]
                ),
            )

        forcesub_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel_id": channel_id, "channel_username": channel_username}},
            upsert=True,
        )

        set_by_user = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else message.from_user.first_name
        )

        await message.reply_photo(
            photo="https://envs.sh/Tn_.jpg",
            caption=(
                f"**🎉 جۆینی ناچاری بۆ گرووپی [{channel_title}]({channel_username}) چالاککرا**\n\n"
                f"**🆔 ئایدی کەناڵ :** `{channel_id}`\n"
                f"**🖇️ لینکی کەناڵ : [لینکی کەناڵ] ({channel_link})**\n"
                f"**📊 ژماری ئەندام : {channel_members_count}**\n"
                f"**👤 چالاککرا لەلایەن : {set_by_user}**"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("๏ داخستن ๏", callback_data="close_force_sub")]]
            ),
        )
        await asyncio.sleep(1)

    except Exception as e:
        await message.reply_photo(
            photo="https://envs.sh/TnZ.jpg",
            caption=(
                "**• ئەدمین نیم لەو کەناڵە 🚫.**\n\n"
                "- تکایە بمکە ئەدمین\n"
                "- لە ڕێگای دووگمەی خوارەوە\n"
                "- دواتر فەرمانی جۆین دووبارە بکەوە\n\n"
                "**• /fsub + یوزەری کەناڵت**"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "๏ زیادم بکە بۆ کەناڵ وەک ئەدمین ๏",
                            url=f"https://t.me/{app.username}?startchannel=s&admin=invite_users+manage_video_chats",
                        )
                    ]
                ]
            ),
        )
        await asyncio.sleep(1)


@app.on_callback_query(filters.regex("close_force_sub"))
async def close_force_sub(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("ᴄʟᴏsᴇᴅ!")
    await callback_query.message.delete()


async def check_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    try:
        user_member = await app.get_chat_member(channel_id, user_id)
        if user_member:
            return
    except UserNotParticipant:
        await message.delete()
        if channel_username:
            channel_url = f"https://t.me/{channel_username}"
        else:
            invite_link = await app.export_chat_invite_link(channel_id)
            channel_url = invite_link
        await message.reply_photo(
            photo="https://envs.sh/Tn_.jpg",
            caption="(**✧¦ تۆ ئەندام نیت لەم کەناڵە {message.from_user.mention},•\n\n\n✧¦ ناتوانی چات بکەیت لەم گرووپە•\n\n✧¦ سەرەتا پێویستە جۆینی کەناڵ بکەیت•\n\n✧¦ ئەگەر جۆین نەکەیت ئەوا چاتەکەت دەسڕمەوە و ئاگادارتەکەمەوە•\n\n✧¦ من ئەم نامەیە دەنێرمەوە ئەگەر جۆین نەبیت\n\n✧¦ کەناڵی گرووپ {channel_username}, ♥️•**"),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ئێرە دابگرە بۆ جۆین کردن ✅", url=channel_url
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "𓆩⌁ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗟𝗜𝗡𝗔 ⌁𓆪",
                            url="https://t.me/GroupAlina",
                        )
                    ],
                ]
            ),
        )
        await asyncio.sleep(1)
    except ChatAdminRequired:
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text(
            "**🚫 I'ᴍ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ғᴏʀᴄᴇᴅ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ. ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.**"
        )


@app.on_message(filters.group)
async def enforce_forcesub(client: Client, message: Message):
    if not await check_forcesub(client, message):
        return


__MODULE__ = "ғsᴜʙ"
__HELP__ = """**
/fsub <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ> - sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.
/fsub off - ᴅɪsᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**
"""
