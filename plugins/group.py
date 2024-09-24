from pyrogram import enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from strings.filters import command
from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.alina_ban import admin_filter
from AlinaMusic.utils.database import add_served_chat

# ------------------------------------------------------------------------------- #


@app.on_message(
    filters.command(
        ["/pin", "پین", "هەڵواسین"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]
    )
    & admin_filter
)
async def pin(_, message):
    replied = message.reply_to_message
    chat_title = message.chat.title
    chat_id = message.chat.id
    user_id = message.from_user.id
    name = message.from_user.mention

    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text("**ئەم فەرمانە تەنیا لە گرووپەکان کاردەکات!**")
    elif not replied:
        await message.reply_text("**وەڵامی نامەیەك بدەوە بۆ ئەوەی پینی بکەیت!**")
    else:
        user_stats = await app.get_chat_member(chat_id, user_id)
        if user_stats.privileges.can_pin_messages and message.reply_to_message:
            try:
                await message.reply_to_message.pin()
                await message.reply_text(
                    f"**بە سەرکەوتوویی نامەکە پینکرا!**\n\n**گرووپ:** {chat_title}\n**ئەدمین:** {name}",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(" 📝 بینینی نامەکان", url=replied.link)]]
                    ),
                )
            except Exception as e:
                await message.reply_text(str(e))


@app.on_message(
    filters.command(
        ["pinned", "پینکراوەکان", "هەڵواسراوەکان"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
)
async def pinned(_, message):
    chat = await app.get_chat(message.chat.id)
    if not chat.pinned_message:
        return await message.reply_text("**هیچ پینێك نەدۆزرایەوە**")
    try:
        await message.reply_text(
            "لێرە لیستی هەڵواسراوەکان، پینکراوەکان ببینە",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="📝 بینینی نامەکان", url=chat.pinned_message.link
                        )
                    ]
                ]
            ),
        )
    except Exception as er:
        await message.reply_text(er)


# ------------------------------------------------------------------------------- #


@app.on_message(
    filters.command(
        ["unpin", "لادانی پین", "لادانی هەڵواسین"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & admin_filter
)
async def unpin(_, message):
    replied = message.reply_to_message
    chat_title = message.chat.title
    chat_id = message.chat.id
    user_id = message.from_user.id
    name = message.from_user.mention

    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text("**ئەم فەرمانە تەنیا لە گرووپەکان کاردەکات!**")
    elif not replied:
        await message.reply_text("**وەڵامی نامەیەك بدەوە بۆ ئەوەی لایدەی لە پین!**")
    else:
        user_stats = await app.get_chat_member(chat_id, user_id)
        if user_stats.privileges.can_pin_messages and message.reply_to_message:
            try:
                await message.reply_to_message.unpin()
                await message.reply_text(
                    f"**بە سەرکەوتوویی لە پین لادرا!**\n\n**گرووپ:** {chat_title}\n**ئەدمین:** {name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    " 📝 بینینی نامەکان ", url=replied.link
                                )
                            ]
                        ]
                    ),
                )
            except Exception as e:
                await message.reply_text(str(e))


# --------------------------------------------------------------------------------- #


@app.on_message(
    filters.command(
        ["removephoto", "لادانی وێنە", "rphoto"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & admin_filter
)
async def deletechatphoto(_, message):

    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("**پڕۆسەی دەکات ..**")
    admin_check = await app.get_chat_member(chat_id, user_id)
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("**ئەم فەرمانە تەنیا لە گرووپەکان کاردەکات!**")
    try:
        if admin_check.privileges.can_change_info:
            await app.delete_chat_photo(chat_id)
            await msg.edit(
                "**بە سەرکەوتوویی وێنەی گرووپ لابردرا!\nلەلایەن {} **".format(
                    message.from_user.mention
                )
            )
    except:
        await msg.edit(
            "**پێویستە ڕۆڵی دەستکاری کردنی زانیاری گرووپت هەبێت بۆ لادانی وێنەی گرووپ**"
        )


# --------------------------------------------------------------------------------- #


@app.on_message(
    filters.command(
        ["setphoto", "دانانی وێنە", "sphoto"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & admin_filter
)
async def setchatphoto(_, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("**پڕۆسەی دەکات . . .**")
    admin_check = await app.get_chat_member(chat_id, user_id)
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("**ئەم فەرمانە تەنیا لە گرووپەکان کاردەکات!**")
    elif not reply:
        await msg.edit("**وەڵامی وێنەیەك بدەوە بۆ دانانی لە پڕۆفایلی گرووپ**")
    elif reply:
        try:
            if admin_check.privileges.can_change_info:
                photo = await reply.download()
                await message.chat.set_photo(photo=photo)
                await msg.edit_text(
                    "**بە سەرکەوتوویی وێنەی گرووپ دانرا!\nلەلایەن {}**".format(
                        message.from_user.mention
                    )
                )
            else:
                await msg.edit(
                    "**هەندێك جیاوازی و هەڵە ڕوویدا وێنەیەکی تر تاقیبکەوە!**"
                )

        except:
            await msg.edit(
                "**پێویستە ڕۆڵی دەستکاری کردنی زانیاری گرووپت هەبێت بۆ دانانی وێنەی گرووپ**"
            )


# --------------------------------------------------------------------------------- #


@app.on_message(
    filters.command(
        ["settitle", "گۆڕینی ناو", "stitle"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & admin_filter
)
async def setgrouptitle(_, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("**پڕۆسەی دەکات . . .**")
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("**ئەم فەرمانە تەنیا لە گرووپەکان کاردەکات!**")
    elif reply:
        try:
            title = message.reply_to_message.text
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_title(title)
                await msg.edit(
                    "**بە سەرکەوتوویی ناوی گرووپ گۆڕدرا!\nلەلایەن {}**".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**پێویستە ڕۆڵی دەستکاری کردنی زانیاری گرووپت هەبێت بۆ گۆڕینی ناوی گرووپ!**"
            )
    elif len(message.command) > 1:
        try:
            title = message.text.split(None, 1)[1]
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_title(title)
                await msg.edit(
                    "**بە سەرکەوتوویی ناوی گرووپ گۆڕدرا!\nلەلایەن {}**".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**پێویستە ڕۆڵی دەستکاری کردنی زانیاری گرووپت هەبێت بۆ گۆڕینی ناوی گرووپ!**"
            )

    else:
        await msg.edit(
            "**پێویستە وڵامی ئەو ناوە بدەیتەوە یان لەگەڵ فەرمان بینووسی بۆ ئەوەی ناوی گرووپ بگۆڕێت!**"
        )


# --------------------------------------------------------------------------------- #


@app.on_message(
    filters.command(
        ["setdiscription", "گۆڕینی بایۆ", "sbio"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & admin_filter
)
async def setg_discription(_, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("**پڕۆسەی دەکات . . .**")
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("**ئەم فەرمانە تەنیا لە گرووپەکان کاردەکات!**")
    elif reply:
        try:
            discription = message.reply_to_message.text
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_description(discription)
                await msg.edit(
                    "**بە سەرکەوتوویی بایۆی گرووپ گۆڕدرا!\nلەلایەن {}**".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**پێویستە ڕۆڵی دەستکاری کردنی زانیاری گرووپت هەبێت بۆ گۆڕینی بایۆی گرووپ!**"
            )
    elif len(message.command) > 1:
        try:
            discription = message.text.split(None, 1)[1]
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_description(discription)
                await msg.edit(
                    "**بە سەرکەوتوویی ناوی گرووپ گۆڕدرا!\nلەلایەن {}**".format(
                        message.from_user.mention
                    )
                )
        except AttributeError:
            await msg.edit(
                "**پێویستە ڕۆڵی دەستکاری کردنی زانیاری گرووپت هەبێت بۆ گۆڕینی بایۆی گرووپ!**"
            )
    else:
        await msg.edit(
            "**پێویستە وڵامی ئەو ناوە بدەیتەوە یان لەگەڵ فەرمان بینووسی بۆ ئەوەی بایۆی گرووپ بگۆڕێت!**"
        )


# --------------------------------------------------------------------------------- #


@app.on_message(command(["/leave", "لێفتکە"]) & SUDOERS)
async def bot_leave(_, message):
    chat_id = message.chat.id
    buttons = [[InlineKeyboardButton("گرووپی بۆت", url=f"https://t.me/IQSUPP")]]
    await message.reply_text(
        "<b>ببورە بەڕیزم\nخاوەنەکەم پێی وتم کە دەربچم لەم گرووپە بۆ هەر کێشەیەك سەردانی گرووپی بۆت بکە</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    await app.leave_chat(chat_id=chat_id, delete=True)


# --------------------------------------------------------------------------------- #


@app.on_message(command(["/lg", "دەرکردنی بۆت"]) & SUDOERS)
async def leave_a_chat(client, message):
    if len(message.command) == 1:
        return await message.reply("**ئایدی یان یوزەر گرووپم پێبدە**")
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[InlineKeyboardButton("گرووپی بۆت", url=f"https://t.me/IQSUPP")]]
        await client.send_message(
            chat_id=chat,
            text="<b>ببورە بەڕیزم\nخاوەنەکەم پێی وتم کە دەربچم لەم گرووپە بۆ هەر کێشەیەك سەردانی گرووپی بۆت بکە</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        await client.leave_chat(chat)
    except Exception as e:
        await message.reply(f"**هەڵە: {e} **")


# --------------------------------------------------------------------------------- #

# --------------------------------------------------------------------------------- #


@app.on_message(
    filters.command(
        [
            "hi",
            "السلام علیک",
            "hello",
            "slaw",
            "good",
            "bash",
            "ok",
            "bye",
            "بەخێربێی",
            "thank",
            "bale",
            "gyan",
            "سلاو",
            "سڵاو",
            "سلام",
            "چۆنن",
            "سپاس",
            "سوپاس",
            "wlc",
            "وەرە",
            "بڕۆ",
            "join",
            "dll",
            "help",
            "جۆین",
        ],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & ~filters.private
)
async def bot_check(_, message):
    chat_id = message.chat.id
    await add_served_chat(chat_id)


# --------------------------------------------------------------------------------- #
