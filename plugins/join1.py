from AlinaMusic import app
from config import MUST_JOIN, MUST_JOIN2  # Assuming two separate channel vars
from pyrogram import Client, filters
from pyrogram.errors import (ChatAdminRequired, ChatWriteForbidden, UserNotParticipant)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# --------------------------


@app.on_message(filters.incoming & filters.private, group=-1)  # Higher priority
async def must_join_channel(app: Client, msg: Message):
    try:
        # Check for the first required channel (MUST_JOIN)
        if MUST_JOIN:
            try:
                await app.get_chat_member(MUST_JOIN, msg.from_user.id)
            except UserNotParticipant:
                # Generate the link and name for MUST_JOIN
                if MUST_JOIN.isalpha():
                    link1 = f"https://t.me/{MUST_JOIN}"
                    chat_info1 = await app.get_chat(MUST_JOIN)
                    name1 = chat_info1.title
                else:
                    chat_info1 = await app.get_chat(MUST_JOIN)
                    link1 = chat_info1.invite_link
                    name1 = chat_info1.title

                try:
                    await msg.reply(
                        f"**• You must join the group\n• To be able to use command\n• Bot Group : « {name1} »\n\n• پێویستە جۆینی کەناڵ بکەیت\n• بۆ ئەوەی بتوانی فەرمان بەکاربھێنیت\n• گرووپی بۆت : « {name1} »**",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(f"• {name1} •", url=link1)]]
                        ),
                        disable_web_page_preview=True,
                    )
                    await msg.stop_propagation()
                except ChatWriteForbidden:
                    pass
                return  # Stop further processing after sending the prompt for MUST_JOIN

        # Check for the second required channel (MUST_JOIN2)
        if MUST_JOIN2:
            try:
                await app.get_chat_member(MUST_JOIN2, msg.from_user.id)
            except UserNotParticipant:
                # Generate the link and name for MUST_JOIN2
                if MUST_JOIN2.isalpha():
                    link2 = f"https://t.me/{MUST_JOIN2}"
                    chat_info2 = await app.get_chat(MUST_JOIN2)
                    name2 = chat_info2.title
                else:
                    chat_info2 = await app.get_chat(MUST_JOIN2)
                    link2 = chat_info2.invite_link
                    name2 = chat_info2.title

                try:
                    await msg.reply(
                        f"**• You must join the group\n• To be able to use command\n• Bot Group : « {name2} »\n\n• پێویستە جۆینی گرووپ بکەیت\n• بۆ ئەوەی بتوانی فەرمان بەکاربھێنیت\n• گرووپی بۆت : « {name2} »**",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(f"• {name2} •", url=link2)]]
                        ),
                        disable_web_page_preview=True,
                    )
                    await msg.stop_propagation()
                except ChatWriteForbidden:
                    pass
                return  # Stop further processing after sending the prompt for MUST_JOIN2

    except ChatAdminRequired:
        print(f"**بۆت بکە ئەدمین لە کەناڵی**: {MUST_JOIN2} !")

    except Exception as e:
        print(f"An error occurred in must_join_channel function: {e}")
