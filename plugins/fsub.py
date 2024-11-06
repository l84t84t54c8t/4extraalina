import asyncio
import logging

from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.plugins.play.play import joinch
from config import MONGO_DB_URI
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

fsubdb = MongoClient(MONGO_DB_URI)
forcesub_collection = fsubdb.status_db.status


@app.on_message(filters.command(["/fsub", "/join", "on.iq", "/on"], "") & filters.group)
async def set_forcesub(client: Client, message: Message):
    if await joinch(message):
        return
    try:
        bot = await client.get_me()
        photobot = bot.photo.big_file_id if bot.photo else None
        if photobot:
            botphoto = await client.download_media(photobot)

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

        if len(message.command) == 2 and message.command[1].lower() in [
            "off",
            "disable",
        ]:
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

        # Check if force subscription is already enabled
        existing_fsub = forcesub_collection.find_one({"chat_id": chat_id})
        if existing_fsub:
            # If already enabled, send a message and return
            return await message.reply_text(
                "**• جۆینی ناچاری چالاککراوە ✅.**\n- دەتوانی کەناڵی جۆین بگؤڕیت بۆ کەناڵێکی تر\n- سەرەتا ناچالاکی بکە :\n- بەم شێوەیە :\n- /join یان /on + off\n\n- دواتر دووبارە جۆینی ناچاری چالاکبکە\n- /join یان /on + یوزەری کەناڵ\n\n**• بۆتی گۆرانی : @IQMCBOT**",
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
                "**• جۆین چالاك نەکراوە لەم گرووپە**\n- بۆ چالاککردنی /fsub یان /join + @یوزەری کەناڵ\n- بۆ ناچالاکردنی جۆینی ناچاری /join off\n\n**• بۆ هەرکێشەیەك سەردانی گرووپی ئەلینا بکە**",
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

        # Extract channel input
        channel_input = message.command[1]

        try:
            channel_info = await client.get_chat(channel_input)
            channel_id = channel_info.id
            channel_title = channel_info.title
            channel_link = await client.export_chat_invite_link(channel_id)
            channel_username = (
                channel_info.username if channel_info.username else channel_link
            )
            channel_members_count = channel_info.members_count

            bot_id = (await client.get_me()).id
            bot_is_admin = False
            async for admin in client.get_chat_members(
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
                {
                    "$set": {
                        "channel_id": channel_id,
                        "channel_username": channel_username,
                    }
                },
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
                    f"**🆔 ئایدی کەناڵ :** {channel_id}\n"
                    f"**🖇️ لینکی کەناڵ :** [کەناڵ]({channel_link})\n"
                    f"**📊 ژماری ئەندام : {channel_members_count}**\n"
                    f"**👤 چالاککرا لەلایەن : {set_by_user}**"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "๏ داخستن ๏", callback_data="close_force_sub"
                            )
                        ]
                    ]
                ),
            )

            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error processing channel information: {e}")
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
                                "๏ زیادم بکە بۆ کەناڵ وەک ئەدمین ๏",
                                url=f"https://t.me/{app.username}?startchannel=s&admin=invite_users+manage_video_chats",
                            )
                        ]
                    ]
                ),
            )
            await asyncio.sleep(1)

    except Exception as e:
        logging.error(f"Error in set_forcesub: {e}")
        await message.reply_text("An error occurred. Please try again later.")


@app.on_callback_query(filters.regex("close_force_sub"))
async def close_force_sub(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("داخرا!")
    await callback_query.message.delete()


@app.on_message(
    filters.command(
        ["/setcaption", "/setmessage", "دانانی نامە", "گۆڕینی نامە", "گۆرینی نامە"], ""
    )
)
async def set_custom_caption(client: Client, message: Message):
    if await joinch(message):
        return
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
            "**• نامەکە لەگەڵ فەرمان بینووسە یان ڕیپلەی بکە**\n\n- وشەی {name} بۆ نووسینی ناوی کەسەکە\n- وشەی {mention} یوزەری کەناڵەکە\n-دەتوانی ئەم نامەیە بەکاربھێنیت :\n\n- سڵاو {name}\n- نامەکانت دەسڕدرێتەوە بەهۆی جۆین نەکردنت لە کەناڵی گرووپ\n- جۆینی کەناڵ بکە تاوەکو نامەکانت نەسڕدرێتەوە\n- کەناڵ : @{mention}"
        )

    caption = message.text.split(None, 1)[1]  # Extract the caption

    # Store the custom caption in MongoDB
    forcesub_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"custom_caption": caption}}, upsert=True
    )

    await message.reply_text("**بە سەرکەوتوویی نامەی جۆین گۆڕا -🖱️**")


@app.on_message(
    filters.command(["/setphoto", "دانانی وێنە", "گۆڕینی وێنە", "گۆرینی وێنە"], "")
)
async def set_custom_photo(client: Client, message: Message):
    if await joinch(message):
        return
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

@app.on_message(filters.command(["/fsubs", "جۆینی ناچاری"], "") & SUDOERS)
async def get_fsub_stats(client: Client, message: Message):
    if await joinch(message):
        return
    try:
        # Count the number of groups where Force Subscription is enabled
        enabled_fsubs = forcesub_collection.count_documents({})

        await message.reply_text(
            f"**• چالاکی جۆینی ناچاری بۆتی ئەلینا**\n\n- بۆ  {enabled_fsubs} گرووپ چالاککراوە",
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
    except Exception as e:
        logging.error(f"Error fetching Force Subscription stats: {e}")
        await message.reply_text("An error occurred while fetching stats.")


@app.on_message(
    filters.command(["/fsubstats", "/fsubinfo", "زانیاری جۆینی ناچاری"], "") & SUDOERS
)
async def get_fsub_stats(client: Client, message: Message):
    if await joinch(message):
        return
    # Fetch all groups where FSub is enabled from the database
    enabled_groups = forcesub_collection.find({"channel_id": {"$exists": True}})

    if forcesub_collection.count_documents({"channel_id": {"$exists": True}}) == 0:
        return await message.reply_text("**• جۆینی ناچاری چالاک نەکراوە**")

    # Prepare the response message
    text = "**• زانیاری گرووپ و کەناڵی جۆینی ناچاری :**\n\n"

    for group in enabled_groups:
        chat_id = group["chat_id"]
        group_info = await client.get_chat(
            chat_id
        )  # Fetch group information from Telegram

        group_title = group_info.title
        group_username = group_info.username if group_info.username else "N/A"

        channel_id = group["channel_id"]
        channel_info = await client.get_chat(
            channel_id
        )  # Fetch channel information from Telegram
        channel_title = channel_info.title
        channel_username = channel_info.username if channel_info.username else "N/A"

        # Append group and channel details to the message
        text += (
            f"**ناوی گرووپ : {group_title}**\n"
            f"**ئایدی گرووپ :** `{chat_id}`\n"
            f"**یوزەری گرووپ : @{group_username if group_username != 'N/A' else 'None'}**\n\n"
            f"**ناوی کەناڵ : {channel_title}**\n"
            f"**ئایدی کەناڵ :** `{channel_id}`\n"
            f"**یوزەری کەناڵ : @{channel_username if channel_username != 'N/A' else 'None'}**\n\n"
        )

    await message.reply_text(
        text,
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

async def check_forcesub(client: Client, message: Message):
    if message.from_user is None:
        return False  # Exit early if no user is associated with the message

    user_id = message.from_user.id
    chat_id = message.chat.id

    # Fetch force subscription data from the database
    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return  # If no force sub data is found, exit early

    channel_id = forcesub_data.get("channel_id")
    channel_username = forcesub_data.get("channel_username")

    # Retrieve custom photo and caption from the database
    custom_photo_id = forcesub_data.get("custom_photo_id")
    custom_caption = forcesub_data.get("custom_caption")

    # Default caption if no custom caption is set
    default_caption = (
        "**✧¦ تۆ ئەندام نیت لەم کەناڵە {name}•\n\n\n**"
        "**✧¦ ناتوانی چات بکەیت لەم گرووپە•\n\n**"
        "**✧¦ سەرەتا پێویستە جۆینی کەناڵ بکەیت•\n\n**"
        "**✧¦ ئەگەر جۆین نەکەیت ئەوا چاتەکەت دەسڕمەوە و ئاگادارتەکەمەوە•\n\n\n**"
        "**✧¦ کەناڵی گرووپ @{mention} ♥️•**"
    )

    # Use final_caption based on the presence of custom_caption
    final_caption = custom_caption if custom_caption else default_caption

    try:
        # Check if the user is a member of the channel
        user_member = await app.get_chat_member(channel_id, user_id)
        if user_member:
            return  # User is a member, no further action needed
    except UserNotParticipant:
        # If user is not a participant, delete the message and send force sub
        # message
        await message.delete()

        # Create the channel link (username or invite link)
        if channel_username:
            channel_url = f"https://t.me/{channel_username}"
        else:
            invite_link = await app.export_chat_invite_link(channel_id)
            channel_url = invite_link

        # Send message with photo if custom_photo_id is available, otherwise
        # send caption only
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
            # Send only the text if no photo is available
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
        # Handle the case where the bot is not an admin in the channel
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text(
            "**🚫 من ئەدمین نیم لە کەناڵ\n🚫 جۆینی ناچاری ناچالاککراوە**"
        )

@app.on_message(filters.group, group=30)
async def enforce_forcesub(client: Client, message: Message):
    if not await check_forcesub(client, message):
        return



__MODULE__ = "ғsᴜʙ"
__HELP__ = """**
/fsub <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ> - sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.
/fsub off - ᴅɪsᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**
"""
