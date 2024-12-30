import asyncio
import logging
import os

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

        # Ask the user for the channel
        t = await message.chat.ask(
            "**• تکایە یوزەری کەناڵ یان لینکەکە دابنێ:**\n\n"
            "- نمونە: @ChannelUsername یان https://t.me/ChannelUsername",
            filters=filters.text & filters.user(user_id),
            reply_to_message_id=message.id,
        )

        channel_input = t.text

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
                return await t.reply_photo(
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
            await t.reply_photo(
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
            await t.reply_photo(
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

    # Ask the user for the custom caption
    t = await message.chat.ask(
        "**• تکایە نامەی جۆین بنێرە:**\n\n"
        "- وشەی {name} بۆ نووسینی ناوی کەسەکە\n"
        "- وشەی {mention} یوزەری کەناڵەکە\n"
        "- ئەم نامەیە دەتوانیت بەکاربھێنیت :\n\n"
        "- سڵاو {name}\n"
        "- نامەکانت دەسڕدرێتەوە بەهۆی جۆین نەکردنت لە کەناڵی گرووپ\n"
        "- جۆینی کەناڵ بکە تاوەکو نامەکانت نەسڕدرێتەوە\n"
        "- کەناڵ : @{mention}",
        filters=filters.text & filters.user(user_id),
        reply_to_message_id=message.id,
    )

    caption = t.text  # Get the caption text from the user's reply

    # Store the custom caption in MongoDB
    forcesub_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"custom_caption": caption}}, upsert=True
    )

    await t.reply("**بە سەرکەوتوویی نامەی جۆین گۆڕا -🖱️**")


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

    # Ask the user for a new photo
    prompt = await message.chat.ask(
        "**• ئێستا وێنەی جۆین بنێرە**\n\n",
        filters=filters.photo & filters.user(user_id),
        reply_to_message_id=message.id,
    )

    # Get the photo file ID from the user's reply
    photo = prompt.photo
    photo_id = photo.file_id

    # Store the custom photo ID in MongoDB
    forcesub_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"custom_photo_id": photo_id}}, upsert=True
    )

    await prompt.reply("**بە سەرکەوتوویی وێنەی جۆین گۆڕا -📸**")


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

    # Prepare the text content for the file
    content = "• زانیاری گرووپ و کەناڵی جۆینی ناچاری:\n\n"

    for group in enabled_groups:
        chat_id = group["chat_id"]
        try:
            # Fetch group information
            group_info = await client.get_chat(chat_id)
            group_title = group_info.title
            group_username = group_info.username if group_info.username else "N/A"
        except Exception:
            group_title = "Unknown"
            group_username = "N/A"

        channel_id = group["channel_id"]
        try:
            # Fetch channel information
            channel_info = await client.get_chat(channel_id)
            channel_title = channel_info.title
            channel_username = channel_info.username if channel_info.username else "N/A"
        except Exception:
            channel_title = "Unknown"
            channel_username = "N/A"

        # Append group and channel details to the file content
        content += (
            f"**ناوی گرووپ:** {group_title}\n"
            f"**ئایدی گرووپ:** `{chat_id}`\n"
            f"**یوزەری گرووپ:** @{group_username if group_username != 'N/A' else 'None'}\n\n"
            f"**ناوی کەناڵ:** {channel_title}\n"
            f"**ئایدی کەناڵ:** `{channel_id}`\n"
            f"**یوزەری کەناڵ:** @{channel_username if channel_username != 'N/A' else 'None'}\n\n"
        )

    # Save the content to a file
    file_path = "fsub_stats.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    # Send the file as a document
    await message.reply_document(
        file_path,
        caption="**• زانیاری گرووپ و کەناڵی جۆینی ناچاری بە وردەکاری:**",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("𓆩⌁ 𝗚𝗥𝗢𝗨𝗣 𝗔𝗟𝗜𝗡𝗔 ⌁𓆪", url="https://t.me/GroupAlina")]]
        ),
    )

    # Clean up by removing the file after sending
    os.remove(file_path)


async def check_forcesub(client: Client, message: Message):
    if message.from_user is None:
        return False  # Exit early if no user is associated with the message

    user_id = message.from_user.id
    chat_id = message.chat.id

    # Fetch force subscription data from the database
    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return False  # Exit early if no force sub data is found

    channel_id = forcesub_data.get("channel_id")
    channel_username = forcesub_data.get("channel_username")

    # Validate channel_id
    if not channel_id:
        return False  # Exit early if channel_id is missing or invalid

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
        user_member = await client.get_chat_member(channel_id, user_id)
        if user_member:
            return True  # User is a member
    except UserNotParticipant:
        # If user is not a participant, delete the message and send force sub
        # message
        await message.delete()

        # Create the channel link (username or invite link)
        channel_url = (
            f"https://t.me/{channel_username}"
            if channel_username
            else await client.export_chat_invite_link(channel_id)
        )

        # Send message with photo if custom_photo_id is available, otherwise
        # send caption only
        if custom_photo_id:
            await message.reply_photo(
                photo=custom_photo_id,
                caption=final_caption.format(
                    name=message.from_user.mention,
                    mention=channel_username,
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
            await message.reply_text(
                final_caption.format(
                    name=message.from_user.mention,
                    mention=channel_username,
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
        await message.reply_text(
            "**🚫 من ئەدمین نیم لە کەناڵ\n🚫 جۆینی ناچاری ناچالاککراوە**"
        )
        return False

    return False


@app.on_message(filters.group, group=30)
async def enforce_forcesub(client: Client, message: Message):
    if not await check_forcesub(client, message):
        return


__MODULE__ = "ғsᴜʙ"
__HELP__ = """**
/fsub <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ> - sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.
/fsub off - ᴅɪsᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**
"""
