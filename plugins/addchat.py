import time
from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from pyrogram import filters
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


@app.on_message(filters.regex("^زیادکردنی چات$"), group=120)
@adminsOnly("can_change_info")
async def add_chat(client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)

    # Step 1: Ask for the keyword
    await m.reply(
        "**ئێستا ئەو وشەیە بنێرە کە دەتەوێت زیادی بکەیت ئەزیزم🖤•**",
        reply_to_message_id=m.id,
    )

    # Function to wait for a specific user's message
    async def wait_for_user_message(user_id, chat_id, timeout=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = await client.listen(chat_id)
            if response.from_user.id == user_id:
                return response
        raise TimeoutError

    try:
        # Wait for the user's keyword
        keyword_response = await wait_for_user_message(m.from_user.id, m.chat.id)
    except TimeoutError:
        await m.reply("**کاتەکەت تەواو بوو، دووبارە هەوڵبدەرەوە♥**")
        return

    keyword = keyword_response.text
    if keyword in data:
        await m.reply(
            "**ببورە ئەم وشەیە پێشتر زیادکراوە💔**",
            reply_to_message_id=keyword_response.id,
        )
        return

    # Step 2: Ask for the response to the keyword
    await m.reply(
        "**ئێستا دەتوانیت یەکێك لەمانە زیادبکەیت بۆ وڵامدانەوە💘\n( دەق، وێنە، گیف، ڤیدیۆ، ڤۆیس، گۆرانی، دەنگ، فایل، ستیکەر)**",
        reply_to_message_id=keyword_response.id,
    )

    try:
        # Wait for the user's response content
        content_response = await wait_for_user_message(m.from_user.id, m.chat.id)
    except TimeoutError:
        await m.reply("**کاتەکەت تەواو بوو، دووبارە هەوڵبدەرەوە♥**")
        return

    # Process the response content
    if content_response.text:
        data[keyword] = f"text&{content_response.text}"
    elif content_response.photo:
        data[keyword] = f"photo&{content_response.photo.file_id}"
    elif content_response.video:
        data[keyword] = f"video&{content_response.video.file_id}"
    elif content_response.animation:
        data[keyword] = f"animation&{content_response.animation.file_id}"
    elif content_response.voice:
        data[keyword] = f"voice&{content_response.voice.file_id}"
    elif content_response.audio:
        data[keyword] = f"audio&{content_response.audio.file_id}"
    elif content_response.document:
        data[keyword] = f"document&{content_response.document.file_id}"
    elif content_response.sticker:
        data[keyword] = f"sticker&{content_response.sticker.file_id}"
    else:
        await content_response.reply(
            f"**تەنیا دەتوانی ئەمانە بنێریت\n(وشە، وێنە، گیف، ڤیدیۆ، ڤۆیس، دەنگ، گۆرانی، فایل، ستیکەر) ♥⚡**",
            quote=True,
        )
        return

    # Save the updated data
    await save_chat_data(cid, data)
    await content_response.reply(
        f"**چات زیادکرا بە ناوی ↤︎ ({keyword}) ♥•**", quote=True
    )


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
