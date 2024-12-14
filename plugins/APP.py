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
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup)

from utils.error import capture_err
from utils.permissions import adminsOnly
from utils.welcomedb import (del_welcome, get_welcome, get_welcome_status,
                             set_welcome, set_welcome_status)


async def handle_new_member(member, chat):
    try:
        if not member or not member.id:
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
async def welcome(_, user):
    if not (
        user.new_chat_member
        and user.new_chat_member.status not in {CMS.RESTRICTED}
        and not user.old_chat_member
    ):
        return

    member = user.new_chat_member.user if user.new_chat_member else user.from_user
    if not member:
        return

    chat = user.chat

    is_welcome_enabled = await get_welcome_status(chat.id)
    if not is_welcome_enabled:
        return

    return await handle_new_member(member, chat)


async def send_welcome_message(chat, user_id, delete=False):
    welcome, raw_text, file_id = await get_welcome(chat.id)
    tz = pytz.timezone("Asia/Baghdad")

    if not raw_text:
        return
    text = raw_text
    keyb = None
    if findall(r"~.+,.+~", raw_text):
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


@app.on_message(filters.command(["/welcome", "بەخێرهاتن"], "") & filters.group)
@adminsOnly("can_change_info")
async def toggle_welcome(_, message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Enable", callback_data="welcome_enable"),
                InlineKeyboardButton("Disable", callback_data="welcome_disable"),
            ]
        ]
    )
    await message.reply_text(
        "**Choose an action for welcome messages:**", reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("welcome_enable|welcome_disable"))
async def toggle_welcome_callback(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    action = query.data

    if action == "welcome_enable":
        await set_welcome_status(chat_id, True)
        await query.message.edit_text("**Welcome messages enabled.**")
    elif action == "welcome_disable":
        await set_welcome_status(chat_id, False)
        await query.message.edit_text("**Welcome messages disabled.**")


@app.on_message(
    filters.command(["/setwelcome", "دانانی بەخێرهاتن"], "") & filters.group
)
@adminsOnly("can_change_info")
async def set_welcome_func(_, message):
    usage = "**Usage:**\nSend a message or media along with /setwelcome to set a welcome message.\n\n**Note:** For photos, videos, and animations, add a caption."
    key = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Learn More",
                    url=f"t.me/{app.username}?start=greetings",
                )
            ],
        ]
    )

    chat_id = message.chat.id
    replied_message = message.reply_to_message
    welcome_type = None
    file_id = None
    raw_text = None

    try:
        # Check if the user replied to a message
        if replied_message:
            if replied_message.animation:
                welcome_type = "Animation"
                file_id = replied_message.animation.file_id
                raw_text = replied_message.caption or ""
            elif replied_message.video:
                welcome_type = "Video"
                file_id = replied_message.video.file_id
                raw_text = replied_message.caption or ""
            elif replied_message.photo:
                welcome_type = "Photo"
                file_id = replied_message.photo.file_id
                raw_text = replied_message.caption or ""
            elif replied_message.text:
                welcome_type = "Text"
                file_id = None
                raw_text = replied_message.text

        # No reply: Handle message text directly from the command
        else:
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                return await message.reply_text(usage, reply_markup=key)

            welcome_type = "Text"
            raw_text = args[1]

        # Process buttons if included
        if message.reply_markup and not findall(r".+\,.+", raw_text):
            urls = extract_urls(message.reply_markup)
            if urls:
                response = "\n".join(
                    [f"{name}=[{text}, {url}]" for name, text, url in urls]
                )
                raw_text = raw_text + response

        # Validate the format and store the welcome message
        raw_text = await check_format(ikb, raw_text)
        if raw_text:
            await set_welcome(chat_id, welcome_type, raw_text, file_id)
            return await message.reply_text(
                "**Welcome message has been successfully set for the group.**"
            )
        else:
            return await message.reply_text(
                "**Error in text formatting!**\n\n**Usage:**\nText: `Text`\nText + Buttons: `Text ~ Buttons`",
                reply_markup=key,
            )

    except UnboundLocalError:
        return await message.reply_text("**Only supports text, photo, GIF, or video.**")


@app.on_message(
    filters.command(["/delwelcome", "سڕینەوەی بەخێرهاتن"], "") & filters.group
)
@adminsOnly("can_change_info")
async def del_welcome_func(_, message):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Delete Welcome", callback_data="delete_welcome")]]
    )
    await message.reply_text(
        "**Click below to delete the welcome message.**", reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("delete_welcome"))
async def delete_welcome_callback(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    await del_welcome(chat_id)
    await query.message.edit_text("**Welcome message deleted successfully.**")
