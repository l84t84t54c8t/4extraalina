from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from requests import get, post
from re import findall
from random import randint
from sqlite3 import connect
from time import sleep

# Telegram API credentials
api_id = 12962251
api_hash = "b51499523800add51e4530c6f552dbc8"
bot_token = "6445743078:AAHjIaJh2I0bhp4EkCIeVDmfc3e3RUVZYW8"

class DeleteAccount:
    def __init__(self, connection=None):
        self.conn = connection
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data(
                id TEXT PRIMARY KEY,
                phone TEXT,
                random_hash TEXT,
                hash TEXT,
                cookie TEXT
            )
        """)
        cursor.close()

    def send_code(self, user_id, phone):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            if exe("SELECT * FROM data WHERE id = ?", (user_id,)).fetchone():
                self.remove(user_id)

            for _ in range(2):
                try:
                    res = post("https://my.telegram.org/auth/send_password", data=f"phone={phone}")
                    if 'random_hash' in res.text:
                        res_data = res.json()
                        exe("INSERT INTO data(id, phone, random_hash) VALUES (?, ?, ?)", 
                            (user_id, phone, res_data['random_hash']))
                        return 0
                    elif "too many tries" in res.text:
                        return 1
                except Exception:
                    sleep(randint(1, 3))
        finally:
            self.conn.commit()
            cursor.close()
        return 2

    def check_code(self, user_id, code):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            row = exe("SELECT phone, random_hash FROM data WHERE id = ?", (user_id,)).fetchone()
            if not row:
                return 3

            phone, random_hash = row
            for _ in range(2):
                try:
                    res = post("https://my.telegram.org/auth/login", 
                               data=f"phone={phone}&random_hash={random_hash}&password={code}")
                    if res.text == "true":
                        cookies = res.cookies.get_dict()
                        req = get("https://my.telegram.org/delete", cookies=cookies)
                        if "Delete Your Account" in req.text:
                            _hash = findall("hash: '(\\w+)'", req.text)[0]
                            exe("UPDATE data SET hash = ?, cookie = ? WHERE id = ?", 
                                (_hash, cookies['stel_token'], user_id))
                            return 0
                    elif "too many tries" in res.text:
                        return 1
                    elif "Invalid confirmation code!" in res.text:
                        return 4
                except Exception:
                    sleep(randint(1, 3))
        finally:
            self.conn.commit()
            cursor.close()
        return 2

    def delete_account(self, user_id):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            row = exe("SELECT hash, cookie FROM data WHERE id = ?", (user_id,)).fetchone()
            if not row:
                return 3

            _hash, cookie = row
            for _ in range(2):
                try:
                    res = post("https://my.telegram.org/delete/do_delete", 
                               cookies={'stel_token': cookie}, 
                               data=f"hash={_hash}&message=goodbye").text
                    if res == "true":
                        return 0
                except Exception:
                    pass
        finally:
            self.conn.commit()
            cursor.close()
        return 2

    def remove(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM data WHERE id = ?", (user_id,))
        finally:
            self.conn.commit()
            cursor.close()

app = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
print("Bot is running! Developed by @IQ7amo")
conn = connect("dataa.db")
delete_service = DeleteAccount(connection=conn)
steps = {}

@app.on_message(filters.private)
async def robot(client, message: Message):
    global steps
    user_id = message.from_user.id
    text = message.text

    if user_id not in steps:
        steps[user_id] = 1
        await message.reply(
            "**بەخێربێی ئەزیزم بۆ بۆتی سەرچاوەی زیرەك بۆ سڕینەوە،سووتاندنی ئەکاونتی تێلەگرام\n\nدەتوانی لەڕێگایی ئەم دووگمەی خوارەوە ژمارەکەت بینێریت🖤⚡️•**",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("• ژمارەکەت بنێرە •", request_contact=True)]
            ], resize_keyboard=True)
        )
        return

    step = steps[user_id]

    if step == 1:
        if message.contact:
            phone = "+" + message.contact.phone_number
            res = delete_service.send_code(user_id, phone)
            if res == 0:
                steps[user_id] = 2
                await message.reply(
                    "**✧¦ بە سەرکەوتوویی کۆد نێردرا بۆ تۆ، تکایە ئەو نامەیە فۆروارد بکە بۆ بۆت کە کۆدەکەی تێدایە♥️•**",
                    reply_markup=ReplyKeyboardRemove()
                )
            elif res == 1:
                await message.reply("**✧¦ ئەم ژمارەیە سنووردار کراوە، تکایە چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**")
            else:
                await message.reply("**✧¦ هەڵەیەکی ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**")
        else:
            await message.reply("**✧¦ تکایە تەنیا دووگمە بەکاربێنە ♥️•**")

    elif step == 2:
        if message.forward_from:
            try:
                code = findall(r"code:\n(\d+)", message.text)[0]
                res = delete_service.check_code(user_id, code)
                if res == 0:
                    steps[user_id] = 3
                    await message.reply(
                        "**✧¦ دڵنیایت کە ئه‌كاونتت بسڕیته‌وه‌؟**",
                        reply_markup=ReplyKeyboardMarkup([
                            [KeyboardButton("• بەڵێ •"), KeyboardButton("• نا •")]
                        ], resize_keyboard=True)
                    )
                elif res == 1:
                    await message.reply("**✧¦ ئەم ژمارەیە سنووردار کراوە، تکایە چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**")
                elif res == 4:
                    await message.reply("**✧¦ کۆدە نادروستە♥️•**")
                else:
                    await message.reply("**✧¦ هەڵەیەکی ڕوویدا تکایە دووبارە هەوڵ بدەرەوە♥️•**")
            except IndexError:
                await message.reply("**✧¦ ناتوانرێت کۆدەکە بدۆزرێتەوە، تکایە دڵنیابە لە فۆرواردی نامەکە.**")
        else:
            await message.reply("**✧¦ تکایە تەنیا نامەکە فۆروارد بکە بۆ بۆت♥️•**")

    elif step == 3:
        if "بەڵێ" in text:
            delete_service.delete_account(user_id)
            delete_service.remove(user_id)
            del steps[user_id]
            await message.reply("**خوات لەگەڵ😔**", reply_markup=ReplyKeyboardRemove())
        elif "نا" in text:
            steps[user_id] = 1
            await message.reply("**✧¦ سڕینەوە هەڵوەشایەوە ♥️•**", reply_markup=ReplyKeyboardRemove())

app.run()
