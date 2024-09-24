import logging
import uuid

from AlinaMusic import app
from AlinaMusic.utils.alina_ban import admin_filter
from AlinaMusic.utils.database import get_assistant
from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.raw import base
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import (
    CreateGroupCall,
    DiscardGroupCall,
    GetGroupParticipants,
)
from pyrogram.types import Message


@app.on_message(
    filters.command(["/vcstart", "/open", "کردنەوەی تێل", "کردنەوەی تیل"], "")
    & admin_filter
)
async def startvc(client, message: Message):

    call_name = (
        message.text.split(maxsplit=1)[1] if len(message.command) > 1 else " Voice Chat"
    )
    hell = await message.reply_text("**•⎆┊تێل دەکرێتەوە ...♥️•**")
    userbot = await get_assistant(message.chat.id)

    try:
        await userbot.invoke(
            CreateGroupCall(
                peer=(await userbot.resolve_peer(message.chat.id)),
                random_id=int(str(uuid.uuid4().int)[:8]),
                title=call_name,
            )
        )

        await hell.edit_text("**•⎆┊بە سەرکەوتوویی تێل کرایەوە♥️⚡️•**")
    except ChatAdminRequired:
        await hell.edit_text("**•⎆┊ڕۆڵی بەڕێوەبردنی تێلم پێویستە♥️⚡️•**")
    except Exception as e:
        logging.exception(e)
        await hell.edit_text(str(e))


@app.on_message(
    filters.command(["/vcend", "/close", "داخستنی تێل", "داخستنی تیل"], "")
    & admin_filter
)
async def endvc(client, message: Message):
    hell = await message.reply_text("**•⎆┊تێل دادەخرێت .. ♥️•**")
    userbot = await get_assistant(message.chat.id)

    try:
        full_chat: base.messages.ChatFull = await userbot.invoke(
            GetFullChannel(channel=(await userbot.resolve_peer(message.chat.id)))
        )
        await userbot.invoke(DiscardGroupCall(call=full_chat.full_chat.call))
        await hell.edit_text("**•⎆┊بە سەرکەوتوویی تێل داخرا♥️⚡️•**")
    except ChatAdminRequired:
        await hell.edit_text("**•⎆┊ڕۆڵی بەڕێوەبردنی تێلم پێویستە♥️⚡️•**")
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("**•⎆┊تێل پێشتر داخراوە•**")
        elif "phone.DiscardGroupCall" in str(e):
            await hell.edit_text("**•⎆┊ڕۆڵی بەڕێوەبردنی تێلم پێویستە♥️⚡️•**")
        else:
            logging.exception(e)
            await hell.edit_text(e)


@app.on_message(filters.command("vclink"))
async def vclink(client, message: Message):
    userbot = await get_assistant(message.chat.id)
    hell = await message.reply_text("**•⎆┊هێنانی لینکی تێل•**")

    try:
        full_chat: base.messages.ChatFull = await userbot.invoke(
            GetFullChannel(channel=(await userbot.resolve_peer(message.chat.id)))
        )

        invite: base.phone.ExportedGroupCallInvite = await userbot.invoke(
            ExportGroupCallInvite(call=full_chat.full_chat.call)
        )
        await hell.edit_text(f"**لینکی تێلی گرووپ: {invite.link}**")
    except ChatAdminRequired:
        await hell.edit_text("**•⎆┊ڕۆڵی بەڕێوەبردنی تێلم پێویستە♥️⚡️•**")
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("**•⎆┊تێل داخراوە•**")
        else:
            logging.exception(e)
            await hell.edit_text(e)


@app.on_message(filters.command("vcuser"))
async def vcmembers(client, message: Message):
    userbot = await get_assistant(message.chat.id)
    hell = await message.reply_text("**•⎆┊هێنانی ئەندامانی تێل•**")

    try:
        full_chat: base.messages.ChatFull = await userbot.invoke(
            GetFullChannel(channel=(await userbot.resolve_peer(message.chat.id)))
        )
        participants: base.phone.GroupParticipants = await userbot.invoke(
            GetGroupParticipants(
                call=full_chat.full_chat.call,
                ids=[],
                sources=[],
                offset="",
                limit=1000,
            )
        )
        count = participants.count
        text = f"**🤖| کۆی گشتی ئەندامەکان : {count}\n\n**"
        users = []
        for participant in participants.participants:
            users.append(participant.peer.user_id)
        for i in users:
            b = await app.get_users(i)
            text += f"[{b.first_name + (' ' + b.last_name if b.last_name else '')}](tg://user?id={b.id})\n"

        await hell.edit_text(text)
    except ChatAdminRequired:
        await hell.edit_text("**•⎆┊ڕۆڵی بەڕێوەبردنی تێلم پێویستە♥️⚡️•**")
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("**•⎆┊تێل داخراوە•**")
        else:
            logging.exception(e)
            await hell.edit_text(e)


__MODULE__ = "Vᴏɪᴄᴇᴄʜᴀᴛ"
__HELP__ = """
**COMMANDS:**

• /vcstart - **sᴛᴀʀᴛs ᴀ ɴᴇᴡ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.**
• /vcend - **ᴇɴᴅs ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.**
• /vcuser - **ɢᴇᴛs ᴛʜᴇ ᴜsᴇʀs ɪɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.**

**INFO:**

- ᴛʜɪs ʙᴏᴛ ᴘʀᴏᴠɪᴅᴇs ᴀ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴛᴀʀᴛ, ᴇɴᴅ, ᴀɴᴅ ɢᴇᴛ ᴛʜᴇ ᴜsᴇʀs ɪɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.

**NOTE:**

- ᴛʜɪs ᴀssɪsᴛᴀɴᴛ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴛᴏ ᴜsᴇ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴄᴏᴍᴍᴀɴᴅs.
"""
