import json

from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import Client, filters, idle

addchats_collection = mongodb.addchat


def get_chat_data(chat_id):
    chat_data = addchats_collection.find_one({"chat_id": chat_id})
    return chat_data["data"] if chat_data else {}


def save_chat_data(chat_id, data):
    addchats_collection.update_one(
        {"chat_id": chat_id}, {"$set": {"data": data}}, upsert=True
    )


@app.on_message(filters.regex("^زیادکردنی چات$"))
async def add_chat(client, m):
    cid = str(m.chat.id)
    data = get_chat_data(cid)

    t = await m.chat.ask(
        "**ئێستا ئەو وشەیە بنێرە کە دەتەوێت زیادی بکەیت ئەزیزم🖤•**",
        filters=filters.text & filters.user(m.from_user.id),
        reply_to_message_id=m.id,
    )
    if t.text in data:
        await app.send_message(
            cid, "**ببورە ئەم وشەیە پێشتر زیادکراوە💔**", reply_to_message_id=t.id
        )
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

        save_chat_data(cid, data)
        await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)


@app.on_message(filters.regex("^چاتەکان$"))
async def list_chats(client, m):
    cid = str(m.chat.id)
    data = get_chat_data(cid)
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
    save_chat_data(cid, {})
    await m.reply("**بە سەرکەوتوویی هەموو چاتەکان سڕدرانەوە♥️✅**")


@app.on_message(filters.regex("^سڕینەوەی چات$"))
async def delete_chat(client, m):
    cid = str(m.chat.id)
    data = get_chat_data(cid)
    t = await m.chat.ask(
        "** ئێستا ئەو وشەیە بنێرە کە زیادتکردووە🎈•**",
        filters=filters.text & filters.user(m.from_user.id),
        reply_to_message_id=m.id,
    )
    if t.text in data:
        del data[t.text]
        save_chat_data(cid, data)
        await t.reply("**بە سەرکەوتوویی چاتە زیادکراوەکە سڕایەوە♥️**")
    else:
        await t.reply("**هیچ چاتێك بەردەست نییە ئەزیزم👾**")


@app.on_message(filters.text)
async def respond(client, m):
    cid = str(m.chat.id)
    data = get_chat_data(cid)
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


"""
پڕۆگرامساز : @IQ7amo
"""
A = " پڕۆگرامساز : @IQ7amo "

try:
    open("rd.json", "r")
except BaseException:
    with open("rd.json", "w") as f:
        f.write("{}")
api_id = "12962251"  # Here Api Id
api_hash = "b51499523800add51e4530c6f552dbc8"  # Here Api Hash
bot_token = "6357186923:AAGNphNNe2Y--qdeioOoHyruP1Y-HdoTZTc"  # Here Bot Token
app = Client("iiu", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
da = json.load(open("rd.json", "r"))


def save(data):
    with open("rd.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=6, ensure_ascii=False)
        f.close()


def ck(c):
    try:
        da[c]
    except KeyError:
        da[c] = {}
        save(da)


@app.on_message(filters.regex("^زیادکردنی چات$"))
async def t(client, m):
    cid = str(m.chat.id)
    ck(cid)
    t = await m.chat.ask(
        "**ئێستا ئەو وشەیە بنێرە کە دەتەوێت زیادی بکەیت ئەزیزم🖤•**",
        filters=filters.text & filters.user(m.from_user.id),
        reply_to_message_id=m.id,
    )
    if t.text in da[cid]:
        await app.send_message(
            cid, "**ببورە ئەم وشەیە پێشتر زیادکراوە💔**", reply_to_message_id=t.id
        )
    else:
        tt = await m.chat.ask(
            "**ئێستا دەتوانیت یەکێك لەمانە زیادبکەیت بۆ وڵامدانەوە💘\n( وشە، وێنە، گیف، ڤیدیۆ، ڤۆیس، گۆرانی، دەنگ، فایل)**",
            filters=filters.user(t.from_user.id),
            reply_to_message_id=t.id,
        )
        if tt.text:
            da[cid][t.text] = f"text&{tt.text}"
            save(da)
            await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)
        elif tt.photo:
            da[cid][t.text] = f"photo&{tt.photo.file_id}"
            save(da)
            await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)
        elif tt.video:
            da[cid][t.text] = f"video&{tt.video.file_id}"
            save(da)
            await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)
        elif tt.animation:
            da[cid][t.text] = f"animation&{tt.animation.file_id}"
            save(da)
            await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)
        elif tt.voice:
            da[cid][t.text] = f"voice&{tt.voice.file_id}"
            save(da)
            await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)
        elif tt.audio:
            da[cid][t.text] = f"audio&{tt.audio.file_id}"
            save(da)
            await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)
        elif tt.document:
            da[cid][t.text] = f"document&{tt.document.file_id}"
            save(da)
            await tt.reply(f"**چات زیادکرا بە ناوی ↤︎ ({t.text}) ♥•**", quote=True)
        else:
            await tt.reply(
                f"**تەنیا دەتوانی ئەمانە بنێریت\n(وشە، وێنە، گیف، ڤیدیۆ، ڤۆیس، دەنگ، گۆرانی، فایل) ‌♥⚡**",
                quote=True,
            )


@app.on_message(filters.regex("^چاتەکان$"))
async def t(client, m):
    r = ""
    i = 0
    cid = str(m.chat.id)
    ck(cid)
    if da[cid] != {}:
        for a, b in da[cid].items():
            tp = b.split("&", 1)
            if tp[0] == "text":
                t = "**وشە**"
            elif tp[0] == "photo":
                t = "**وێنە**"
            elif tp[0] == "video":
                t = "**ڤیدیۆ**"
            elif tp[0] == "animation":
                t = "**گیف**"
            elif tp[0] == "voice":
                t = "**ڤۆیس**"
            elif tp[0] == "audio":
                t = "**گۆرانی**"
            elif tp[0] == "document":
                t = "**فایل**"
            i += 1
            r += f"{i} => {a} ~ {t}\n"
        await m.reply(r)
    else:
        await m.reply("**هیچ چاتێکی زیادکراو نییە♥️**•")


@app.on_message(filters.regex("^سڕینەوەی چاتەکان$"))
async def t(client, m):
    cid = str(m.chat.id)
    ck(cid)
    if da[cid] != {}:
        da[cid] = {}
        save(da)
        await m.reply("**بە سەرکەوتوویی هەموو چاتەکان سڕدرانەوە♥️✅**")
    else:
        await m.reply("**هیچ چاتی زیادکرا نییە ئەزیزم💔**")


@app.on_message(filters.regex("^سڕینەوەی چات$"))
async def t(client, m):
    cid = str(m.chat.id)
    ck(cid)
    t = await m.chat.ask(
        "** ئێستا ئەو وشەیە بنێرە کە زیادتکردووە🎈•**",
        filters=filters.text & filters.user(m.from_user.id),
        reply_to_message_id=m.id,
    )
    if t.text in da[cid]:
        da[cid].pop(t.text)
        save(da)
        await t.reply("**بە سەرکەوتوویی چاتە زیادکراوەکە سڕایەوە♥️**")
    else:
        await t.reply("**هیچ چاتێك بەردەست نییە ئەزیزم👾**")


@app.on_message(filters.text)
async def t(client, m):
    cid = str(m.chat.id)
    if cid in da:
        for a, b in da[cid].items():
            tp = b.split("&", 1)
            if m.text == a:
                if tp[0] == "text":
                    await m.reply(tp[1])
                elif tp[0] == "photo":
                    await m.reply_photo(tp[1])
                elif tp[0] == "video":
                    await m.reply_video(tp[1])
                elif tp[0] == "animation":
                    await m.reply_animation(tp[1])
                elif tp[0] == "voice":
                    await m.reply_voice(tp[1])
                elif tp[0] == "audio":
                    await m.reply_audio(tp[1])
                elif tp[0] == "document":
                    await m.reply_document(tp[1])


print("#" * 25)
print(A.center(25, "#"))
print("#" * 25)
print("دەستی بە کارکردن کرد ...")
app.start()
idle()
"""
پڕۆگرامساز : @IQ7amo
"""
