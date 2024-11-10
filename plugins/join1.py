from AlinaMusic import app
from config import MUST_JOIN, MUST_JOIN2  # Assuming two separate channel vars
from pyrogram import Client, filters
from pyrogram.errors import (ChatAdminRequired, ChatWriteForbidden,
                             UserNotParticipant)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# --------------------------

# ------------------------


@app.on_message(filters.incoming & filters.private, group=-2)
async def must_join_channel(app: Client, msg: Message):
    if not (MUST_JOIN and MUST_JOIN2):
        return

    # Check if user is a member of the first channel
    try:
        await app.get_chat_member(MUST_JOIN, msg.from_user.id)
    except UserNotParticipant:
        if MUST_JOIN.isalpha():
            link = f"https://t.me/{MUST_JOIN}"
        else:
            chat_info = await app.get_chat(MUST_JOIN)
            name = chat_info.first_name
            link = chat_info.invite_link

        try:
            await msg.reply(
                f"**• Sorry . . {msg.from_user.mention}\n• You must first join channel to use me\n• Channel: « @{MUST_JOIN} »\n\n• ببووره . . ئەزیزم {msg.from_user.mention}\n• سەرەتا پێویستە جۆینی کەناڵ بکەیت بۆ بەکارهێنانم\n• کەناڵ: « @{MUST_JOIN} »**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(name, url=link),
                        ]
                    ]
                ),
                disable_web_page_preview=True,
            )
            await msg.stop_propagation()
        except ChatWriteForbidden:
            pass
        return  # Stop here if the user is not in the first channel

    # Check if user is a member of the second channel
    try:
        await app.get_chat_member(MUST_JOIN2, msg.from_user.id)
    except UserNotParticipant:
        if MUST_JOIN2.isalpha():
            link = f"https://t.me/{MUST_JOIN2}"
        else:
            chat_info = await app.get_chat(MUST_JOIN2)
            name = chat_info.first_name
            link = chat_info.invite_link

        try:
            await msg.reply(
                f"**• Sorry . . {msg.from_user.mention}\n• You must first join channel to use me\n• Channel: « @{MUST_JOIN2} »\n\n• ببووره . . ئەزیزم {msg.from_user.mention}\n• سەرەتا پێویستە جۆینی کەناڵ بکەیت بۆ بەکارهێنانم\n• کەناڵ: « @{MUST_JOIN2} »**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(name, url=link),
                        ]
                    ]
                ),
                disable_web_page_preview=True,
            )
            await msg.stop_propagation()
        except ChatWriteForbidden:
            pass
        return  # Stop here if the user is not in the second channel

    # If user is in either of the channels, proceed normally

    except ChatAdminRequired:
        print(f"**بۆت بکە ئەدمین لە کەناڵی**: {MUST_JOIN_1} or {MUST_JOIN_2} !")
