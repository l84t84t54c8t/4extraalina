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


@app.on_message(filters.command(["fsub", "join", "on"]) & filters.group)
async def set_forcesub(client: Client, message: Message):
    bot = await app.get_me()
    photobot = bot.photo.big_file_id
    botphoto = await app.download_media(photobot)
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if not (
        member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or user_id in SUDOERS
    ):
        return await message.reply_text(
            "**• ناتوانی فەرمان بەکاربهێنیت**\n- تەنیا خاوەنی گرووپ و ئەدمینەکان\n- ئەم فەرمانە بەکابێنن",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𓆩⌁ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗟𝗜𝗡𝗔 ⌁𓆪", url=f"https://t.me/GroupAlina"
                        )
                    ]
                ]
            ),
        )

    if len(message.command) == 2 and message.command[1].lower() in ["off", "disable"]:
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text(
            "**• بە سەرکەوتوویی جۆینی ناچاری ناچالاککرا .**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𓆩⌁ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗟𝗜𝗡𝗔 ⌁𓆪", url=f"https://t.me/GroupAlina"
                        )
                    ]
                ]
            ),
        )
    if len(message.command) != 2:
        return await message.reply_text(
            "**• جۆین چالاك نەکراوە لەم گرووپە**\n- بۆ چالاککردنی /fsub یان /join + @یوزەری کەناڵ\n- بۆ ناچالاکردنی جۆینی ناچاری /off\n\n**• بۆ هەرکێشەیەك سەردانی گرووپی ئەلینا بکە**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𓆩⌁ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗟𝗜𝗡𝗔 ⌁𓆪", url=f"https://t.me/GroupAlina"
                        )
                    ]
                ]
            ),
        )

    # Extract channel input, allowing for @ symbol
    channel_input = message.command[1].lstrip("@")

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
                photo=botphoto,
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
            photo=botphoto,
            caption=(
                f"**🎉 جۆینی ناچاری بۆ [{channel_title}]({channel_username}) چالاککرا**\n\n"
                f"**🆔 ئایدی کەناڵ :** `{channel_id}`\n"
                f"**🖇️ لینکی کەناڵ :** [کەناڵ]({channel_link})\n"
                f"**📊 ژماری ئەندام : {channel_members_count}**\n"
                f"**👤 چالاککرا لەلایەن : {set_by_user}**"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("๏ ᴄʟᴏsᴇ ๏", callback_data="close_force_sub")]]
            ),
        )
        await asyncio.sleep(1)

    except Exception as e:
        await message.reply_photo(
            photo=botphoto,
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


@app.on_message(
    filters.command(
        ["/setcaption", "/setmessage", "دانانی نامە", "گۆڕینی نامە", "گۆرینی نامە"], ""
    )
    & filters.group
)
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
            "**• ناتوانی فەرمان بەکاربهێنیت**\n- تەنیا خاوەنی گرووپ و ئەدمینەکان\n- ئەم فەرمانە بەکابێنن",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𓆩⌁ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗟𝗜𝗡𝗔 ⌁𓆪", url=f"https://t.me/GroupAlina"
                        )
                    ]
                ]
            ),
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

    await message.reply_text("**بە سەرکەوتوویی نامەی جۆین گۆڕا -🖱️**")


@app.on_message(
    filters.command(["/setphoto", "دانانی وێنە", "گۆڕینی وێنە", "گۆرینی وێنە"], "")
    & filters.group
)
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
            "**• ناتوانی فەرمان بەکاربهێنیت**\n- تەنیا خاوەنی گرووپ و ئەدمینەکان\n- ئەم فەرمانە بەکابێنن",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𓆩⌁ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗟𝗜𝗡𝗔 ⌁𓆪", url=f"https://t.me/GroupAlina"
                        )
                    ]
                ]
            ),
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

    await message.reply_text("**بە سەرکەوتوویی وێنەی جۆین گۆڕا -📸**")


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
    custom_caption = forcesub_data.get("custom_caption")

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
                caption=final_caption.format(
                    name=message.from_user.mention, mention=channel_username
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "ئێرە دابگرە بۆ جۆین کردن ✅", url="https://t.me/{channel_username}",
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
            # Only reply with caption if no photo is set
            await message.reply_text(
                final_caption.format(
                    name=message.from_user.mention, mention=channel_username
                ),
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
            "**🚫 من ئەدمین نیم لە کەناڵ\n🚫 جۆینی ناچاری ناچالاککراوە**"
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
