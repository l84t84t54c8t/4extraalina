from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import filters

# MongoDB collection for managing chat-related data
chat_data_collection = mongodb.chat_data


async def get_chat_data(chat_id):
    chat_data = await chat_data_collection.find_one({"chat_id": chat_id})
    return chat_data["data"] if chat_data else {}


async def save_chat_data(chat_id, data):
    await chat_data_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"data": data}}, upsert=True
    )


@app.on_message(filters.regex("^زیادکردنی چات$"))
async def add_chat(client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)  # Use await for the async function

    t = await m.chat.ask(
        "**ئێستا ئەو وشەیە بنێرە کە دەتەوێت زیادی بکەیت ئەزیزم🖤•**",
        filters=filters.text & filters.user(m.from_user.id),
        reply_to_message_id=m.id,
    )
    if t.text in data:
        await m.reply("**ببورە ئەم وشەیە پێشتر زیادکراوە💔**", reply_to_message_id=t.id)
    else:
        tt = await m.chat.ask(
            "**ئێستا دەتوانیت یەکێك لەمانە زیادبکەیت بۆ وڵامدانەوە💘\n( وشە، وێنە، گیف، ڤیدیۆ، ڤۆیس، گۆرانی، دەنگ، فایل)**",
            filters=filters.user(t.from_user.id),
            reply_to_message_id=t.id,
        )
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
        else:
            await tt.reply(
                f"**تەنیا دەتوانی ئەمانە بنێریت\n(وشە، وێنە، گیف، ڤیدیۆ، ڤۆیس، دەنگ، گۆرانی، فایل) ‌♥⚡**",
                quote=True,
            )
            return

        await save_chat_data(cid, data)  # Use await for the async function
        await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)


@app.on_message(filters.regex("^چاتەکان$"))
async def list_chats(client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)  # Use await for the async function
    if data:
        response = ""
        for i, (key, value) in enumerate(data.items(), 1):
            type_label = value.split("&", 1)[0]
            type_map = {
                "text": "**وشە**",
                "photo": "**وێنە**",
                "video": "**ڤیدیۆ**",
                "animation": "**گیف**",
                "voice": "**ڤۆیس**",
                "audio": "**گۆرانی**",
                "document": "**فایل**",
            }
            response += (
                f'{i} => {key} ~ {type_map.get(type_label, "ناونامەی نەزانراو")}\n'
            )
        await m.reply(response)
    else:
        await m.reply("**هیچ چاتێکی زیادکراو نییە♥️**•")


@app.on_message(filters.regex("^سڕینەوەی چاتەکان$"))
async def clear_chats(client, m):
    cid = str(m.chat.id)
    await save_chat_data(cid, {})  # Use await for the async function
    await m.reply("**بە سەرکەوتوویی هەموو چاتەکان سڕدرانەوە♥️✅**")


@app.on_message(filters.regex("^سڕینەوەی چات$"))
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


@app.on_message(filters.text)
async def respond(client, m):
    cid = str(m.chat.id)
    data = await get_chat_data(cid)  # Use await for the async function
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
