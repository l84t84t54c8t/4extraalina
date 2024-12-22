from telethon.sync import TelegramClient, events, Button
from requests import get, post
from re import findall
from random import randint
from sqlite3 import connect
from time import sleep
from os import chdir

# Your configuration values here
api_id = '12962251'  # your api id
api_hash = 'b51499523800add51e4530c6f552dbc8'  # your api hash
bot_token = '6445743078:AAElVgMEQXKageGsH7pmMMkFxyhvhUvDdsU'  # your bot token

class delete:
    def __init__(self, connection=None):
        self.conn = connection
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS data(id, phone, random_hash, hash, cookie)")
        self.conn.commit()  # Commit the changes after table creation
        cursor.close()

    def send_code(self, id, phone):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            if len(exe(f"SELECT * FROM data WHERE id = '{id}'").fetchall()):
                self.remove(id)
            for _ in range(2):
                try:
                    res = post("https://my.telegram.org/auth/send_password", data=f"phone={phone}")
                    if 'random_hash' in res.text:
                        res = res.json()
                        exe(f"INSERT INTO data(id, phone, random_hash) VALUES ('{id}', '{phone}', '{res['random_hash']}')")
                        return 0  # ok
                    elif "too many tries" in res.text:
                        return 1  # limit
                    else:
                        return 2  # unknown
                except Exception as e:
                    if _ < 4:
                        sleep(randint(1, 3))
        finally:
            self.conn.commit()

        return 3  # server error

    def check_code(self, id, code):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            phone, random_hash = next(exe(f"SELECT phone, random_hash FROM data WHERE id = '{id}'"))
            for _ in range(2):
                try:
                    res = post("https://my.telegram.org/auth/login", data=f"phone={phone}&random_hash={random_hash}&password={code}")
                    if res.text == "true":
                        cookies = res.cookies.get_dict()
                        req = get("https://my.telegram.org/delete", cookies=cookies)
                        if "Delete Your Account" in req.text:
                            _hash = findall("hash: '(\w+)'", req.text)[0]
                            exe(f"UPDATE data SET hash = '{_hash}', cookie = '{cookies['stel_token']}' WHERE id = '{id}'")
                            return 0  # ok
                        else:
                            return 2  # unknown
                    elif "too many tries" in res.text:
                        return 1  # limit
                    elif "Invalid confirmation code!" in res.text:
                        return 4  # invalid code
                    else:
                        print(res.text)
                except Exception as e:
                    if _ < 4:
                        sleep(randint(1, 3))
        except Exception as e:
            print(type(e), e)
        finally:
            self.conn.commit()
        return 3  # server error

    def delete(self, id):
        try:
            cursor = self.conn.cursor()
            exe = cursor.execute
            _hash, cookies = next(exe(f"SELECT hash, cookie FROM data WHERE id = '{id}'"))
            for _ in range(2):
                try:
                    res = post("https://my.telegram.org/delete/do_delete", cookies={'stel_token': cookies}, data=f"hash={_hash}&message=goodby").text
                    if res == "true":
                        return 0  # ok
                    else:
                        return 5  # failed
                except Exception as e:
                    pass
        finally:
            self.conn.commit()

        return 3  # server error

    def remove(self, id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"DELETE FROM data WHERE id = '{id}'")
        finally:
            self.conn.commit()

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
print("بۆت چالاکە !\nکۆد لەلایەن : @IQ7amo")
conn = connect("dataa.db")
delete = delete(connection=conn)
steps = {}

channel_username = 'Haawall'

async def check_channel_membership(event):
    try:
        user_id = event.sender_id
        # Get the participants of the channel
        participants = await bot.get_participants(channel_username)
        # Check if the user is a member of the channel
        for participant in participants:
            if participant.id == user_id:
                return True  # User is a member
        return False  # User is not a member
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False  # In case of an error, assume user is not a member


@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def robot(event):
    global steps
    text = event.raw_text
    id = event.sender_id
    try:
        if not await check_channel_membership(event):  # Pass event here
            # If the user is not a member, prompt them to join the channel
            buttons = [
                [Button.url("• جۆینی کەناڵ بکە •", url=f"https://t.me/{channel_username}")]
            ]
            return await event.reply(
                f"**• Sorry . .\n• You must first join Channel to use me\n• Channel : « @{channel_username} »\n\n• ببووره . . ئەزیزم\n• سەرەتا پێویستە جۆینی کەناڵ بکەیت بۆ بەکارهێنانم\n• کەناڵ : «  @{channel_username} »**", 
                buttons=buttons
            )
        
        if id not in steps:
            steps[id] = 1
            return await event.reply("**بەخێربێی ئەزیزم بۆ بۆتی سەرچاوەی زیرەك بۆ سڕینەوە،سووتاندنی ئەکاونتی تێلەگرام\n\n دەتوانی لەڕێگایی ئەم دووگمەی خوارەوە ژمارەکەت بینێریت🖤⚡️•**", buttons=[[Button.request_phone("• ژمارەکەت بنێرە •", resize=True)]])

        elif "start" in text or text == "• هەڵوەشاندنەوە •":
            steps[id] = 1
            await event.reply("**بەخێربێی ئەزیزم بۆ بۆتی سەرچاوەی زیرەك بۆ سڕینەوە،سووتاندنی ئەکاونتی تێلەگرام\n\n دەتوانی لەڕێگایی ئەم دووگمەی خوارەوە ژمارەکەت بینێریت🖤⚡️•**", buttons=[[Button.request_phone("• ژمارەکەت بنێرە •", resize=True)]])
            delete.remove(id)
            return

        step = steps[id]
        if step == 1:
            if event.contact:
                phone = "+" + event.contact.to_dict()['phone_number']
                res = delete.send_code(id, phone)
                if not res:
                    steps[id] = 2
                    return await event.reply("**✧¦ بە سەرکەوتوویی کۆد نێردرا بۆ تۆ، تکایە ئەو نامەیە فۆروارد بکە بۆ بۆت کە کۆدەکەی تێدایە♥️•**", buttons=[[Button.text("• هەڵوەشاندنەوە •", resize=True)]])
                elif res == 1:
                    return await event.reply("**✧¦ ئەم ژمارەیە سنووردار کراوە ناتوانی ئەکاونت بسڕێتەوە لە ئێستادا چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**")
                elif res == 2:
                    return await event.reply("**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**")
                else:
                    return await event.reply("**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**")
            else:
                return await event.reply("**✧¦ تکایە تەنیا دووگمە بەکاربێنە ♥️•**")
        if step == 2:
            if event.forward:
                code = event.raw_text.split("code:\n")[1].split("\n")[0]
                res = delete.check_code(id, code)
                if not res:
                    # Adding a confirmation step before deletion
                    confirm_msg = await event.reply(
                        "**ئایا دڵنیای دەتەوێت ئەکاونتت بسڕیتەوە؟**",
                        buttons=[
                            [Button.text("• بەڵێ دەمەوێت بیسڕمەوە •", resize=True)],
                            [Button.text("• نەخێر نامەوێت •", resize=True)],
                        ]
                    )

                    # Save confirmation step for future actions
                    steps[id] = 3
                    return
                elif res == 1:
                    return await event.reply("**✧¦ ئەم ژمارەیە سنووردار کراوە ناتوانی ئەکاونت بسڕێتەوە لە ئێستادا چەند کاتژمێرێکی تر هەوڵبدەوە♥️•**")
                elif res == 2:
                    return await event.reply("**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**")
                elif res == 3:
                    return await event.reply("**✧¦ کۆدە نا دروستە یان بە سەرچووە♥️•**")
                else:
                    return await event.reply("**✧¦ هەڵەیەکی دیارینەکراو ڕوویدا تکایە لە چەند خولەکێکی تر دووبارە هەوڵ بدەرەوە♥️•**")
            else:
                return await event.reply("**✧¦ تکایە تەنیا نامەکە فۆروارد بکە بۆ بۆت♥️•**")
        if step == 3:
            if "• بەڵێ دەمەوێت بیسڕمەوە •" in text:
                # Deleting the account upon confirmation
                await event.reply("**بەسەرکەوتوویی ئەکاونتت سڕدرایەوە.**")
                delete.delete(id)
                delete.remove(id)
                del steps[id]
            elif "• نەخێر نامەوێت •" in text:
                await event.reply("**هەڵوەشێنرایەوە ئەکاونتت نە سڕدرایەوە.**")
                del steps[id]

    except Exception as e:
        print(type(e), e)

bot.run_until_disconnected()
