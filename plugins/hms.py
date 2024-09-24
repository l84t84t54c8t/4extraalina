from pyrogram import filters
from pyrogram.types import *
from AlinaMusic import app

hmses = {}


@app.on_message(
    filters.reply & filters.regex(r"^(چرپەنامە|چرپە|/whisper)$") & filters.group
)
async def reply_with_link(client, message):
    user_id = message.reply_to_message.from_user.id
    my_id = message.from_user.id
    bar_id = message.chat.id
    start_link = f"https://t.me/{app.username}?start=hms{my_id}to{user_id}in{bar_id}"
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("- ئێرە دابگرە 📬", url=start_link)]]
    )
    await message.reply_text(
        "**\n⇜ دووگمەی خوارەوە داگرە بۆ نووسینی چرپە.\n✓**", reply_markup=reply_markup
    )


waiting_for_hms = False


@app.on_message(filters.command("start"), group=5790)
async def hms_start(client, message):
    if message.text.split(" ", 1)[-1].startswith("hms"):
        global waiting_for_hms, hms_ids
        hms_ids = message.text
        waiting_for_hms = True
        await message.reply_text(
            "**-> ئێستا چرپەنامە بنێرە\n√**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- هەڵوەشاندنەوە ❌️", callback_data="hms_cancel"
                        )
                    ]
                ]
            ),
        )
        return


@app.on_message(filters.private & filters.text & ~filters.command("hstart"), group=576)
async def send_hms(client, message):
    global waiting_for_hms
    if waiting_for_hms:
        to_id = int(hms_ids.split("to")[-1].split("in")[0])
        from_id = int(hms_ids.split("hms")[-1].split("to")[0])
        in_id = int(hms_ids.split("in")[-1])
        to_url = f"tg://openmessage?user_id={to_id}"
        from_url = f"tg://openmessage?user_id={from_id}"
        user = await client.get_users(to_id)
        user2 = await client.get_users(from_id)
        user_id = user.id
        user_mention = user.mention()
        user_mention2 = user2.mention()
        hmses[str(to_id)] = {"hms": message.text, "bar": in_id}
        await message.reply_text("**⇜ بە سەرکەوتوویی چرپەنامە .. نێردرا \n√**")
        await client.send_message(
            chat_id=in_id,
            text=f"**⇜ ئەزیزم 「 {user_mention} 」.\n⇜ چرپەیەکی نھێنیت هەیە لە 「 {user_mention2} 」.**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- کردنەوەی چرپەنامە 🗳", callback_data="hms_answer"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "- نێردراوە بۆ 🖱", url=f"tg://openmessage?user_id={to_id}"
                        )
                    ],
                    [InlineKeyboardButton("- لەلایەن 🖱", url=f"{from_url}")],
                ]
            ),
        )
        waiting_for_hms = False


@app.on_callback_query(filters.regex("hms_answer"), group=5766565)
async def display_hms(client, callback):
    in_id = callback.message.chat.id
    who_id = callback.from_user.id
    if hmses.get(str(who_id)) is not None:
        if hmses.get(str(who_id))["bar"] == in_id:
            await callback.answer(hmses.get(str(who_id))["hms"], show_alert=True)
    else:
        await callback.answer("⇜ لاچۆ ئەم چرپەیە بۆتۆ نییە", show_alert=True)


@app.on_callback_query(filters.regex("hms_cancel"), group=57967)
async def cancel_hms(client, callback):
    global waiting_for_hms
    waiting_for_hms = False
    await client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text="**-> چرپەنامە هەڵوەشێنرایەوە\n√**",
    )


__MODULE__ = "Wʜɪsᴘᴇʀ Rᴇᴘʟᴀʏ"
__HELP__ = """
**Wʜɪsᴘᴇʀ Bʏ Rᴇᴘʟᴀʏ** 

- Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴜsᴇᴅ ᴛᴏ sᴇɴᴅ ᴀ sᴇᴄʀᴇᴛ ᴍᴇssᴀɢᴇ ɪɴ ɢʀᴏᴜᴘs ᴛʜᴀᴛ ᴏɴʟʏ ᴀ ᴅᴇsɪɢɴᴀᴛᴇᴅ ᴘᴇʀsᴏɴ ᴄᴀɴ ᴏᴘᴇɴ

**ᴜsᴀɢᴇ :**
- Rᴇᴘʟᴀʏ ᴘᴇʀsᴏɴ ᴡʀɪᴛᴇ ᴡʜɪsᴘᴇʀ 
- Tʜᴇɴ ʏᴏᴜ ɢᴏ ᴘʀɪᴠᴀᴛᴇ ᴀɴᴅ ᴡʀɪᴛᴇ sᴇᴄʀᴇᴛ ᴍᴇssᴀɢᴇs

**ᴇxᴀᴍᴘʟᴇ : **
- /whisper Rᴇᴘʟᴀʏ ᴘᴇʀsᴏɴ
"""
