import datetime
from re import findall

import pytz
from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import is_gbanned_user
from AlinaMusic.utils.functions import check_format, extract_text_and_keyb
from AlinaMusic.utils.keyboard import ikb
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.types import (CallbackQuery, Chat, ChatMemberUpdated,
                            InlineKeyboardButton, InlineKeyboardMarkup)

from utils.error import capture_err
from utils.permissions import adminsOnly
from utils.welcomedb import (del_welcome, get_welcome, get_welcome_status,
                             set_welcome, set_welcome_status)

from .notes import extract_urls


async def handle_new_member(member, chat):
    try:
        if not member or not member.id:  # Check if member exists
            return
        if member.id in SUDOERS:
            return
        if await is_gbanned_user(member.id):
            await chat.ban_member(member.id)
            await app.send_message(
                chat.id,
                f"**• بەکارهێنەر : {member.mention}\n- باندی گشتی کراوە**\n"
                + "**- دەرکراوە لە هەموو گرووپ و کەناڵەکان**\n"
                + "**- بەهۆی ئەنجامدانی کاری نادروست**",
            )
            return
        if member.is_bot:
            return
        return await send_welcome_message(chat, member.id)
    except ChatAdminRequired:
        return


@app.on_chat_member_updated(filters.group, group=6)
@capture_err
async def welcome(_, user: ChatMemberUpdated):
    if not (
        user.new_chat_member
        and user.new_chat_member.status not in {CMS.RESTRICTED}
        and not user.old_chat_member
    ):
        return

    member = user.new_chat_member.user if user.new_chat_member else user.from_user
    if not member:
        return  # Prevent AttributeError if member is None

    chat = user.chat

    # Check if welcome is enabled for this group
    is_welcome_enabled = await get_welcome_status(chat.id)
    if not is_welcome_enabled:
        return

    return await handle_new_member(member, chat)


async def send_welcome_message(chat: Chat, user_id: int, delete: bool = False):
    welcome, raw_text, file_id = await get_welcome(chat.id)
    tz = pytz.timezone("Asia/Baghdad")

    if not raw_text:
        return
    text = raw_text
    keyb = None
    if findall(r".+\,.+", raw_text):
        text, keyb = extract_text_and_keyb(ikb, raw_text)
    u = await app.get_users(user_id)
    if "{GROUPNAME}" in text:
        text = text.replace("{GROUPNAME}", chat.title)
    if "{NAME}" in text:
        text = text.replace("{NAME}", u.mention)
    if "{ID}" in text:
        text = text.replace("{ID}", f"`{user_id}`")
    if "{FIRSTNAME}" in text:
        text = text.replace("{FIRSTNAME}", u.first_name)
    if "{SURNAME}" in text:
        sname = u.last_name or "None"
        text = text.replace("{SURNAME}", sname)
    if "{USERNAME}" in text:
        susername = u.username or "None"
        text = text.replace("{USERNAME}", susername)
    if "{DATE}" in text:
        DATE = datetime.datetime.now().strftime("%Y-%m-%d")
        text = text.replace("{DATE}", DATE)
    if "{WEEKDAY}" in text:
        WEEKDAY = datetime.datetime.now(tz).strftime("%A")
        text = text.replace("{WEEKDAY}", WEEKDAY)
    if "{TIME}" in text:
        TIME = datetime.datetime.now(tz).strftime("%H:%M:%S")
        text = text.replace("{TIME}", f"{TIME}")

    if welcome == "Text":
        m = await app.send_message(
            chat.id,
            text=text,
            reply_markup=keyb,
            disable_web_page_preview=True,
        )
    elif welcome == "Photo":
        m = await app.send_photo(
            chat.id,
            photo=file_id,
            caption=text,
            reply_markup=keyb,
        )
    elif welcome == "Video":
        m = await app.send_video(
            chat.id,
            video=file_id,
            caption=text,
            reply_markup=keyb,
        )
    else:
        m = await app.send_animation(
            chat.id,
            animation=file_id,
            caption=text,
            reply_markup=keyb,
        )


@app.on_message(
    filters.command(["/setwelcome", "دانانی بەخێرهاتن"], "") & filters.group
)
@adminsOnly("can_change_info")
async def set_welcome_func(_, message):
    usage = "**پێویستە ڕیپلەی وێنە یان گیف یان تێکست یان ڤیدیۆ بکەیت\n\nتێبینی : بۆ وێنە و گیف و ڤیدیۆ دەبێت شتێ بنووسیت لە ژێری**"
    key = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="لێرە زیاتر بزانە",
                    url=f"t.me/{app.username}?start=greetings",
                )
            ],
        ]
    )
    replied_message = message.reply_to_message
    chat_id = message.chat.id
    try:
        if not replied_message:
            await message.reply_text(usage, reply_markup=key)
            return
        if replied_message.animation:
            welcome = "Animation"
            file_id = replied_message.animation.file_id
            text = replied_message.caption
            if not text:
                return await message.reply_text(usage, reply_markup=key)
            raw_text = text.markdown
        elif replied_message.video:
            welcome = "Video"
            file_id = replied_message.video.file_id
            text = replied_message.caption
            if not text:
                return await message.reply_text(usage, reply_markup=key)
            raw_text = text.markdown
        elif replied_message.photo:
            welcome = "Photo"
            file_id = replied_message.photo.file_id
            text = replied_message.caption
            if not text:
                return await message.reply_text(usage, reply_markup=key)
            raw_text = text.markdown
        elif replied_message.text:
            welcome = "Text"
            file_id = None
            text = replied_message.text
            raw_text = text.markdown
        if replied_message.reply_markup and not findall(r".+\,.+", raw_text):
            urls = extract_urls(replied_message.reply_markup)
            if urls:
                response = "\n".join(
                    [f"{name}=[{text}, {url}]" for name, text, url in urls]
                )
                raw_text = raw_text + response
        raw_text = await check_format(ikb, raw_text)
        if raw_text:
            await set_welcome(chat_id, welcome, raw_text, file_id)
            return await message.reply_text(
                "**بە سەرکەوتوویی نامەی بەخێرهاتن لە گرووپ دانرا**"
            )
        else:
            return await message.reply_text(
                "**هەڵە هەیە لە جۆری تێکست\n\nبەکارهێنان :**\nText: `Text`\nText + Buttons: `Text ~ Buttons`",
                reply_markup=key,
            )
    except UnboundLocalError:
        return await message.reply_text("**تەنیا پشتگیری وێنە و گیف و ڤیدیۆ دەکات**")


@app.on_message(
    filters.command(["/delwelcome", "سڕینەوەی بەخێرهاتن"], "") & filters.group
)
@adminsOnly("can_change_info")
async def del_welcome_func(_, message):
    # Create an InlineKeyboardMarkup with both buttons on the same line
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("بەڵێ", callback_data="dwelcome"),
            ],
            [
                InlineKeyboardButton("نەخێر", callback_data="cdelete"),
            ],
        ]
    )

    await message.reply_text(
        "**کردارێک هەڵبژێرە بۆ سڕینەوەی بەخێرهاتن:**", reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("dwelcome"))
async def delete_welcome_callback(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    await del_welcome(chat_id)
    await query.message.edit_text("**بە سەرکەوتوویی نامەی بەخێرهاتن سڕدرایەوە.**")


@app.on_callback_query(filters.regex("cdelete"))
async def cancel_delete_callback(_, query: CallbackQuery):
    # Edit the message to inform the user that the action has been canceled
    await query.message.edit_text("**بە سەرکەوتوویی هەڵوەشێنرایەوە.**")


"""
@app.on_message(
    filters.command(
        ["/delwelcome", "/deletewelcome", "سڕینەوەی بەخێرهاتن", "سرینەوەی بەخێرهاتن"],
        "",
    )
    & ~filters.private
)
@adminsOnly("can_change_info")
async def del_welcome_func(_, message):
    chat_id = message.chat.id
    await del_welcome(chat_id)
    await message.reply_text("**بە سەرکەوتوویی نامەی بەخێرهاتن سڕدرایەوە**")

"""


@app.on_message(
    filters.command(["/getwelcome", "هێنانی بەخێرهاتن"], "") & ~filters.private
)
@adminsOnly("can_change_info")
async def get_welcome_func(_, message):
    chat = message.chat
    welcome, raw_text, file_id = await get_welcome(chat.id)
    if not raw_text:
        return await message.reply_text("**هیچ نامەیەکی بەخێرهاتن دانەنراوە**")
    if not message.from_user:
        return await message.reply_text(
            "**تۆ ئەدمینی نادیاری ناتوانی ئەم فەرمانە بەکاربێنی**"
        )

    await send_welcome_message(chat, message.from_user.id)

    await message.reply_text(
        f'**بەخێرهاتن: {welcome}\n\nشێوازی نامەی دانراو: **`{file_id}`\n\n`{raw_text.replace("`", "")}`'
    )


@app.on_message(filters.command(["/welcome", "بەخێرهاتن"], "") & filters.group)
@adminsOnly("can_change_info")
async def toggle_welcome(_, message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("چالاککردن", callback_data="welcome_enable"),
                InlineKeyboardButton("لە کارخستن", callback_data="welcome_disable"),
            ]
        ]
    )
    await message.reply_text(
        "**کردارێک هەڵبژێرە بۆ بەخێرهاتن:**", reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("welcome_enable|welcome_disable"))
async def toggle_welcome_callback(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    action = query.data

    if action == "welcome_enable":
        await set_welcome_status(chat_id, True)
        await query.message.edit_text("**ناردنی نامەی بەخێرهاتن چالاککرا.**")
    elif action == "welcome_disable":
        await set_welcome_status(chat_id, False)
        await query.message.edit_text("**ناردنی نامەی بەخێرهاتن لە کارخرا.**")


# Command to enable or disable /welcome


@app.on_message(filters.command(["/welcofefeme", "بەخffێرهاتن"], "") & ~filters.private)
@adminsOnly("can_change_info")
async def toggle_welcome(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**بەکارهێنان:** /welcome [on|off]")

    status = message.command[1].lower()
    chat_id = message.chat.id

    if status == "on" or status == "چالاک":
        await set_welcome_status(chat_id, True)
        await message.reply_text("**ناردنی نامەی بەخێرهاتن چالاککرا**")
    elif status == "off" or status == "ناچالاک":
        await set_welcome_status(chat_id, False)
        await message.reply_text("**ناردنی نامەی بەخێرهاتن ناچالاککرا**")
    else:
        await message.reply_text("**هەڵە نووسیوتە! بنووسە /welcome [on|off]**")


__MODULE__ = "Wᴇʟᴄᴏᴍᴇ"
__HELP__ = """
/welcome  [ᴏɴ, ʏ, ᴛʀᴜᴇ, ᴇɴᴀʙʟᴇ, ᴛ] - ᴛᴏ ᴛᴜʀɴ ᴏɴ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇs
/welcome [ᴏғғ, ɴ, ғᴀʟsᴇ, ᴅɪsᴀʙʟᴇ, ғ, ɴᴏ] - ᴛᴏ ᴛᴜʀɴ ᴏғғ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇs
/setwelcome - Rᴇᴘʟʏ ᴛʜɪs ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴄᴏɴᴛᴀɪɴɪɴɢ ᴄᴏʀʀᴇᴄᴛ
ғᴏʀᴍᴀᴛ ғᴏʀ ᴀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ, ᴄʜᴇᴄᴋ ᴇɴᴅ ᴏғ ᴛʜɪs ᴍᴇssᴀɢᴇ.

/delwelcome - Dᴇʟᴇᴛᴇ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ.
/getwelcome - Gᴇᴛ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ.

**SET_WELCOME ->**

**Tᴏ sᴇᴛ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ɢɪғ ᴀs ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ. Aᴅᴅ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴀs ᴄᴀᴘᴛɪᴏɴ ᴛᴏ ᴛʜᴇ ᴘʜᴏᴛᴏ ᴏʀ ɢɪғ. Tʜᴇ ᴄᴀᴘᴛɪᴏɴ ᴍᴜsᴇ ʙᴇ ɪɴ ᴛʜᴇ ғᴏʀᴍᴀᴛ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ.**

Fᴏʀ ᴛᴇxᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ɪᴜsᴛ sᴇɴᴅ ᴛʜᴇ ᴛᴇxᴛ. Tʜᴇɴ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ

Tʜᴇ ғᴏʀᴍᴀᴛ sʜᴏᴜʟᴅ ʙᴇ sᴏᴍᴇᴛʜɪɴɢ ʟɪᴋᴇ ʙᴇʟᴏᴡ.

**Hɪ** {NAME} [{ID}] Wᴇʟᴄᴏᴍᴇ ᴛᴏ {GROUPNAME}

~ #Tʜɪs sᴇᴘᴀʀᴀᴛᴇʀ (~) sʜᴏᴜʟᴅ ʙᴇ ᴛʜᴇʀᴇ ʙᴇᴛᴡᴇᴇɴ ᴛᴇxᴛ ᴀɴᴅ ʙᴜᴛᴛᴏɴs, ʀᴇᴍᴏᴠᴇ ᴛʜɪs ᴄᴏᴍᴍᴇɴᴛ ᴀʟsᴏ

Button=[Dᴜᴄᴋ, ʜᴛᴛᴘs://ᴅᴜᴄᴋᴅᴜᴄᴋɢᴏ.ᴄᴏᴍ]
Button2=[Gɪᴛʜᴜʙ, ʜᴛᴛᴘs://ɢɪᴛʜᴜʙ.ᴄᴏᴍ]
**NOTES ->**

Cʜᴇᴄᴋᴏᴜᴛ /markdownhelp ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ғᴏʀᴍᴀᴛᴛɪɴɢs ᴀɴᴅ ᴏᴛʜᴇʀ sʏɴᴛᴀx.
"""
