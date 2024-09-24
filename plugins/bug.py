from datetime import datetime

from config import OWNER_ID as owner_id
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from strings.filters import command
from AlinaMusic import app


def content(msg: Message) -> [None, str]:
    text_to_return = msg.text

    if msg.text is None:
        return None
    if " " in text_to_return:
        try:
            return msg.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@app.on_message(command(["/bug", "ریپۆرت", "ڕیپۆرت"]))
async def bugs(_, msg: Message):
    if msg.chat.username:
        chat_username = f"@{msg.chat.username} / `{msg.chat.id}`"
    else:
        chat_username = f"**گرووپی تایبەت /** `{msg.chat.id}`"

    bugs = content(msg)
    user_id = msg.from_user.id
    mention = (
        "[" + msg.from_user.first_name + "](tg://user?id=" + str(msg.from_user.id) + ")"
    )
    datetimes_fmt = "%d-%m-%Y"
    datetimes = datetime.utcnow().strftime(datetimes_fmt)

    bug_report = f"""**
ڕاپۆرت بۆ: [﮼محمد](t.me/IQ7amo)

لەلایەن: {mention}
ئایدی بەکارهێنەر: `{user_id}`
گرووپ: {chat_username}

ڕاپۆرت: {bugs}

بەرواری ڕاپۆرت: {datetimes}**"""

    if msg.chat.type == "private":
        await msg.reply_text("<b>» ئەم فەرمانە تەنیا لە گرووپ بەکاردێت</b>")
        return

    if user_id == owner_id:
        if bugs:
            await msg.reply_text(
                "<b>» تۆ خاوەنی بۆتی دڵم</b>",
            )
            return
        else:
            await msg.reply_text("خاوەنی بۆت")
    elif user_id != owner_id:
        if bugs:
            await msg.reply_text(
                f"<b>ڕاپۆرت: {bugs}</b>\n\n"
                "<b>» بە سەرکەوتوویی ڕاپۆرتەکەت نێردرا بۆ خاوەنی بۆت!</b>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("⌯ داخستن ⌯", callback_data="close_data")]]
                ),
            )
            await app.send_photo(
                -1001962701094,
                photo="https://telegra.ph/file/25ea9bbfcf7bca252070b.jpg",
                caption=f"{bug_report}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("⌯ بینینی ڕاپۆرت ⌯", url=f"{msg.link}")],
                        [
                            InlineKeyboardButton(
                                "⌯ داخستن ⌯", callback_data="close_send_photo"
                            )
                        ],
                    ]
                ),
            )
        else:
            await msg.reply_text(
                f"<b>» هیچ شتێك نییە بۆ ڕاپۆرت!\nتکایە فەرمان بەکاربێنە لەگەڵ ڕاپۆرتەکەت\nبەکارهێنان:\n/bug باشترین بۆتە\n/report best bot music</b>",
            )


@app.on_callback_query(filters.regex("close_send_photo"))
async def close_send_photo(_, query: CallbackQuery):
    is_admin = await app.get_chat_member(query.message.chat.id, query.from_user.id)
    if not is_admin.privileges.can_delete_messages:
        await query.answer("تۆ مافی داخستنت نییە", show_alert=True)
    else:
        await query.message.delete()
