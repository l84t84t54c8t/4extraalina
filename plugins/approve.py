#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#

from asyncio import sleep

from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import get_assistant
from AlinaMusic.utils.keyboard import ikb
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors.exceptions.bad_request_400 import UserAlreadyParticipant
from pyrogram.types import (ChatJoinRequest, ChatPrivileges,
                            InlineKeyboardButton, InlineKeyboardMarkup)

from utils.permissions import adminsOnly, member_permissions

approvaldb = mongodb.autoapprove


def smallcap(text):
    trans_table = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢABCDEFGHIJKLMNOPQRSTUVWXYZ0𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    )
    return text.translate(trans_table)


@app.on_message(filters.command(["autoapprove", "approve"]) & filters.group)
@adminsOnly("can_change_info")
async def approval_command(client, message):
    chat_id = message.chat.id
    chat = await approvaldb.find_one({"chat_id": chat_id})
    if chat:
        mode = chat.get("mode", "")
        if not mode:
            mode = "manual"
            await approvaldb.update_one(
                {"chat_id": chat_id},
                {"$set": {"mode": mode}},
                upsert=True,
            )
        if mode == "automatic":
            switch = "manual"
            mdbutton = "ᴀᴜᴛᴏᴍᴀᴛɪᴄ"
        else:
            switch = "automatic"
            mdbutton = "ᴍᴀɴɴᴜᴀʟ"
        buttons = {
            "ناچالاککردن": "approval_off",
            f"{mdbutton}": f"approval_{switch}",
        }
        keyboard = ikb(buttons, 1)
        await message.reply(
            "**پەسەندکردنی ئۆتۆماتیکی لەم گرووپە : چالاکە**", reply_markup=keyboard
        )
    else:
        buttons = {"چالاککردن": "approval_on"}
        keyboard = ikb(buttons, 1)
        await message.reply(
            "**پەسەندکردنی ئۆتۆماتیکی لەم گرووپە : ناچالاکە**", reply_markup=keyboard
        )


@app.on_callback_query(filters.regex("approval(.*)"))
async def approval_cb(client, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        if from_user.id not in SUDOERS:
            return await cb.answer(
                f"**تۆ ڕۆڵی پێویستت نییە ئەزیزم\nڕۆڵ : {permission}**",
                show_alert=True,
            )
    command_parts = cb.data.split("_", 1)
    option = command_parts[1]
    if option == "off":
        if await approvaldb.count_documents({"chat_id": chat_id}) > 0:
            approvaldb.delete_one({"chat_id": chat_id})
            buttons = {"چالاککردن": "approval_on"}
            keyboard = ikb(buttons, 1)
            return await cb.edit_message_text(
                "**پەسەندکردنی ئۆتۆماتیکی لەم گرووپە : ناچالاکە**",
                reply_markup=keyboard,
            )
    if option == "on":
        switch = "manual"
        mode = "automatic"
    if option == "automatic":
        switch = "manual"
        mode = option
    if option == "manual":
        switch = "automatic"
        mode = option
    await approvaldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True,
    )
    chat = await approvaldb.find_one({"chat_id": chat_id})
    mode = smallcap(chat["mode"])
    buttons = {"ناچالاککردن": "approval_off", f"{mode}": f"approval_{switch}"}
    keyboard = ikb(buttons, 1)
    await cb.edit_message_text(
        "**پەسەندکردنی ئۆتۆماتیکی لەم گرووپە : چالاکە**", reply_markup=keyboard
    )


# Dictionary to track approval tasks by chat_id
approval_tasks = {}


@app.on_message(filters.command("approveall") & filters.group)
@adminsOnly("can_restrict_members")
async def approve_all(client, message):
    userbot = await get_assistant(message.chat.id)
    chat_id = message.chat.id
    a = await message.reply_text("**چاوەڕێ بکە ...**")

    # Fetch the pending join requests
    pending_users = app.get_chat_join_requests(chat_id)  # This is an async generator

    cancel_button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "- هەڵوەشاندنەوە", callback_data=f"cancel_approval:{chat_id}"
                )
            ]
        ]
    )

    # Set approval task as active
    approval_tasks[chat_id] = True

    async for user in pending_users:
        if not approval_tasks.get(chat_id):
            await message.reply_text("**پڕۆسەی پەسەندکردن هەڵوەشایەوە**")
            break

        try:
            await app.promote_chat_member(
                chat_id,
                userbot.id,
                privileges=ChatPrivileges(
                    can_change_info=True,
                    can_invite_users=True,
                ),
            )

            # Approving one user at a time
            await userbot.approve_chat_join_request(chat_id, user.from_user.id)
            await message.reply_text(
                f"**پەسەندکردنی : {user.from_user.first_name}**",
                reply_markup=cancel_button,
            )
            await sleep(2)  # Delay to simulate step-by-step approval
        except Exception as e:
            await message.reply_text(
                f"**شکست لە پەسەندکردن :\nڕۆڵی ئەدمینی زیاترم پێبدە**"
            )
            continue

    if approval_tasks.get(chat_id):
        await a.edit("**هەموو داواکاری جۆین بوون پەسەندکرا**")

    # Remove the task after completion
    approval_tasks.pop(chat_id, None)


@app.on_callback_query(filters.regex("cancel_approval"))
async def cancel_approval_callback(client, callback_query):
    chat_id = int(callback_query.data.split(":")[1])
    approval_tasks[chat_id] = False  # Cancel the approval process
    await callback_query.message.edit_text("**پڕۆسەی پەسەندکردن هەڵوەشایەوە**")


@app.on_message(filters.command(["clearpending", "unapproveall"]) & filters.group)
@adminsOnly("can_restrict_members")
async def clear_pending_command(client, message):
    chat_id = message.chat.id
    result = await approvaldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"pending_users": []}},
    )
    if result.modified_count > 0:
        await message.reply_text("**بەکارهێنەرانی چاوەڕوانکراو پاککرایەوە.**")
    else:
        await message.reply_text("**هیچ بەکارهێنەرێ چاوەڕوانکراو نییە بۆ پاککردنەوە**")


@app.on_chat_join_request(filters.group)
async def accept(client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    chat_id = await approvaldb.find_one({"chat_id": chat.id})
    if chat_id:
        mode = chat_id["mode"]
        if mode == "automatic":
            await app.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
            return
        if mode == "manual":
            is_user_in_pending = await approvaldb.count_documents(
                {"chat_id": chat.id, "pending_users": int(user.id)}
            )
            if is_user_in_pending == 0:
                await approvaldb.update_one(
                    {"chat_id": chat.id},
                    {"$addToSet": {"pending_users": int(user.id)}},
                    upsert=True,
                )
                buttons = {
                    "وەرگرتن": f"manual_approve_{user.id}",
                    "ڕەتکردنەوە": f"manual_decline_{user.id}",
                }
                keyboard = ikb(buttons, int(2))
                text = f"**بەکارهێنەر : {user.mention}\n داواکاری نارد بۆ جۆین کردنی لە گرووپ\nئایا هیچ ئەدمینێ هەیە وەریبگرێت یان ڕەتی بکاتەوە**"
                admin_data = [
                    i
                    async for i in app.get_chat_members(
                        chat_id=message.chat.id,
                        filter=ChatMembersFilter.ADMINISTRATORS,
                    )
                ]
                for admin in admin_data:
                    if admin.user.is_bot or admin.user.is_deleted:
                        continue
                    text += f"[\u2063](tg://user?id={admin.user.id})"
                return await app.send_message(chat.id, text, reply_markup=keyboard)


@app.on_callback_query(filters.regex("manual_(.*)"))
async def manual(app, cb):
    chat = cb.message.chat
    from_user = cb.from_user
    permissions = await member_permissions(chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        if from_user.id not in SUDOERS:
            return await cb.answer(
                f"**تۆ ڕۆڵی پێویستت نییە ئەزیزم\nڕۆڵ : {permission}**",
                show_alert=True,
            )
    datas = cb.data.split("_", 2)
    dis = datas[1]
    id = datas[2]
    if dis == "approve":
        try:
            await app.approve_chat_join_request(chat_id=chat.id, user_id=id)
        except UserAlreadyParticipant:
            await cb.answer(
                "**ئەم بەکارهێنەرە وەرگیراوە پێشتر**",
                show_alert=True,
            )
            return await cb.message.delete()

    if dis == "decline":
        try:
            await app.decline_chat_join_request(chat_id=chat.id, user_id=id)
        except Exception as e:
            if "messages.HideChatJoinRequest" in str(e):
                await cb.answer(
                    "**ئەم بەکارهێنەرە وەرگیراوە**",
                    show_alert=True,
                )

    await approvaldb.update_one(
        {"chat_id": chat.id},
        {"$pull": {"pending_users": int(id)}},
    )
    return await cb.message.delete()


__MODULE__ = "Aᴘᴘʀᴏᴠᴇ"
__HELP__ = """
command: /autoapprove

Tʜɪs ᴍᴏᴅᴜʟᴇ ʜᴇʟᴘs ᴛᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴄᴄᴇᴘᴛ ᴄʜᴀᴛ ɪᴏɪɴ ʀᴇǫᴜᴇsᴛ sᴇɴᴅ ʙʏ ᴀ ᴜsᴇʀ ᴛʜʀᴏᴜɢʜ ɪɴᴠɪᴛᴀᴛɪᴏɴ ʟɪɴᴋ ᴏғ ʏᴏᴜʀ ɢʀᴏᴜᴘ

**Mᴏᴅᴇs:**
ᴡʜᴇɴ ʏᴏᴜ sᴇɴᴅ /autoapprove ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ʏᴏᴜ sᴇᴇ ᴛᴜʀɴ ᴏɴ ʙᴜᴛᴛᴏɴ ɪғ ᴀᴜᴛᴛᴏᴘʀᴏᴠᴇ ɴᴏᴛ ᴇɴᴀʙʟᴇᴅ ғᴏʀ ʏᴏᴜʀ ᴄʜᴀᴛ ɪғ ᴀʟʀᴇᴅʏ ᴛᴜʀɴᴇᴅ ᴏɴ ʏᴏᴜ ᴡɪʟʟ sᴇ ᴛᴡᴏ ᴍᴏᴅᴇs ᴛʜᴀᴛ's ᴀʀᴇ ʙᴇʟᴏᴡ ᴀɴᴅ ʜɪs ᴜsᴀsɢᴇ


¤ Automatic - ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴄᴄᴇᴘᴛs ᴄʜᴀᴛ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ.

¤ Manual - ᴀ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ sᴇɴᴅ ᴛᴏ ᴛʜᴇ ᴄʜᴀᴛ ʙʏ ᴛᴀɢɢɪɴɢ ᴛʜᴇ ᴀᴅᴍɪɴs. ᴛʜᴇ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴄᴄᴇᴘᴛ ᴏʀ ᴅᴇᴄʟɪɴᴇ ᴛʜᴇ ʀᴇǫᴜᴇsᴛs.

Usᴇ: /clearpending ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀʟʟ ᴘᴇɴᴅɪɴɢ ᴜsᴇʀ ɪᴅ ғʀᴏᴍ ᴅʙ. ᴛʜɪs ᴡɪʟʟ ᴀʟʟᴏᴡ ᴛʜᴇ ᴜsᴇʀ ᴛᴏ sᴇɴᴅ ʀᴇǫᴜᴇsᴛ ᴀɢᴀɪɴ.
"""
