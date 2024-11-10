from AlinaMusic import app
from config import MUST_JOIN, MUST_JOIN2
from pyrogram import Client, filters
from pyrogram.errors import (ChatAdminRequired, ChatWriteForbidden,
                             UserNotParticipant)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# --------------------------
# Assuming MUST_JOIN is a list of channel usernames or IDs, like: MUST_JOIN = ["channel1", "channel2"]
MUST_JOINN = ["MUST_JOIN", "MUST_JOIN2"]

@app.on_message(filters.incoming & filters.private, group=-2)
async def must_join_channel(app: Client, msg: Message):
    if not MUST_JOINN:
        return
    for channel in MUST_JOINN:
        try:
            await app.get_chat_member(channel, msg.from_user.id)
        except UserNotParticipant:
            if channel.isalpha():
                link = f"https://t.me/{channel}"
            else:
                chat_info = await app.get_chat(channel)
                name = chat_info.first_name
                link = chat_info.invite_link
            try:
                await msg.reply(
                    f"**• Sorry, {msg.from_user.mention}.\n"
                    f"• You must join all required channels to use me.\n"
                    f"• Please join: @{channel}\n\n"
                    f"• ببووره {msg.from_user.mention}.\n"
                    f"• پێویستە ئەم کەناڵەکان جۆین بکەیت بۆ بەکارهێنانم.\n"
                    f"• کەناڵ : @{channel}**",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    name, url=link
                                ),
                            ]
                        ]
                    ),
                    disable_web_page_preview=True,
                )
                await msg.stop_propagation()
                return  # Stop checking after first non-member channel
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"****بۆت بکە ئەدمین لە کەناڵی**: {MUST_JOINN}!")
    except KeyError as e:
        print(f"Username not found: {e}")
