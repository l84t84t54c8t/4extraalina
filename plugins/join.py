from AlinaMusic import app
from config import MUST_JOIN2
from pyrogram import Client, filters
from pyrogram.errors import (ChatAdminRequired, ChatWriteForbidden,
                             UserNotParticipant)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    if not MUST_JOIN2:
        return
    try:
        try:
            await app.get_chat_member(MUST_JOIN2, msg.from_user.id)
        except UserNotParticipant:
            # Set a default value for channel_name
            channel_name = f"@{MUST_JOIN2}"
            if MUST_JOIN2.isalpha():
                link = "https://t.me/" + MUST_JOIN2
            else:
                chat_info = await app.get_chat(MUST_JOIN2)
                link = chat_info.invite_link # Re-assign channel_name if a title is available
            try:
                await msg.reply(
                    f"**• Sorry . . {msg.from_user.mention}\n• You must first join group to use me\n• Group : « @{MUST_JOIN2} »\n\n• ببووره . . ئەزیزم {msg.from_user.mention}\n• سەرەتا پێویستە جۆینی گرووپ بکەیت بۆ بەکارهێنانم\n• گرووپ : «  @{MUST_JOIN2} »**",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(text="گرووپی ئەلینا", url=link),
                            ]
                        ]
                    ),
                    disable_web_page_preview=True,
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"**بۆت بکە ئەدمین لە کەناڵی**: {MUST_JOIN2} !")
