import asyncio

from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.permissions import adminsOnly

# MongoDB collection for managing chat-related data
chat_data_collection = mongodb.chat_data


async def get_chat_data(chat_id: int):
    chat_data = await chat_data_collection.find_one({"chat_id": chat_id})
    return chat_data["data"] if chat_data else {}


async def save_chat_data(chat_id: int, data):
    await chat_data_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"data": data}}, upsert=True
    )



async def wait_for_message(client: Client, chat_id: int, filters: filters.Filter, timeout: int = 60):
    """
    Waits for a message with specific filters in a particular chat.
    
    Parameters:
        - client: The Pyrogram client instance.
        - chat_id: The chat ID where the message should be received.
        - filters: Filters to match the message (e.g., text, user).
        - timeout: Maximum time (in seconds) to wait for the message.

    Returns:
        - Message object: The received message if it matches the filters, else None if timeout is reached.
    """
    # Create a condition for the message to match the filters
    async def check_message(message):
        return message.chat.id == chat_id and filters(message)

    # Wait for the message that matches the filters
    try:
        message = await client.listen(chat_id, filters=filters, timeout=timeout)
        return message
    except asyncio.TimeoutError:
        return None  # Return None if no message matches within the timeout period

# Example usage within your bot command
@app.on_message(filters.regex("^زیادکردنی چات$") & filters.group, group=120)
async def add_chat(client: Client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)

    # Step 1: Ask for the keyword
    question1 = await m.reply(
        "**ئێستا ئەو وشەیە بنێرە کە دەتەوێت زیادی بکەیت ئەزیزم🖤•**",
        reply_to_message_id=m.id,
    )
    
    # Wait for the user's response for the keyword
    t = await wait_for_message(
        client,
        chat_id=m.chat.id,
        filters=filters.text & filters.user(m.from_user.id),
        timeout=60  # 60 seconds timeout for receiving the message
    )

    if t and t.text in data:
        await m.reply("**ببورە ئەم وشەیە پێشتر زیادکراوە💔**", reply_to_message_id=t.id)
        return
    elif t is None:
        await m.reply("**ببورە، کاتی ئەم پەیامە تێپەڕیە. تکایە دابەزەری ئەم کاتەیە.**", reply_to_message_id=m.id)
        return

    # Step 2: Ask for the response
    question2 = await m.reply(
        "**ئێستا دەتوانیت یەکێك لەمانە زیادبکەیت بۆ وڵامدانەوە💘\n( دەق، وێنە، گیف، ڤیدیۆ، ڤۆیس، گۆرانی، دەنگ، فایل، ستیکەر)**",
        reply_to_message_id=t.id,
    )

    # Wait for the user's response for the content
    tt = await wait_for_message(
        client,
        chat_id=m.chat.id,
        filters=filters.user(m.from_user.id),
        timeout=60  # 60 seconds timeout
    )

    if tt is None:
        await m.reply("**ببورە، کاتی ئەم پەیامە تێپەڕیە. تکایە دابەزەری ئەم کاتەیە.**", reply_to_message_id=question2.id)
        return

    # Step 3: Process the content
    if tt.text:
        data[t.text] = f"text&{tt.text}"
    elif tt.photo:
        data[t.text] = f"photo&{tt.photo.file_id}"
    elif tt.video:
        data[t.text] = f"video&{tt.video.file_id}"
    elif tt.animation:
        data[t.text] = f"animation&{tt.animation.file_id}"
    elif tt.voice:
        data[t.text] = f"voice&{tt.voice.file_id}"
    elif tt.audio:
        data[t.text] = f"audio&{tt.audio.file_id}"
    elif tt.document:
        data[t.text] = f"document&{tt.document.file_id}"
    elif tt.sticker:
        data[t.text] = f"sticker&{tt.sticker.file_id}"
    else:
        await tt.reply(
            f"**تەنیا دەتوانی ئەمانە بنێریت\n(وشە، وێنە، گیف، ڤیدیۆ، ڤۆیس، دەنگ، گۆرانی، فایل، ستیکەر) ♥⚡**",
            quote=True,
        )
        return

    # Step 4: Save and confirm
    await save_chat_data(cid, data)
    await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)

@app.on_message(filters.regex("^چاتەکان$"), group=121)
@adminsOnly("can_change_info")
async def list_chats(client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)  # Use await for the async function
    if data:
        response = ""
        for i, (key, value) in enumerate(data.items(), 1):
            type_label = value.split("&", 1)[0]
            type_map = {
                "text": "دەق",
                "photo": "وێنە",
                "video": "ڤیدیۆ",
                "animation": "گیف",
                "voice": "ڤۆیس",
                "audio": "گۆرانی",
                "document": "فایل",
                "sticker": "ستیکەر",
            }
            response += (
                f'**{i} => {key} ~ {type_map.get(type_label, "ناونامەی نەزانراو")}\n**'
            )
        await m.reply(response)
    else:
        await m.reply("**هیچ چاتێکی زیادکراو نییە♥️**•")


@app.on_message(filters.regex("^سڕینەوەی چاتەکان$"), group=122)
@adminsOnly("can_change_info")
async def clear_chats(client, m):
    cid = m.chat.id

    # Check if the user is either an owner or a sudoer
    member = await client.get_chat_member(cid, m.from_user.id)
    if m.from_user.id not in SUDOERS and member.status != ChatMemberStatus.OWNER:
        await m.reply("❌ تەنها خاوەنی گرووپ دەتوانێت ئەم فرمانە بەکاربهێنێ.")
        return

    # Send confirmation message with buttons
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("❌ نەخێر", callback_data="cancel_clear_chats"),
                InlineKeyboardButton("✅ بەلێ", callback_data="confirm_clear_chats"),
            ]
        ]
    )
    await m.reply(
        "**ئایا دڵنیایت کە دەتەوێ هەموو چاتەکان بسڕیتەوە؟**",
        reply_markup=buttons,
    )


@app.on_callback_query(filters.regex("^confirm_clear_chats$"))
async def confirm_clear_chats(client, callback_query):
    cid = callback_query.message.chat.id

    # Check if the user pressing the button is either an owner or a sudoer
    if callback_query.from_user.id not in SUDOERS:
        member = await client.get_chat_member(cid, callback_query.from_user.id)
        if member.status != ChatMemberStatus.OWNER:
            await callback_query.answer(
                "❌ تەنها خاوەنی گرووپ دەتوانێت ئەم فرمانە بەکاربهێنێ.", show_alert=True
            )
            return

    # Clear chats
    await save_chat_data(str(cid), {})  # Use await for the async function
    await callback_query.message.edit("**بە سەرکەوتوویی هەموو چاتەکان سڕدرانەوە♥️✅**")


@app.on_callback_query(filters.regex("^cancel_clear_chats$"))
async def cancel_clear_chats(client, callback_query):
    cid = callback_query.message.chat.id

    # Check if the user pressing the button is either an owner or a sudoer
    if callback_query.from_user.id not in SUDOERS:
        member = await client.get_chat_member(cid, callback_query.from_user.id)
        if member.status != ChatMemberStatus.OWNER:
            await callback_query.answer(
                "❌ تەنها خاوەنی گرووپ دەتوانێت ئەم فرمانە بەکاربهێنێ.", show_alert=True
            )
            return

    await callback_query.message.edit("**❌ سڕینەوەی چاتەکان هەڵوەشایەوە.**")


@app.on_message(filters.regex("^سڕینەوەی چات$"), group=123)
@adminsOnly("can_change_info")
async def delete_chat(client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)  # Use await for the async function
    t = await m.chat.ask(
        "** ئێستا ئەو وشەیە بنێرە کە زیادتکردووە🎈•**",
        filters=filters.text & filters.user(m.from_user.id),
        reply_to_message_id=m.id,
    )
    if t.text in data:
        del data[t.text]
        await save_chat_data(cid, data)  # Use await for the async function
        await t.reply("**بە سەرکەوتوویی چاتە زیادکراوەکە سڕایەوە♥️**")
    else:
        await t.reply("**هیچ چاتێك بەردەست نییە ئەزیزم👾**")


@app.on_message(filters.text, group=125)
async def respond(client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)
    if m.text in data:
        type_label, content = data[m.text].split("&", 1)
        if type_label == "text":
            await m.reply(content)
        elif type_label == "photo":
            await m.reply_photo(content)
        elif type_label == "video":
            await m.reply_video(content)
        elif type_label == "animation":
            await m.reply_animation(content)
        elif type_label == "voice":
            await m.reply_voice(content)
        elif type_label == "audio":
            await m.reply_audio(content)
        elif type_label == "document":
            await m.reply_document(content)
        elif type_label == "sticker":
            await m.reply_sticker(content)
