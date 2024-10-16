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


@app.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def set_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

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

    # Extract channel input, allowing for @ symbol
    channel_input = message.command[1].lstrip('@')
    
    try:
        channel_info = await client.get_chat(channel_input)
        channel_id = channel_info.id
        channel_title = channel_info.title
        channel_link = await app.export_chat_invite_link(channel_id)
        channel_username = (
            f"@{channel_info.username}" if channel_info.username else channel_link
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
                    "**🚫 I'ᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀɴɴᴇʟ.**\n\n"
                    "**➲ ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ᴡɪᴛʜ:**\n\n"
                    "**➥ Iɴᴠɪᴛᴇ Nᴇᴡ Mᴇᴍʙᴇʀs**\n\n"
                    "🛠️ **Tʜᴇɴ ᴜsᴇ /ғsᴜʙ <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ> ᴛᴏ sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.**"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "๏ ᴀᴅᴅ ᴍᴇ ɪɴ ᴄʜᴀɴɴᴇʟ ๏",
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
                f"**🎉 ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛ ᴛᴏ** [{channel_title}]({channel_username}) **ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**\n\n"
                f"**🆔 ᴄʜᴀɴɴᴇʟ ɪᴅ:** `{channel_id}`\n"
                f"**🖇️ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ:** [ɢᴇᴛ ʟɪɴᴋ]({channel_link})\n"
                f"**📊 ᴍᴇᴍʙᴇʀ ᴄᴏᴜɴᴛ:** {channel_members_count}\n"
                f"**👤 sᴇᴛ ʙʏ:** {set_by_user}"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("๏ ᴄʟᴏsᴇ ๏", callback_data="close_force_sub")]]
            ),
        )
        await asyncio.sleep(1)

    except Exception as e:
        await message.reply_photo(
            photo="https://envs.sh/TnZ.jpg",
            caption=(
                "**🚫 I'ᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀɴɴᴇʟ.**\n\n"
                "**➲ ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ᴡɪᴛʜ:**\n\n"
                "**➥ Iɴᴠɪᴛᴇ Nᴇᴡ Mᴇᴍʙᴇʀs**\n\n"
                "🛠️ **Tʜᴇɴ ᴜsᴇ /ғsᴜʙ <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ> ᴛᴏ sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.**"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "๏ ᴀᴅᴅ ᴍᴇ ɪɴ ᴄʜᴀɴɴᴇʟ ๏",
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


@app.on_message(filters.command("setcaption") & filters.group)
async def set_custom_caption(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if the user is the owner/admin or in SUDOERS
    member = await client.get_chat_member(chat_id, user_id)
    if not (
        member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or user_id in SUDOERS
    ):
        return await message.reply_text(
            "**Only the group owner, admins, or SUDOERS can use this command.**"
        )

    # Check if a caption is provided
    if len(message.command) < 2:
        return await message.reply_text(
            "**• نامەکە لەگەڵ فەرمان بینووسە یان ڕیپلەی بکە**\n\n- وشەی {name} بۆ نووسینی ناوی کەسەکە\n- وشەی {mention} یوزەری کەناڵەکە\n-دەتوانی ئەم نامەیە بەکاربھێنیت :\n\n`- سڵاو {name}\n- نامەکانت دەسڕدرێتەوە بەهۆی جۆین نەکردنت لە کەناڵی گرووپ\n- جۆینی کەناڵ بکە تاوەکو نامەکانت نەسڕدرێتەوە\n- کەناڵ : {mention}`"
        )

    caption = message.text.split(None, 1)[1]  # Extract the caption

    # Store the custom caption in MongoDB
    forcesub_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"custom_caption": caption}}, upsert=True
    )

    await message.reply_text(
        "**بە سەرکەوتوویی نامەی جۆین گۆڕا -🖱️**"
    )


@app.on_message(filters.command("setphoto") & filters.group)
async def set_custom_photo(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if the user is the owner/admin or in SUDOERS
    member = await client.get_chat_member(chat_id, user_id)
    if not (
        member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or user_id in SUDOERS
    ):
        return await message.reply_text(
            "**Only the group owner, admins, or SUDOERS can use this command.**"
        )

    # Check if the command is a reply to a message with a photo
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text(
            "**• تکایە ڕیپلەی وێنەی نوێ بکە**\n\n- وێنەکە لە گرووپ دابنێ\n- ڕیپلەی بکە و بنووسە گۆڕینی وێنە"
        )

    # Get the file ID of the photo from the replied message
    photo_id = message.reply_to_message.photo.file_id  

    # Store the custom photo ID in MongoDB
    forcesub_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"custom_photo_id": photo_id}}, upsert=True
    )

    await message.reply_text(
        "**بە سەرکەوتوویی وێنەی جۆین گۆڕا -📸**"
    )


async def check_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    # Retrieve custom photo and caption from the database
    custom_photo_id = forcesub_data.get("custom_photo_id")
    custom_caption = forcesub_data.get("custom_caption", "Join the channel to participate.")

    # Default caption if no custom caption is set
    default_caption = (
        "**✧¦ تۆ ئەندام نیت لەم کەناڵە {name}•\n\n\n**"
        "**✧¦ ناتوانی چات بکەیت لەم گرووپە•\n\n**"
        "**✧¦ سەرەتا پێویستە جۆینی کەناڵ بکەیت•\n\n**"
        "**✧¦ ئەگەر جۆین نەکەیت ئەوا چاتەکەت دەسڕمەوە و ئاگادارتەکەمەوە•\n\n\n**"
        "**✧¦ کەناڵی گرووپ {mention} ♥️•**"
    )

    # Use final_caption based on the presence of custom_caption
    final_caption = custom_caption if custom_caption else default_caption

    # If no custom photo is set, try to get the group photo
    if not custom_photo_id:
        if message.chat.photo:
            custom_photo_id = await app.download_media(message.chat.photo.big_file_id)

        # If no group photo, use the bot's own profile photo as fallback
        if not custom_photo_id:
            bot = await app.get_me()
            photobot = bot.photo.big_file_id
            custom_photo_id = await app.download_media(photobot)

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

        # Send message with a photo if custom_photo_id is set, otherwise send caption only
        if custom_photo_id:
            await message.reply_photo(
                photo=custom_photo_id,
                caption=final_caption.format(name=message.from_user.mention, mention=channel_username),
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
        else:
            await message.reply_text(
                final_caption.format(name=message.from_user.mention, mention=channel_username),
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
                disable_web_page_preview=True,
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
