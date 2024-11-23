import asyncio

from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import get_assistant
from pyrogram import Client, enums, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (CallbackQuery, ChatPermissions, ChatPrivileges,
                            InlineKeyboardButton, InlineKeyboardMarkup,
                            Message)


def get_keyboard(command):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("بەڵێ ✅", callback_data=f"{command}_yes"),
                InlineKeyboardButton("نەخێر ❌", callback_data=f"{command}_no"),
            ]
        ]
    )


@app.on_message(
    filters.command(
        ["purgeall", "سڕینەوەی نامەکان", "پاککردنەوەی گرووپ"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
)
async def banall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id

    AMBOTOK = await message.reply_text(
        f"**بەڕێز {message.from_user.mention}\nپشکنینی گرووپ بۆ سڕینەوەی نامەکان**"
    )
    await asyncio.sleep(2)
    bot = await app.get_chat_member(chat_id, app.me.id)
    if not (bot.privileges.can_delete_messages):
        await AMBOTOK.edit(
            f"**من ڕۆڵی پێویستم نییە بۆ ئەنجامدانی\n**"
            f"**پێویستی بە ڕۆڵی.\n**"
            f"**- سڕینەوەی نامە.\n**"
            f"**- دەرکردن و میوت کردن.\n**"
        )
        return
    await asyncio.sleep(5)
    await AMBOTOK.delete()
    confirm_msg = await message.reply(
        f"**بەڕێز {message.from_user.mention}\nدڵنیایی، دەتەوێ هەموو نامەکان بسڕمەوە ؟**",
        reply_markup=get_keyboard("deleteall"),
    )


@app.on_callback_query(filters.regex(r"^deleteall_(yes|no)$"))
async def handle_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer(
            "**تەنها خاوەنی گرووپ دەتوانێت ئەم کارە بکات.**", show_alert=True
        )
        return

    if callback_query.data == "deleteall_yes":
        await callback_query.answer(
            "**سڕینەوەی نامەکان دەستی پێکرد . .**", show_alert=True
        )
        await app.promote_chat_member(
            chat_id,
            assid,
            privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=True,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_promote_members=False,
            ),
        )

        try:
            async for msg in assistant.get_chat_history(chat_id):
                try:
                    await assistant.delete_messages(chat_id, msg.id)
                except Exception as e:
                    print(f"Failed to delete message {msg.id}: {e}")
                    continue
            await app.promote_chat_member(
                chat_id,
                assid,
                privileges=ChatPrivileges(
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                ),
            )
            await callback_query.answer(
                "**بە سەرکەوتوویی هەموو نامەکان سڕدرانەوە.**", show_alert=False
            )
        except Exception as e:
            await callback_query.answer(f"**هەڵە:\n{str(e)}**", show_alert=False)
    elif callback_query.data == "deleteall_no":
        await callback_query.message.edit("**سڕینەوەی نامەکان هەڵوەشێنرایەوە.**")


@app.on_message(
    filters.command(
        ["unmutell", "لادانی ئاگاداری گشتی", "لادانی میوتی گشتی"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
)
async def unmuteall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(
            f"**بەڕێز {message.from_user.mention}\n**تەنها خاوەنی گرووپ {owner_AMBOT} دەتوانێت بیکات.**"
        )
        return

    confirm_msg = await message.reply(
        f"**بەڕێز {message.from_user.mention}\nدڵنیایی، دەتەوێ میوتی هەموو ئەندامەکانی گرووپ لابدەیت ؟**",
        reply_markup=get_keyboard("unmuteall"),
    )


@app.on_callback_query(filters.regex(r"^unmuteall_(yes|no)$"))
async def handle_unmuteall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer(
            "Only the group owner can confirm this action.", show_alert=True
        )
        return
    if callback_query.data == "unmuteall_yes":
        await callback_query.message.edit("**لادانی میوتی هەموو ئەندامەکان ...**")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_restrict_members:
            await callback_query.message.edit("**ببورە من ڕۆڵی میوت و دەرکردنم نییە.**")
            return
        unmuted = 0
        async for member in app.get_chat_members(chat_id):
            if member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ]:
                continue
            try:
                await app.restrict_chat_member(
                    chat_id,
                    member.user.id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=False,
                        can_send_polls=False,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    ),
                )
                unmuted += 1
            except Exception as e:
                print(f"Failed to unmute {member.user.id}: {e}")
        await callback_query.message.edit(f"**بە سەرکەوتوویی {unmuted} میوتی لادرا.**")
    elif callback_query.data == "unmuteall_no":
        await callback_query.message.edit("**لادانی میوتی هەموو ئەندامەکان هەڵوەشێنرایەوە.**")


@app.on_message(
    filters.command(
        ["muteall", "ئاگاداری گشتی", "میوتی گشتی"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
)
async def muteall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(
            f"**بەڕێز {message.from_user.mention}\n**تەنها خاوەنی گرووپ {owner_AMBOT} دەتوانێت بیکات.**"
        )
        return
    confirm_msg = await message.reply(
        f"**بەڕێز {message.from_user.mention}\nدڵنیایی، دەتەوێ هەموو ئەندامەکانی گرووپ میوت بکەیت ؟**",
        reply_markup=get_keyboard("muteall"),
    )


@app.on_callback_query(filters.regex(r"^muteall_(yes|no)$"))
async def handle_muteall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer(
            "**تەنها خاوەنی گرووپ دەتوانێت ئەم کارە بکات.**", show_alert=True
        )
        return
    if callback_query.data == "muteall_yes":
        await callback_query.message.edit("**میوت کردنی هەموو ئەندامەکان ...**")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_restrict_members:
            await callback_query.message.edit("**ببورە من ڕۆڵی میوت و دەرکردنم نییە.**")
            return
        muted = 0
        async for member in app.get_chat_members(chat_id):
            if member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ]:
                continue
            try:
                await app.restrict_chat_member(
                    chat_id, member.user.id, ChatPermissions(can_send_messages=False)
                )
                muted += 1
            except Exception as e:
                print(f"Failed to mute {member.user.id}: {e}")
        await callback_query.message.edit(
            f"**بە سەرکەوتوویی {muted} ئەندام میوت کرا.**"
        )
    elif callback_query.data == "muteall_no":
        await callback_query.message.edit("**میوتی گشتی هەڵوەشێنرایەوە.**")


@app.on_message(filters.command("kickalllll"))
async def kickall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(
            f"Hey {message.from_user.mention}, 'kickall' can only be executed by the group owner {owner_AMBOT}."
        )
        return
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to kick all group members?",
        reply_markup=get_keyboard("kickall"),
    )


@app.on_callback_query(filters.regex(r"^kickall_(yes|no)$"))
async def handle_kickall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer(
            "Only the group owner can confirm this action.", show_alert=True
        )
        return
    if callback_query.data == "kickall_yes":
        await callback_query.message.edit("Kickall process started...")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_restrict_members:
            await callback_query.message.edit(
                "I don't have permission to kick members in this group."
            )
            return
        kicked = 0
        async for member in app.get_chat_members(chat_id):
            if (
                member.status in ["administrator", "creator"]
                or member.user.id == app.me.id
            ):
                continue
            try:
                await app.kick_chat_member(chat_id, member.user.id)
                kicked += 1
            except Exception as e:
                print(f"Failed to kick {member.user.id}: {e}")
        await callback_query.message.edit(f"Kicked {kicked} members successfully.")
    elif callback_query.data == "kickall_no":
        await callback_query.message.edit("Kickall process canceled.")


@app.on_message(filters.command("unpinalll"))
async def unpinall(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await message.reply_text(
            f"Hey {message.from_user.mention}, 'unpinall' can only be executed by the group owner {owner_AMBOT}."
        )
        return
    confirm_msg = await message.reply(
        f"{message.from_user.mention}, are you sure you want to unpin all messages?",
        reply_markup=get_keyboard("unpinall"),
    )


@app.on_callback_query(filters.regex(r"^unpinall_(yes|no)$"))
async def handle_unpinall_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    owner_id = None
    async for admin in client.get_chat_members(
        chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.status == enums.ChatMemberStatus.OWNER:
            owner_id = admin.user.id
            owner_AMBOT = admin.user.mention
    if user_id != owner_id and user_id not in SUDOERS:
        await callback_query.answer(
            "Only the group owner can confirm this action.", show_alert=True
        )
        return
    if callback_query.data == "unpinall_yes":
        await callback_query.message.edit("Unpinning process started...")
        bot = await app.get_chat_member(chat_id, app.me.id)
        if not bot.privileges.can_pin_messages:
            await callback_query.message.edit(
                "I don't have permission to unpin messages in this group."
            )
            return
        try:
            chat = await app.get_chat(chat_id)
            pinned_message = chat.pinned_message
            unpinned = 0
            if pinned_message:
                await app.unpin_chat_message(chat_id, pinned_message.message_id)
                unpinned += 1
                await callback_query.message.edit(
                    f"Unpinned {unpinned} message successfully."
                )
            else:
                await callback_query.message.edit("There are no messages to unpin.")
        except Exception as e:
            print(f"Failed to unpin message: {e}")
            await callback_query.message.edit(
                "An error occurred while trying to unpin the message."
            )
    elif callback_query.data == "unpinall_no":
        await callback_query.message.edit("Unpinning process canceled.")
