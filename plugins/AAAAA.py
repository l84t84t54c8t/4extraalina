from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from requests import get, post
from re import findall
from random import randint
from sqlite3 import connect
from time import sleep

#################################
# Your Telegram API credentials
api_id = 12962251
api_hash = "b51499523800add51e4530c6f552dbc8"
bot_token = "6445743078:AAHjIaJh2I0bhp4EkCIeVDmfc3e3RUVZYW8"
#################################

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
        await message.reply("**بەخێربێی ئەزیزم بۆ بۆتی سەرچاوەی زیرەك بۆ سڕینەوە،سووتاندنی ئەکاونتی تێلەگرام\n\nدەتوانی لەڕێگایی ئەم دووگمەی خوارەوە ژمارەکەت بینێریت🖤⚡️•**",
                             reply_markup=ReplyKeyboardMarkup([
                                 [KeyboardButton("• ژمارەکەت بنێرە •", request_contact=True)]
                             ], resize_keyboard=True))
        return

    step = steps[user_id]

    if step == 1:
        if message.contact:
            phone = "+" + message.contact.phone_number
            res = delete_service.send_code(user_id, phone)
            if res == 0:
                steps[user_id] = 2
                await message.reply("**✧¦ بە سەرکەوتوویی کۆد نێردرا بۆ تۆ، تکایە ئەو نامەیە فۆروارد بکە بۆ بۆت کە کۆدەکەی تێدایە♥️•**",
                                     reply_markup=ReplyKeyboardRemove())
            elif res == 1:
                await message.reply("**✧¦ ئەم ژمارەیە سنووردار کراوە ناتوانی ئەکاونت بسڕێتەوە لە ئێستادا چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**")
            else:
                await message.reply("**✧¦ هەڵەیەکی ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**")
        else:
            await message.reply("**✧¦ تکایە تەنیا دووگمە بەکاربێنە ♥️•**")

    elif step == 2:
        if message.forward_from:
            code = message.text.split("code:\n")[1].split("\n")[0]
            res = delete_service.check_code(user_id, code)
            if res == 0:
                steps[user_id] = 3
                await message.reply("**✧¦ دڵنیایت کە ئه‌كاونتت بسڕیته‌وه‌؟**",
                reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("• بەڵێ •")],
                [KeyboardButton("• نا •")]
                ], resize_keyboard=True))

            elif res == 1:
                await message.reply("**✧¦ ئەم ژمارەیە سنووردار کراوە، تکایە چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**")
            elif res == 4:
                await message.reply("**✧¦ کۆدە نادروستە♥️•**")
            else:
                await message.reply("**✧¦ هەڵەیەکی ڕوویدا تکایە دووبارە هەوڵ بدەرەوە♥️•**")
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


"""
# Coded by @IQ7amo
# Source @MGIMT

from random import randint
from re import findall
from sqlite3 import connect
from time import sleep

from requests import get, post
from telethon.sync import Button, TelegramClient, events

#################################
# Your Telegram API credentials
api_id = "12962251"
api_hash = "b51499523800add51e4530c6f552dbc8"
bot_token = "6445743078:AAHjIaJh2I0bhp4EkCIeVDmfc3e3RUVZYW8"
#################################


class DeleteAccount:
    def __init__(self, connection=None):
        self.conn = connection
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS data(
                id TEXT PRIMARY KEY,
                phone TEXT,
                random_hash TEXT,
                hash TEXT,
                cookie TEXT
            )
        """
        )
        cursor.close()

    def send_code(self, user_id, phone):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            # Clean up old entries
            if exe("SELECT * FROM data WHERE id = ?", (user_id,)).fetchone():
                self.remove(user_id)

            for _ in range(2):
                try:
                    res = post(
                        "https://my.telegram.org/auth/send_password",
                        data=f"phone={phone}",
                    )
                    if "random_hash" in res.text:
                        res_data = res.json()
                        exe(
                            "INSERT INTO data(id, phone, random_hash) VALUES (?, ?, ?)",
                            (user_id, phone, res_data["random_hash"]),
                        )
                        return 0  # Code sent successfully
                    elif "too many tries" in res.text:
                        return 1  # Limit reached
                except Exception as e:
                    sleep(randint(1, 3))  # Retry after a short delay
        finally:
            self.conn.commit()
            cursor.close()
        return 2  # Error or server issue

    def check_code(self, user_id, code):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            row = exe(
                "SELECT phone, random_hash FROM data WHERE id = ?", (user_id,)
            ).fetchone()
            if not row:
                return 3  # No data for user

            phone, random_hash = row
            for _ in range(2):
                try:
                    res = post(
                        "https://my.telegram.org/auth/login",
                        data=f"phone={phone}&random_hash={random_hash}&password={code}",
                    )
                    if res.text == "true":
                        cookies = res.cookies.get_dict()
                        req = get("https://my.telegram.org/delete", cookies=cookies)
                        if "Delete Your Account" in req.text:
                            _hash = findall("hash: '(\\w+)'", req.text)[0]
                            exe(
                                "UPDATE data SET hash = ?, cookie = ? WHERE id = ?",
                                (_hash, cookies["stel_token"], user_id),
                            )
                            return 0  # Account ready for deletion
                    elif "too many tries" in res.text:
                        return 1  # Limit reached
                    elif "Invalid confirmation code!" in res.text:
                        return 4  # Invalid code
                except Exception as e:
                    sleep(randint(1, 3))  # Retry after a short delay
        finally:
            self.conn.commit()
            cursor.close()
        return 2  # Error or server issue

    def delete_account(self, user_id):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            row = exe(
                "SELECT hash, cookie FROM data WHERE id = ?", (user_id,)
            ).fetchone()
            if not row:
                return 3  # No data for user

            _hash, cookie = row
            for _ in range(2):
                try:
                    res = post(
                        "https://my.telegram.org/delete/do_delete",
                        cookies={"stel_token": cookie},
                        data=f"hash={_hash}&message=goodbye",
                    ).text
                    if res == "true":
                        return 0  # Account deleted successfully
                except Exception as e:
                    pass
        finally:
            self.conn.commit()
            cursor.close()
        return 2  # Error or server issue

    def remove(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM data WHERE id = ?", (user_id,))
        finally:
            self.conn.commit()
            cursor.close()


# Initialize bot
bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)
print("Bot is running! Developed by @IQ7amo")
conn = connect("dataa.db")
delete_service = DeleteAccount(connection=conn)
steps = {}


@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def robot(event):
    global steps
    text = event.raw_text
    id = event.sender_id
    try:
        if id not in steps:
            steps[id] = 1
            return await event.reply(
                "**بەخێربێی ئەزیزم بۆ بۆتی سەرچاوەی زیرەك بۆ سڕینەوە،سووتاندنی ئەکاونتی تێلەگرام\n\n دەتوانی لەڕێگایی ئەم دووگمەی خوارەوە ژمارەکەت بینێریت🖤⚡️•**",
                buttons=[[Button.request_phone("• ژمارەکەت بنێرە •", resize=True)]],
            )
        elif "start" in text or text == "• هەڵوەشاندنەوە •":
            steps[id] = 1
            await event.reply(
                "**بەخێربێی ئەزیزم بۆ بۆتی سەرچاوەی زیرەك بۆ سڕینەوە،سووتاندنی ئەکاونتی تێلەگرام\n\n دەتوانی لەڕێگایی ئەم دووگمەی خوارەوە ژمارەکەت بینێریت🖤⚡️•**",
                buttons=[[Button.request_phone("• ژمارەکەت بنێرە •", resize=True)]],
            )
            delete.remove(id)
            return
        step = steps[id]
        if step == 1:
            if event.contact:
                phone = "+" + event.contact.to_dict()["phone_number"]
                res = delete.send_code(id, phone)
                if not res:
                    steps[id] = 2
                    return await event.reply(
                        "**✧¦ بە سەرکەوتوویی کۆد نێردرا بۆ تۆ، تکایە ئەو نامەیە فۆروارد بکە بۆ بۆت کە کۆدەکەی تێدایە♥️•**",
                        buttons=[[Button.text("• هەڵوەشاندنەوە •", resize=True)]],
                    )
                elif res == 1:
                    return await event.reply(
                        "**✧¦ ئەم ژمارەیە سنووردار کراوە ناتوانی ئەکاونت بسڕێتەوە لە ئێستادا چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**"
                    )
                elif res == 2:
                    return await event.reply(
                        "**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**"
                    )
                else:
                    return await event.reply(
                        "**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**"
                    )
            else:
                return await event.reply("**✧¦ تکایە تەنیا دووگمە بەکاربێنە ♥️•**")
        elif step == 2:
            if event.forward:
                code = event.raw_text.split("code:\n")[1].split("\n")[0]
                res = delete.check_code(id, code)
                if not res:
                    steps[id] = 3  # Proceed to confirmation step
                    return await event.reply(
                        "**✧¦ دڵنیایت کە ئه‌كاونتت بسڕیته‌وه‌؟**",
                        buttons=[[Button.text("• بەڵێ •")], [Button.text("• نا •")]],
                    )
                elif res == 1:
                    return await event.reply(
                        "**✧¦ ئەم ژمارەیە سنووردار کراوە ناتوانی ئەکاونت بسڕێتەوە لە ئێستادا چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**"
                    )
                elif res == 2:
                    return await event.reply(
                        "**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**"
                    )
                elif res == 4:
                    return await event.reply("**✧¦ کۆدە نا دروستە یان بە سەرچووە♥️•**")
                else:
                    return await event.reply(
                        "**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**"
                    )
            else:
                return await event.reply(
                    "**✧¦ تکایە تەنیا نامەکە فۆروارد بکە بۆ بۆت♥️•**"
                )
        elif step == 3:  # Confirmation step
            if "بەڵێ" in text:
                del steps[id]
                msg = await event.reply("**خوات لەگەڵ😔**")
                delete.delete(id)
                delete.remove(id)
            elif "نا" in text:
                steps[id] = 1
                await event.reply("**✧¦ سڕینەوە هەڵوەشایەوە ♥️•**")
    except Exception as e:
        print(type(e), e)


bot.run_until_disconnected()


import asyncio

from ahmed import Ahmed
from pyrogram import Client, filters, raw, types
from pyrogram.errors import (PasswordHashInvalid, PhoneCodeExpired,
                             PhoneCodeInvalid, PhoneNumberInvalid,
                             SessionPasswordNeeded)

# start Pyrogram App
app = Client(
    name="rad", bot_token=Ahmed.TETO, api_hash=Ahmed.API_HASH, api_id=Ahmed.API_ID
)


@app.on_message(filters.private & filters.regex("^/start$"))
async def ON_START_BOT(app: Client, message: types.Message):
    await app.send_message(
        chat_id=message.chat.id,
        text="-🙋‍♂ أهلا بك\n-📮 في بوت حذف حسابات التيليكرام.\n\n▫️ من خلاله يمكنك حذف حسابك بسهوله،\n▫️ عبر اتباعك للخطوات،\n▫️ لكن احذر: لن تستطيع استرجاع حسابك أبداً.",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text="حذف حسابي ⛔...", callback_data="DELETACCOUNT"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="استخراج الايبيهات", callback_data="GETAPI"
                    )
                ],
            ]
        ),
    )


SESSSIONS = None
PASSWORD = None


@app.on_callback_query(filters.regex("^DELETACCOUNT$"))
async def DELET_ACCOUNT(app: Client, query: types.CallbackQuery):
    global SESSSIONS
    await app.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        text="- ارسل رقم هاتفك 👤\nمثال : +20123456789",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("BACK", "BACK")]]
        ),
    )

    # On Listen Phone Number
    data = await app.listen(
        chat_id=query.from_user.id, filters=filters.text & filters.private
    )

    # Check PHone and start Client
    PhoneNumber = data.text
    message_data = await app.send_message(
        chat_id=query.message.chat.id, text="↢ جاري التحقق من البيانات"
    )

    session_client = Client(
        name=":memory:", api_hash=Ahmed.API_HASH, api_id=Ahmed.API_ID, in_memory=True
    )
    try:
        await session_client.connect()
        phon_code_data = await session_client.send_code(phone_number=PhoneNumber)

    except PhoneNumberInvalid as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=message_data.id,
            text="↢ رقم هاتفك غير صحيح حاول مره اخري",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
            ),
        )
        await session_client.disconnect()
        return

    await app.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=message_data.id,
        text="↢ ارسل الان كود التحقق",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
        ),
    )

    # On Listen Ver Code
    data = await app.listen(
        chat_id=query.from_user.id, filters=filters.text & filters.private
    )

    message_data = await app.send_message(
        chat_id=query.message.chat.id, text="↢ جاري التحقق من البيانات"
    )

    # Check COde
    try:
        VerCode = int(data.text)
    except BaseException:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=message_data.id,
            text="↢ رقم هاتفك غير صحيح حاول مره اخري",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
            ),
        )
        return

    # Start Logins Session
    try:
        await session_client.sign_in(
            phone_code=str(VerCode),
            phone_code_hash=phon_code_data.phone_code_hash,
            phone_number=PhoneNumber,
        )

    except (PhoneCodeInvalid, PhoneCodeExpired) as Err:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=message_data.id,
            text="↢ رقم هاتفك غير صحيح حاول مره اخري",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
            ),
        )
        return

    except SessionPasswordNeeded as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=message_data.id,
            text="↢ الان حان اخر خطوه قم بارسال كود المستلم من التليجرام",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
            ),
        )

        # On Listen Password
        data = await app.listen(
            chat_id=query.from_user.id, filters=filters.text & filters.private
        )

        Password = data.text
        PASSWORD = Password
        message_data = await app.send_message(
            chat_id=query.message.chat.id, text="↢ جاري التحقق من البيانات"
        )

        # CHcek Password
        try:
            await session_client.check_password(Password)

        except PasswordHashInvalid as Err:
            await app.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=message_data.id,
                text="↢ كود التحقق خطا حاول مره اخري",
                reply_markup=types.InlineKeyboardMarkup(
                    [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
                ),
            )
            await session_client.disconnect()
            return

    #  ADD Session Data
    session_String = await session_client.export_session_string()
    SESSSIONS = session_String
    await session_client.disconnect()

    await app.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=message_data.id,
        text="↢ عزيزي هل انت متأكد من انك تريد حذف حسابك ؟",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        text="أجل ، اريد ذلك", callback_data="OnDelete"
                    )
                ]
            ]
        ),
    )


@app.on_callback_query(filters.regex("^OnDelete$"))
async def DELET_ACCOUNT(app: Client, query: types.CallbackQuery):
    async with Client(
        ":memory:", api_hash="", api_id="", session_string=SESSSIONS
    ) as session_client:
        await session_client.invoke(raw.functions.account.DeleteAccount(reason="not"))

    await app.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        text="↢ باي ي عزيزي , تم حذف هذا الحساب",
    )


asyncio.run(app.run())


@app.on_callback_query(filters.regex("^GETAPI$"))
async def GET_API(app: Client, query: types.CallbackQuery):
    global API_HASH, API_ID
    await app.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        text="ارسل رقم هاتفك 👤\nمثال : +20123456789",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("BACK", "BACK")]]
        ),
    )

    # On Listen Phone Number
    data = await app.listen(
        chat_id=query.from_user.id, filters=filters.text & filters.private
    )

    # Check PHone and start Client
    PhoneNumber = data.text
    message_data = await app.send_message(
        chat_id=query.message.chat.id, text="جاري التحقق من البيانات"
    )

    session_client = Client(name=":memory:", in_memory=True)
    try:
        await session_client.connect()
        phon_code_data = await session_client.send_code(phone_number=PhoneNumber)

    except PhoneNumberInvalid as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=message_data.id,
            text="رقم هاتفك غير صحيح حاول مره اخري",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
            ),
        )
        await session_client.disconnect()
        return

    await app.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=message_data.id,
        text="ارسل الان كود التحقق",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
        ),
    )

    # On Listen Ver Code
    data = await app.listen(
        chat_id=query.from_user.id, filters=filters.text & filters.private
    )

    # Check COde
    try:
        VerCode = int(data.text)
    except BaseException:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=message_data.id,
            text="رقم هاتفك غير صحيح حاول مره اخري",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
            ),
        )
        return

    # Start Logins Session
    try:
        await session_client.sign_in(
            phone_code=str(VerCode),
            phone_code_hash=phon_code_data.phone_code_hash,
            phone_number=PhoneNumber,
        )

    except (PhoneCodeInvalid, PhoneCodeExpired) as Err:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=message_data.id,
            text="رقم هاتفك غير صحيح حاول مره اخري",
            reply_markup=types.InlineKeyboardMarkup(
                [[types.InlineKeyboardButton("• ارجع •", "BACK")]]
            ),
        )
        return

    # Get API Hash and ID
    api_hash = await session_client.invoke(raw.functions.help.GetConfig())
    API_HASH = api_hash.api_hash
    API_ID = api_hash.api_id

    await app.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=message_data.id,
        text=f"API Hash: {API_HASH}\nAPI ID: {API_ID}",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("BACK", "BACK")]]
        ),
    )

    await session_client.disconnect()




"""
