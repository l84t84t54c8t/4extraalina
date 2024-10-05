import asyncio
from contextlib import suppress
from string import ascii_lowercase
from typing import Dict, Union

from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)
from AlinaMusic.utils.keyboard import ikb
from config import BANNED_USERS
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.errors import ChatAdminRequired, InviteHashExpired, UserNotParticipant
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    ChatPrivileges,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from utils.error import capture_err
from utils.permissions import adminsOnly, member_permissions

warnsdb = mongodb.warns

__MODULE__ = "Bᴀɴ"
__HELP__ = """
/ban - Ban A User
/banall - Ban All Users
/sban - Delete all messages of user that sended in group and ban the user
/tban - Ban A User For Specific Time
/unban - Unban A User
/warn - Warn A User
/swarn - Delete all the message sended in group and warn the user
/rmwarns - Remove All Warning of A User
/warns - Show Warning Of A User
/kick - Kick A User
/skick - Delete the replied message kicking its sender
/purge - Purge Messages
/purge [n] - Purge "n" number of messages from replied message
/del - Delete Replied Message
/promote - Promote A Member
/fullpromote - Promote A Member With All Rights
/demote - Demote A Member
/pin - Pin A Message
/unpin - unpin a message
/unpinall - unpinall messages
/mute - Mute A User
/tmute - Mute A User For Specific Time
/unmute - Unmute A User
/zombies - Ban Deleted Accounts
/report | @admins | @admin - Report A Message To Admins."""


async def int_to_alpha(user_id: int) -> str:
    alphabet = list(ascii_lowercase)[:10]
    text = ""
    user_id = str(user_id)
    for i in user_id:
        text += alphabet[int(i)]
    return text


async def get_warns_count() -> dict:
    chats_count = 0
    warns_count = 0
    async for chat in warnsdb.find({"chat_id": {"$lt": 0}}):
        for user in chat["warns"]:
            warns_count += chat["warns"][user]["warns"]
        chats_count += 1
    return {"chats_count": chats_count, "warns_count": warns_count}


async def get_warns(chat_id: int) -> Dict[str, int]:
    warns = await warnsdb.find_one({"chat_id": chat_id})
    if not warns:
        return {}
    return warns["warns"]


async def get_warn(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    if name in warns:
        return warns[name]


async def add_warn(chat_id: int, name: str, warn: dict):
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    warns[name] = warn

    await warnsdb.update_one(
        {"chat_id": chat_id}, {"$set": {"warns": warns}}, upsert=True
    )


async def remove_warns(chat_id: int, name: str) -> bool:
    warnsd = await get_warns(chat_id)
    name = name.lower().strip()
    if name in warnsd:
        del warnsd[name]
        await warnsdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"warns": warnsd}},
            upsert=True,
        )
        return True
    return False


@app.on_message(
    filters.command(["/kick", "/skick", "دەرکردن", "دەرکردنی کاتی"], "")
    & ~filters.private
    & ~BANNED_USERS
)
@adminsOnly("can_restrict_members")
async def kickFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە**")
    if user_id == app.id:
        return await message.reply_text("**ناتوانم خۆم دەربکەم بەڕێزم**")
    if user_id in SUDOERS:
        return await message.reply_text("**ناتوانم گەشەپێدەرەکەم دەربکەم بەڕێزم**")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("**ناتوانم ئەدمینی تر دەربکەم بەڕێزم**")

    mention = (await app.get_users(user_id)).mention
    msg = f"""
**بەکارهێنەر : {mention}**
**دەرکرا لەلایەن : {message.from_user.mention if message.from_user else 'بەکارهێنەری نەناسراو'}**
**هۆکار : {reason or 'هیچ هۆکارێك نییە'}**"""
    await message.chat.ban_member(user_id)

    # Check if message.command exists and has a valid length
    if message.command and len(message.command[0]) > 0 and message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)
    await message.reply_text(msg)


# Ban members


@app.on_message(
    filters.command(["دەرم بکە", "/kickme", "/banme"], "")
    & ~filters.private
    & ~BANNED_USERS
)
async def fire_user(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە**")
    if user_id == app.id:
        return await message.reply_text("**ناتوانم خۆم دەربکەم بەڕێزم**")
    if user_id in SUDOERS:
        return await message.reply_text("**ناتوانم گەشەپێدەرەکەم دەربکەم بەڕێزم**")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("**ناتوانم ئەدمینی تر دەربکەم بەڕێزم**")

    await message.reply_text("**یەللە بۆ دەرەوە**")
    await app.ban_chat_member(message.chat.id, message.from_user.id)


@app.on_message(
    filters.command(["/ban", "/sban", "/tban", "باندی کاتی"], "")
    & ~filters.private
    & ~BANNED_USERS
)
@adminsOnly("can_restrict_members")
async def banFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)

    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە**")
    if user_id == app.id:
        return await message.reply_text("**ناتوانم خۆم دەربکەم بەڕێزم**")
    if user_id in SUDOERS:
        return await message.reply_text("**ناتوانم گەشەپێدەرەکەم دەربکەم بەڕێزم**")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("**ناتوانم ئەدمینی تر دەربکەم بەڕێزم**")

    try:
        mention = (await app.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "بەکارهێنەری نەناسراو"
        )

    msg = (
        f"**بەکارهێنەر : {mention}\n**"
        f"**دەرکرا لەلایەن : {message.from_user.mention if message.from_user else 'بەکارهێنەری نەناسراو'}\n**"
    )

    if message.command and len(message.command[0]) > 0 and message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)

    if message.command[0] == "tban":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += f"**دەرکرا بۆ : {time_value}\n**"
        if temp_reason:
            msg += f"**هۆکار : {temp_reason}**"
        with suppress(AttributeError):
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg)
            else:
                await message.reply_text("**ناتوانی لە 99 زیاتر بەکاربێنی**")
        return

    if reason:
        msg += f"**هۆکار : {reason}**"

    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg)


# Unban members


@app.on_message(
    filters.command(["/unban", "لادانی دەرکردن", "لادانی باند"], "")
    & ~filters.private
    & ~BANNED_USERS
)
@adminsOnly("can_restrict_members")
async def unban_func(_, message: Message):
    # we don't need reasons for unban, also, we
    # don't need to get "text_mention" entity, because
    # normal users won't get text_mention if the user
    # they want to unban is not in the group.
    reply = message.reply_to_message
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە**")

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text("**تۆ ناتوانی باندی کەناڵ لابەی**")

    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(f"**بەکارهێنەر : {umention}\nباندی لادرا**")


@app.on_message(
    filters.command(["promote", "fullpromote"]) & ~filters.private & ~BANNED_USERS
)
@adminsOnly("can_promote_members")
async def promoteFunc(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە**")

    bot = (await app.get_chat_member(message.chat.id, app.id)).privileges

    if user_id == app.id:
        return await message.reply_text("**ناتوانم خۆم بکەم بە ئەدمین بەڕێزم**")
    if not bot:
        return await message.reply_text("**من ئەدمین نیم بەرێزم**")
    if not bot.can_promote_members:
        return await message.reply_text("**من ڕۆڵی تەواوم نییە پێویستە ڕۆڵم هەبێت**")

    umention = (await app.get_users(user_id)).mention
    from_user_mention = message.from_user.mention

    if message.command[0][0] == "f":
        await message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=bot.can_change_info,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=bot.can_restrict_members,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=bot.can_promote_members,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            ),
        )
        await message.reply_text(
            f"**بەکارهێنەر : {umention}\nکرا بە فوول ئەدمین\nلەلایەن {from_user_mention} **",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "پشکنینی ڕۆڵی ئەدمین",
                            callback_data=f"check_powers_{user_id}",
                        )
                    ]
                ]
            ),
        )
    else:
        await message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=False,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=False,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=False,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            ),
        )
        await message.reply_text(
            f"**بەکارهێنەر : {umention}\nکرا بە ئەدمین\nلەلایەن {from_user_mention} **",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "پشکنینی ڕۆڵی ئەدمین",
                            callback_data=f"check_powers_{user_id}",
                        )
                    ]
                ]
            ),
        )


# Handle callback to check and toggle admin powers
@app.on_callback_query(filters.regex(r"^check_powers_(\d+)"))
async def check_powers_callback(_, query: CallbackQuery):
    user_id = int(query.data.split("_")[2])
    bot = (await app.get_chat_member(query.message.chat.id, app.id)).privileges
    user_privileges = (
        await app.get_chat_member(query.message.chat.id, user_id)
    ).privileges

    if not bot or not bot.can_promote_members:
        return await query.answer("**من ڕۆڵی پێویستم نییە**", show_alert=True)

    def generate_privilege_buttons(privs):
        buttons = []
        for priv, name in [
            ("can_change_info", "گۆرینی زانیاری"),
            ("can_invite_users", "بانگهێشت کردن"),
            ("can_delete_messages", "سڕینەوەی نامە"),
            ("can_restrict_members", "باند و میوت"),
            ("can_pin_messages", "هەڵواسینی نامە"),
            ("can_promote_members", "زیادکردنی ئەدمین"),
            ("can_manage_chat", "کۆنتڕۆلکردنی گرووپ"),
            ("can_manage_video_chats", "کۆنتڕۆلکردنی تێل"),
        ]:
            state = "✅ ڕێپێدراو" if getattr(privs, priv, False) else "❌ ڕێپێنەدراو"
            buttons.append(
                [
                    InlineKeyboardButton(
                        f"{name}: {state}", callback_data=f"toggle_{priv}_{user_id}"
                    )
                ]
            )
        buttons.append([InlineKeyboardButton("گەڕانەوە", callback_data="back")])
        buttons.append([InlineKeyboardButton("داخستن", callback_data="close")])
        return buttons

    await query.message.edit_caption(
        caption="**ڕۆڵی ئەدمین :\n**"
        + "\n".join(
            f"{name}: {'✅ ڕێپێدراو' if getattr(user_privileges, priv, False) else '❌ ڕێپێنەدراو'}"
            for priv, name in [
                ("can_change_info", "گۆرینی زانیاری"),
                ("can_invite_users", "بانگهێشت کردن"),
                ("can_delete_messages", "سڕینەوەی نامە"),
                ("can_restrict_members", "باند و میوت"),
                ("can_pin_messages", "هەڵواسینی نامە"),
                ("can_promote_members", "زیادکردنی ئەدمین"),
                ("can_manage_chat", "کۆنتڕۆلکردنی گرووپ"),
                ("can_manage_video_chats", "کۆنتڕۆلکردنی تێل"),
            ]
        ),
        reply_markup=InlineKeyboardMarkup(generate_privilege_buttons(user_privileges)),
    )


# Toggle admin power
@app.on_callback_query(filters.regex(r"^toggle_(.+)_(\d+)"))
async def toggle_power_callback(_, query: CallbackQuery):
    print(f"Received callback data: {query.data}")  # Add logging to check the data
    power, user_id_str = query.data.split("_")[1], query.data.split("_")[2]

    try:
        user_id = int(user_id_str)  # Attempt to convert to int
    except ValueError:
        return await query.answer("Invalid user ID.", show_alert=True)

    if not bot or not getattr(bot, power, False):
        return await query.answer("ئەم رؤلەم نییە کە بیدەم بە کەسیتر", show_alert=True)

    # Get current user privileges
    current_privs = (
        await app.get_chat_member(query.message.chat.id, user_id)
    ).privileges

    # Toggle the selected power
    new_privs = ChatPrivileges(
        can_change_info=current_privs.can_change_info,
        can_invite_users=current_privs.can_invite_users,
        can_delete_messages=current_privs.can_delete_messages,
        can_restrict_members=current_privs.can_restrict_members,
        can_pin_messages=current_privs.can_pin_messages,
        can_promote_members=current_privs.can_promote_members,
        can_manage_chat=current_privs.can_manage_chat,
        can_manage_video_chats=current_privs.can_manage_video_chats,
    )
    setattr(new_privs, power, not getattr(current_privs, power))

    # Apply the new privileges
    await query.message.chat.promote_member(user_id=user_id, privileges=new_privs)

    await query.answer(
        f"{'ڕێپێدراو' if getattr(new_privs, power) else 'ڕێپێنەدراو'} {power.replace('_', ' ').capitalize()}",
        show_alert=True,
    )

    # Update the buttons and caption
    await check_powers_callback(_, query)


@app.on_callback_query(filters.regex(r"^close"))
async def close_callback(_, query: CallbackQuery):
    await query.message.delete()


@app.on_callback_query(filters.regex(r"^back"))
async def back_callback(_, query: CallbackQuery):
    await query.message.edit_caption("**هەڵوەشایەوە ❌**")


# Demote Member


@app.on_message(filters.command("purge") & ~filters.private)
@adminsOnly("can_delete_messages")
async def purgeFunc(_, message: Message):
    repliedmsg = message.reply_to_message
    await message.delete()

    if not repliedmsg:
        return await message.reply_text("**وەڵامی نامە بدەوە بۆ سڕینەوە**")

    cmd = message.command
    if len(cmd) > 1 and cmd[1].isdigit():
        purge_to = repliedmsg.id + int(cmd[1])
        if purge_to > message.id:
            purge_to = message.id
    else:
        purge_to = message.id

    chat_id = message.chat.id
    message_ids = []

    for message_id in range(
        repliedmsg.id,
        purge_to,
    ):
        message_ids.append(message_id)

        # Max message deletion limit is 100
        if len(message_ids) == 100:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,  # For both sides
            )

            # To delete more than 100 messages, start again
            message_ids = []

    # Delete if any messages left
    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )


@app.on_message(filters.command("del") & ~filters.private)
@adminsOnly("can_delete_messages")
async def deleteFunc(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("**وەڵامی نامە بدەوە بۆ سڕینەوە**")
    await message.reply_to_message.delete()
    await message.delete()


@app.on_message(
    filters.command(["/demote", "لادانی ئەدمین"], "") & ~filters.private & ~BANNED_USERS
)
@adminsOnly("can_promote_members")
async def demote(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە**")
    if user_id == app.id:
        return await message.reply_text("**ناتوانم خۆم لابدەم لە ئەدمینی بەڕێزم**")
    if user_id in SUDOERS:
        return await message.reply_text(
            "**ناتوانم گەشەپێدەرەکەم لابدەم لە ئەدمین بەڕێزم**"
        )
    try:
        member = await app.get_chat_member(message.chat.id, user_id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            await message.chat.promote_member(
                user_id=user_id,
                privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_chat=False,
                    can_manage_video_chats=False,
                ),
            )
            umention = (await app.get_users(user_id)).mention
            await message.reply_text(f"**بەکارهێنەر : {umention}\nلادرا لە ئەدمین**")
        else:
            await message.reply_text("**ئەم بەکارهێنەرە ئەدمین نییە**")
    except Exception as e:
        await message.reply_text(e)


# Mute members


@app.on_message(
    filters.command(["/mute", "/tmute", "ئاگاداری", "ئاگاداری کاتی"], "")
    & ~filters.private
    & ~BANNED_USERS
)
@adminsOnly("can_restrict_members")
async def mute(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە*")
    if user_id == app.id:
        return await message.reply_text("**ناتوانم خۆم میوت بکەم بەڕێزم**")
    if user_id in SUDOERS:
        return await message.reply_text("**ناتوانم گەشەپێدەرەکەم میوت بکەم بەڕێزم**")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text("**ناتوانم ئەدمینی تر میوت بکەم بەڕێزم**")
    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({"🚨  لادانی میوت  🚨": f"unmute_{user_id}"})
    msg = (
        f"**بەکارهێنەر :** {mention}\n**"
        f"**میوت کرا لەلایەن : {message.from_user.mention if message.from_user else 'بەکارهێنەری نەناسراو'}\n**"
    )
    if message.command[0] == "tmute" or message.command[0] == "ئاگاداری کاتی":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += f"**میوت کرا بۆ : {time_value}\n**"
        if temp_reason:
            msg += f"**هۆکار : {temp_reason}**"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(
                    user_id,
                    permissions=ChatPermissions(),
                    until_date=temp_mute,
                )
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg, reply_markup=keyboard)
            else:
                await message.reply_text("**ناتوانی لە 99 زیاتر بەکاربێنی**")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"**هۆکار : {reason}**"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg, reply_markup=keyboard)


@app.on_message(
    filters.command(["/unmute", "لادانی ئاگاداری"], "")
    & ~filters.private
    & ~BANNED_USERS
)
@adminsOnly("can_restrict_members")
async def unmute(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("**ناتوانم بەکارهێنەر بدۆزمەوە*")
    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(f"**بەکارهێنەر : {umention}\میوتی لادرا**")


@app.on_message(filters.command(["warn", "swarn"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def warn_user(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text("**- ناتوانم بەکارھێنەر بدۆزمەوە**")
    if user_id == app.id:
        return await message.reply_text("**- ناتوانم خۆم ئاگاداربکەمەوە بەڕێزم **")
    if user_id in SUDOERS:
        return await message.reply_text("**- ناتوانم گەشەپێدەرەکەم ئاگاداربکەمەوە **")
    if user_id in [
        member.user.id
        async for member in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]:
        return await message.reply_text(
            "**- ناتوانم ئەدمینەکان ئاگاداربکەمەوە بەڕێزم**"
        )
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({"🚨  سڕینەوەی ئاگاداری  🚨": f"unwarn_{user_id}"})
    if warns:
        warns = warns["warns"]
    else:
        warns = 0
    if message.command[0][0] == "s":
        await message.reply_to_message.delete()
        await app.delete_user_history(message.chat.id, user_id)
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(
            f"**- ژمارەی ئاگادارکردنەوەکانی : {mention}\n- زۆر بووە، دەرمکرد**"
        )
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        msg = f"""
**بەکارهێنەر ئاگادارکرایەوە : {mention}**
**لەلایەن : {message.from_user.mention if message.from_user else 'نەناسراو'}**
**هۆکار : {reason or 'هیچ هۆکارێک نییە'}**
**ژمارەی ئاگادارکردنەوە : {warns + 1}/3**"""
        replied_message = message.reply_to_message
        if replied_message:
            message = replied_message
        await message.reply_text(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_") & ~BANNED_USERS)
async def remove_warning(_, cq: CallbackQuery):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "**- تۆ ڕۆڵی پێویستت نییە بۆ ئەنجامدانی ئەم فەرمانە\n**"
            + f"**ڕۆڵی پێویست : {permission}**",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer("**- بەکارهێنەر ئاگادار نەکراوەتەوە**")
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"**ئاگاداری سڕدرایەوە لەلایەن : {from_user.mention} **"
    await cq.message.edit(text)


@app.on_message(filters.command("rmwarns") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def remove_warnings(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("**- ناتوانم بەکارھێنەر بدۆزمەوە**")
    mention = (await app.get_users(user_id)).mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if warns == 0 or not warns:
        await message.reply_text(f"**- بەکارهێنەر : {mention}\n- ئاگادار نەکراوەتەوە**")
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(f"**- ئاگاداری سڕدرایەوە لەسەر : {mention}**")


@app.on_message(filters.command("warns") & ~filters.private & ~BANNED_USERS)
@capture_err
async def check_warns(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("**- ناتوانم بەکارھێنەر بدۆزمەوە**")
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    if warns:
        warns = warns["warns"]
    else:
        return await message.reply_text(
            f"**- بەکارهێنەر : {mention}\n- ئاگادار نەکراوەتەوە**"
        )
    return await message.reply_text(
        f"**- بەکارهێنەر :{mention}\n- ژمارەی ئاگاداری : {warns} لە 3**"
    )


@app.on_message(filters.command("unbanme"))
async def unbanme(client, message):
    try:
        # Check if the command has a group ID argument
        if len(message.command) < 2:
            await message.reply_text("Please provide the group ID.")
            return

        group_id = message.command[1]

        try:
            # Try to unban the user from the group
            await client.unban_chat_member(group_id, message.from_user.id)

            # Check if the user is already a participant in the group
            try:
                member = await client.get_chat_member(group_id, message.from_user.id)
                if member.status == "member":
                    await message.reply_text(
                        f"You are already unbanned in that group. You can join now by clicking here: {await get_group_link(client, group_id)}"
                    )
                    return
            except UserNotParticipant:
                pass  # The user is not a participant, proceed to unban

            # Send unban success message
            try:
                group_link = await get_group_link(client, group_id)
                await message.reply_text(
                    f"I unbanned you in the group. You can join now by clicking here: {group_link}"
                )
            except InviteHashExpired:
                await message.reply_text(
                    f"I unbanned you in the group, but I couldn't provide a link to the group."
                )
        except ChatAdminRequired:
            await message.reply_text(
                "I am not an admin in that group, so I cannot unban you."
            )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


async def get_group_link(client, group_id):
    # Try to get the group link or username
    chat = await client.get_chat(group_id)
    if chat.username:
        return f"https://t.me/{chat.username}"
    else:
        invite_link = await client.export_chat_invite_link(group_id)
        return invite_link


@app.on_message(filters.command("link") & ~BANNED_USERS)
@adminsOnly("can_invite_users")
async def invite(_, message):
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        link = (await app.get_chat(message.chat.id)).invite_link
        if not link:
            link = await app.export_chat_invite_link(message.chat.id)
        text = f"**لینکی گرووپ دروستکرا **\n\n{link}"
        if message.reply_to_message:
            await message.reply_to_message.reply_text(
                text, disable_web_page_preview=True
            )
        else:
            await message.reply_text(text, disable_web_page_preview=True)
