import datetime
import re

from AlinaMusic import app
from AlinaMusic.utils.database import (
    delete_all_global_filters,
    delete_global_filter,
    deleteall_filters,
    get_filter,
    get_filters_names,
    get_global_filter,
    get_global_filter_names,
    save_filter,
    save_global_filter,
)
from AlinaMusic.utils.functions import (
    check_format,
    extract_text_and_keyb,
    get_data_and_name,
)
from AlinaMusic.utils.keyboard import ikb
from config import BANNED_USERS
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.error import capture_err
from utils.permissions import adminsOnly, member_permissions

from .notes import extract_urls


@app.on_message(filters.command("filter") & filters.group & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def save_filters(_, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "**Usage:**\nReply to a message with /filter [FILTER_NAME] [CONTENT] to set a new filter."
            )

        replied_message = message.reply_to_message or message
        data, name = await get_data_and_name(replied_message, message)

        if len(name) < 2:
            return await message.reply_text(
                f"To filter, the {name} must be greater than 2 words."
            )

        if data == "error":
            return await message.reply_text(
                "**Usage:**\n/filter [FILTER_NAME] [CONTENT]\n`-----------OR-----------`\nReply to a message with /filter [FILTER_NAME]."
            )

        file_id = None
        _type = None

        if replied_message.text:
            _type = "text"
        elif replied_message.sticker:
            _type = "sticker"
            file_id = replied_message.sticker.file_id
        elif replied_message.animation:
            _type = "animation"
            file_id = replied_message.animation.file_id
        elif replied_message.photo:
            _type = "photo"
            file_id = replied_message.photo.file_id
        elif replied_message.document:
            _type = "document"
            file_id = replied_message.document.file_id
        elif replied_message.video:
            _type = "video"
            file_id = replied_message.video.file_id
        elif replied_message.video_note:
            _type = "video_note"
            file_id = replied_message.video_note.file_id
        elif replied_message.audio:
            _type = "audio"
            file_id = replied_message.audio.file_id
        elif replied_message.voice:
            _type = "voice"
            file_id = replied_message.voice.file_id

        # Extract URLs if reply markup exists and data doesn't match regex
        if replied_message.reply_markup and not re.findall(r"\[.+\,.+\]", data):
            urls = extract_urls(replied_message.reply_markup)
            if urls:
                response = "\n".join(
                    [f"{name}=[{text}, {url}]" for name, text, url in urls]
                )
                data += response

        if data:
            data = await check_format(ikb, data)
            if not data:
                return await message.reply_text(
                    "**Wrong formatting, check the help section.**"
                )

        name = name.replace("_", " ")
        _filter = {
            "type": _type,
            "data": data,
            "file_id": file_id,
        }

        chat_id = message.chat.id
        await save_filter(chat_id, name, _filter)
        return await message.reply_text(f"__**Saved filter {name}.**__")
    except UnboundLocalError:
        return await message.reply_text(
            "**The replied message is inaccessible.\n`Forward the message and try again.`**"
        )


@app.on_message(filters.command("filters") & filters.group & ~BANNED_USERS)
@capture_err
async def get_filters(_, message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        return await message.reply_text("**No filters in the chat.**")

    _filters.sort()
    msg = f"List of filters in the **{message.chat.title}**:\n"
    msg += "\n".join([f"**-** `{_filter}`" for _filter in _filters])
    await message.reply_text(msg)


@app.on_message(
    filters.text
    & ~filters.private
    & ~filters.channel
    & ~filters.via_bot
    & ~filters.forwarded
    & ~BANNED_USERS,
    group=1,
)
@capture_err
async def filters_response(_, message):
    from_user = message.from_user if message.from_user else message.sender_chat
    user_id = from_user.id
    chat_id = message.chat.id
    text = message.text.lower().strip()

    if not text:
        return

    list_of_filters = await get_filters_names(chat_id)
    for word in list_of_filters:
        pattern = r"( |^|[^\w])" + re.escape(word) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            _filter = await get_filter(chat_id, word)
            data_type = _filter["type"]
            data = _filter["data"]
            file_id = _filter.get("file_id")
            keyb = None

            if data:
                # Replace placeholders with actual values
                replacements = {
                    "{app.mention}": app.mention,
                    "{GROUPNAME}": message.chat.title,
                    "{NAME}": message.from_user.mention,
                    "{ID}": str(from_user.id),
                    "{FIRSTNAME}": message.from_user.first_name,
                    "{SURNAME}": message.from_user.last_name or "None",
                    "{USERNAME}": message.from_user.username or "None",
                    "{DATE}": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "{WEEKDAY}": datetime.datetime.now().strftime("%A"),
                    "{TIME}": datetime.datetime.now().strftime("%H:%M:%S"),
                }
                for placeholder, value in replacements.items():
                    data = data.replace(placeholder, value)

                if re.findall(r"\[.+\,.+\]", data):
                    keyboard = extract_text_and_keyb(ikb, data)
                    if keyboard:
                        data, keyb = keyboard

            replied_message = message.reply_to_message
            if replied_message:
                replied_user = (
                    replied_message.from_user
                    if replied_message.from_user
                    else replied_message.sender_chat
                )
                if text.startswith("~"):
                    await message.delete()
                if replied_user.id != from_user.id:
                    message = replied_message

            if data_type == "text":
                await message.reply_text(
                    text=data,
                    reply_markup=keyb,
                    disable_web_page_preview=True,
                )
            elif file_id:  # Only check for file_id if data_type requires it
                if data_type == "sticker":
                    await message.reply_sticker(sticker=file_id)
                elif data_type == "animation":
                    await message.reply_animation(
                        animation=file_id, caption=data, reply_markup=keyb
                    )
                elif data_type == "photo":
                    await message.reply_photo(
                        photo=file_id, caption=data, reply_markup=keyb
                    )
                elif data_type == "document":
                    await message.reply_document(
                        document=file_id, caption=data, reply_markup=keyb
                    )
                elif data_type == "video":
                    await message.reply_video(
                        video=file_id, caption=data, reply_markup=keyb
                    )
                elif data_type == "video_note":
                    await message.reply_video_note(video_note=file_id)
                elif data_type == "audio":
                    await message.reply_audio(
                        audio=file_id, caption=data, reply_markup=keyb
                    )
                elif data_type == "voice":
                    await message.reply_voice(
                        voice=file_id, caption=data, reply_markup=keyb
                    )

            return  # Avoid filter spam


@app.on_message(filters.command("stopall") & filters.group & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def stop_all(_, message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        await message.reply_text("**No filters in this chat.**")
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Yes, do it", callback_data="stop_yes"),
                    InlineKeyboardButton("No, don't do it", callback_data="stop_no"),
                ]
            ]
        )
        await message.reply_text(
            "**Are you sure you want to delete all the filters in this chat forever?**",
            reply_markup=keyboard,
        )


@app.on_callback_query(filters.regex("stop_(.*)") & ~BANNED_USERS)
async def stop_all_cb(_, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)

    if "can_change_info" not in permissions:
        return await cb.answer(
            "You don't have the required permission.\nPermission: can_change_info",
            show_alert=True,
        )

    input = cb.data.split("_", 1)[1]
    if input == "yes":
        stopped_all = await deleteall_filters(chat_id)
        if stopped_all:
            return await cb.message.edit(
                "**Successfully deleted all filters in this chat.**"
            )
    if input == "no":
        await cb.message.reply_to_message.delete()
        await cb.message.delete()


@app.on_message(filters.command("gfilter") & filters.group & ~BANNED_USERS)
async def save_global_filter_command(_, message):
    if message.from_user.id != 833360381:  # Check for the bot owner
        return await message.reply_text("**Only the bot owner can use this command.**")

    try:
        if not message.reply_to_message:  # Check if there's a replied message
            return await message.reply_text(
                "**Usage:**\nReply to a message with `/gfilter [FILTER_NAME] [CONTENT]`."
            )

        # Extract filter name and content from the message text
        content_parts = message.text.split(" ", 2)
        if len(content_parts) < 3:
            return await message.reply_text(
                "**Usage:**\n/gfilter [FILTER_NAME] [CONTENT] to set a new global filter."
            )

        filter_name = content_parts[1]
        filter_content = content_parts[2]

        replied_message = message.reply_to_message
        file_id = None
        _type = None

        # Determine the type of the replied message
        if replied_message.text:
            _type = "text"
        elif replied_message.sticker:
            _type = "sticker"
            file_id = replied_message.sticker.file_id
        elif replied_message.animation:
            _type = "animation"
            file_id = replied_message.animation.file_id
        elif replied_message.photo:
            _type = "photo"
            file_id = replied_message.photo.file_id
        elif replied_message.document:
            _type = "document"
            file_id = replied_message.document.file_id
        elif replied_message.video:
            _type = "video"
            file_id = replied_message.video.file_id
        elif replied_message.video_note:
            _type = "video_note"
            file_id = replied_message.video_note.file_id
        elif replied_message.audio:
            _type = "audio"
            file_id = replied_message.audio.file_id
        elif replied_message.voice:
            _type = "voice"
            file_id = replied_message.voice.file_id

        # Save the global filter in the database
        _filter = {
            "type": _type,
            "data": filter_content,
            "file_id": file_id,
        }

        await save_global_filter(filter_name, _filter)  # Save the global filter
        return await message.reply_text(f"__**Saved global filter {filter_name}.**__")
    except Exception as e:
        return await message.reply_text(f"**An error occurred:** {str(e)}")


@app.on_message(
    filters.text
    & ~filters.private
    & ~filters.channel
    & ~filters.via_bot
    & ~BANNED_USERS
)
async def global_filters_response(_, message):
    text = message.text.lower().strip()
    global_filters = await get_global_filter_names()

    for filter_name in global_filters:
        global_filter = await get_global_filter(filter_name)
        if not global_filter:
            continue

        # Check if the filter should trigger (you can modify this logic)
        pattern = r"( |^|[^\w])" + re.escape(filter_name) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            data_type = global_filter["type"]
            data = global_filter["data"]
            file_id = global_filter.get("file_id")

            # Send the appropriate response based on the filter type
            if data_type == "text":
                await message.reply_text(data)
            elif file_id:
                if data_type == "sticker":
                    await message.reply_sticker(sticker=file_id)
                elif data_type == "animation":
                    await message.reply_animation(animation=file_id, caption=data)
                elif data_type == "photo":
                    await message.reply_photo(photo=file_id, caption=data)
                elif data_type == "document":
                    await message.reply_document(document=file_id, caption=data)
                elif data_type == "video":
                    await message.reply_video(video=file_id, caption=data)
                elif data_type == "voice":
                    await message.reply_voice(voice=file_id, caption=data)
                elif data_type == "audio":
                    await message.reply_audio(audio=file_id, caption=data)

            return  # Stop further processing if a global filter triggered


@app.on_message(filters.command("delgfilter") & filters.group & ~BANNED_USERS)
async def delete_global_filter_command(_, message):
    # Check if the message sender is the bot owner
    if message.from_user.id != 833360381:
        return await message.reply_text("**Only the bot owner can use this command.**")

    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "**Usage:**\n/deleteglobalfilter [FILTER_NAME]"
            )

        name = message.command[1]

        # Delete the global filter from the database
        if await delete_global_filter(name):
            return await message.reply_text(f"__**Deleted global filter {name}.**__")
        else:
            return await message.reply_text(f"**Global filter {name} not found.**")
    except Exception as e:
        return await message.reply_text(f"**An error occurred:** {str(e)}")


@app.on_message(filters.command("delallgfilters") & filters.group & ~BANNED_USERS)
async def delete_all_global_filters_command(_, message):
    if message.from_user.id != 833360381:  # Check for the bot owner
        return await message.reply_text("**Only the bot owner can use this command.**")

    try:
        # Confirm the deletion of all global filters
        confirmation_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Yes, delete all", callback_data="confirm_delete_all"
                    ),
                    InlineKeyboardButton(
                        "No, cancel", callback_data="cancel_delete_all"
                    ),
                ]
            ]
        )
        await message.reply_text(
            "**Are you sure you want to delete all global filters?**",
            reply_markup=confirmation_keyboard,
        )
    except Exception as e:
        return await message.reply_text(f"**An error occurred:** {str(e)}")


@app.on_callback_query(filters.regex("confirm_delete_all") & ~BANNED_USERS)
async def confirm_delete_all_cb(_, cb):
    try:
        # Delete all global filters
        await delete_all_global_filters()
        await cb.message.edit("**Successfully deleted all global filters.**")
    except Exception as e:
        await cb.message.edit(f"**An error occurred:** {str(e)}")


@app.on_callback_query(filters.regex("cancel_delete_all") & ~BANNED_USERS)
async def cancel_delete_all_cb(_, cb):
    await cb.answer("Deletion canceled.", show_alert=True)


__MODULE__ = "Fɪʟᴛᴇʀs"
__HELP__ = """/filters To Get All The Filters In The Chat.
/filter [FILTER_NAME] To Save A Filter(reply to a message).

Supported filter types are Text, Animation, Photo, Document, Video, video notes, Audio, Voice.

To use more words in a filter use.
`/filter Hey_there` To filter "Hey there".

/stop [FILTER_NAME] To Stop A Filter.
/stopall To delete all the filters in a chat (permanently).

You can use markdown or html to save text too.

Checkout /markdownhelp to know more about formattings and other syntax.
"""
