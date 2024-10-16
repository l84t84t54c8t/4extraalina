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
            "**Please provide a caption to set as the custom force subscription caption.**"
        )

    caption = message.text.split(None, 1)[1]  # Extract the caption

    # Store the custom caption in MongoDB
    forcesub_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"custom_caption": caption}}, upsert=True
    )

    await message.reply_text(
        "**Custom caption has been set successfully for force subscription.**"
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

    # Check if there is a photo in the message
    if not message.photo:
        return await message.reply_text(
            "**Please send a photo to set it as the custom force subscription photo.**"
        )

    photo_id = message.photo.file_id  # Get the file ID of the photo

    # Store the custom photo ID in MongoDB
    forcesub_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"custom_photo_id": photo_id}}, upsert=True
    )

    await message.reply_text(
        "**Custom photo has been set successfully for force subscription.**"
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
    custom_caption = forcesub_data.get(
        "custom_caption", "Join the channel to participate."
    )

    # If no custom photo is set, try to get the group photo
    if not custom_photo_id:
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

        await message.reply_photo(
            photo=custom_photo_id,
            caption=(
                f"**👋 ʜᴇʟʟᴏ {message.from_user.mention},**\n\n"
                f"{custom_caption}\n\n"
                f"**[ᴄʜᴀɴɴᴇʟ]({channel_url}) ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.**"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ئێرە دابگرە بۆ جۆین کردن ✅", url=channel_url)]]
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
