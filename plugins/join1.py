from AlinaMusic import app
from config import MUST_JOIN
from pyrogram import Client, filters
from pyrogram.errors import (ChatAdminRequired, ChatWriteForbidden,
                             UserNotParticipant)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    if not MUST_JOIN:
        return
    try:
        try:
            await app.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = f"https://t.me/{MUST_JOIN}"
                chat_info = await app.get_chat(MUST_JOIN)
                channel_name = chat_info.title  # Get the channel name
            else:
                chat_info = await app.get_chat(MUST_JOIN)
                link = chat_info.invite_link
                channel_name = chat_info.title  # Get the channel name

            try:
                await msg.reply(
                    f"**• Sorry . . {msg.from_user.mention}\n• You must first join channel to use me\n• Channel : « @{MUST_JOIN} »\n\n• ببووره . . ئەزیزم {msg.from_user.mention}\n• سەرەتا پێویستە جۆینی کەناڵ بکەیت بۆ بەکارهێنانم\n• کەناڵ : «  @{MUST_JOIN} »**",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    # Use the channel name in the button text
                                    f"{channel_name}",
                                    url=link,
                                ),
                            ]
                        ]
                    ),
                    disable_web_page_preview=True,
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"**بۆت بکە ئەدمین لە کەناڵی**: {MUST_JOIN} !")
