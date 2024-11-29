import os
from AlinaMusic import app
from AlinaMusic.plugins.play.play import joinch
from config import OWNER_ID, OWNER_USERNAME
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
from pyrogram.types import (ChatPermissions, ChatPrivileges,
                            InlineKeyboardButton, InlineKeyboardMarkup)
from telegraph import upload_file

photosource = "https://graph.org/file/3202937ba2792dfa8722f.jpg"

alkl = []

# Check if the user has joined the channel
async def check_joined_channel(message):
    if await joinch(message):
        return True
    return False

@app.on_message(filters.command(["قفل الحمايه", "تعطيل الحمايه"], ""))
async def disable_protection(client, message):
    if await check_joined_channel(message):
        return
    group_id = message.chat.id
    user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
    
    if user_status.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or \
       message.from_user.id == OWNER_ID or \
       message.from_user.username in OWNER_USERNAME:
        if group_id in alkl:
            return await message.reply_text("الحماية معطلة مسبقًا✅")
        alkl.append(group_id)
        return await message.reply_text("تم تعطيل الحماية بنجاح✅🔒")
    else:
        return await message.reply_text(f"عذرًا {message.from_user.mention}, هذا الأمر لا يخصك✨♥")

@app.on_message(filters.command(["فتح الحمايه", "تفعيل الحمايه"], ""))
async def enable_protection(client, message):
    if await check_joined_channel(message):
        return
    group_id = message.chat.id
    user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
    
    if user_status.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or \
       message.from_user.id == OWNER_ID or \
       message.from_user.username in OWNER_USERNAME:
        if group_id not in alkl:
            return await message.reply_text("الحماية مفعلّة مسبقًا✅")
        alkl.remove(group_id)
        return await message.reply_text("تم فتح الحماية بنجاح✅🔓")
    else:
        return await message.reply_text(f"عذرًا {message.from_user.mention}, هذا الأمر لا يخصك✨♥")

# Helper function to create keyboard for protections
def create_protection_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("الـــحــمــايـــه ⚡", callback_data="jzhfjgh5")]
    ])

@app.on_message(filters.command(
    ["فتح الكل", "قفل الكل", "الحمايه", "قفل المنشن", "فتح المنشن", 
     "قفل الفديو", "فتح الفديو", "فتح الروابط", "قفل الروابط", 
     "قفل التوجيه", "فتح التوجيه", "قفل الملصقات", "فتح الملصقات", 
     "قفل الصور", "فتح الصور"], ""),
    group=71328934
)
async def show_protection_settings(client, message):
    if await check_joined_channel(message):
        return
    if message.chat.id in alkl:
        return await message.reply_text(f"عذرا {message.from_user.mention}, الأمر معطل من قبل مالك الجروب ✨✅")
    
    keyboard = create_protection_keyboard()
    chat_id = message.chat.id
    chat_name = message.chat.title
    chat_username = f"@{message.chat.username}" if message.chat.username else "لا يوجد"
    
    await message.reply_text(
        f"الإعدادات\n\n¦ لمجموعة: {chat_name}\n¦ ايدي المجموعة: {chat_id}\n¦ معرف المجموعة: {chat_username}\n\nاضغط على الحماية بالأسفل",
        reply_markup=keyboard
    )

# Callback handler for protection buttons
@app.on_callback_query(filters.regex("jzhfjgh5"))
async def protection_options(client, CallbackQuery):
    user_status = await client.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    
    if user_status.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await CallbackQuery.answer("يجب أن تكون إدمن للقيام بذلك!", show_alert=True)
    
    buttons = [
        [InlineKeyboardButton("قفل الصور ⚡", callback_data="stop_photo"),
         InlineKeyboardButton("فتح الصور ⚡", callback_data="photoun")],
        [InlineKeyboardButton("قفل الفديو ⚡", callback_data="stop_video"),
         InlineKeyboardButton("فتح الفديو ⚡", callback_data="viddelet")],
        [InlineKeyboardButton("قفل التوجيه ⚡", callback_data="stop_forward"),
         InlineKeyboardButton("فتح التوجيه ⚡", callback_data="frwdelet")],
        [InlineKeyboardButton("قفل الروابط ⚡", callback_data="stop_link"),
         InlineKeyboardButton("فتح الروابط ⚡", callback_data="rwadelet")],
        [InlineKeyboardButton("قفل المنشن ⚡", callback_data="stop_mention"),
         InlineKeyboardButton("فتح المنشن ⚡", callback_data="mendelet")],
        [InlineKeyboardButton("قفل الملصقات ⚡", callback_data="stop_sticker"),
         InlineKeyboardButton("فتح الملصقات ⚡", callback_data="moldelet")],
        [InlineKeyboardButton("قفل الكل ⚡", callback_data="stop_alkl"),
         InlineKeyboardButton("فتح الكل ⚡", callback_data="opn_alkl")]
    ]
    
    await CallbackQuery.edit_message_text(
        "الآن تحكم في أوامر الحماية بالأسفل 👇", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Further callback handlers for enabling and disabling protections can be simplified by using the above structure for each protection command.

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus

# Helper function to create the protection control buttons
def create_control_buttons(action_prefix, callback_suffix):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="بالكتم", callback_data=f"{action_prefix}_unmut{callback_suffix}"),
            InlineKeyboardButton(text="بالحظر", callback_data=f"{action_prefix}_unban{callback_suffix}"),
            InlineKeyboardButton(text="بمسح الرساله", callback_data=f"{action_prefix}_lock{callback_suffix}"),
            InlineKeyboardButton(text="رجوع", callback_data="jzhfjgh5"),
        ]
    ])

# Callback query handler for protection actions (قفل الحماية)
@app.on_callback_query(
    filters.regex(
        pattern=r"^(stop_photo|stop_video|stop_forward|stop_link|stop_mention|stop_sticker|stop_alkl)$"
    )
)
async def group_protection_handler(client: Client, CallbackQuery):
    a = await client.get_chat_member(CallbackQuery.message.chat.id, CallbackQuery.from_user.id)
    
    if a.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await CallbackQuery.answer("يجب أن تكون إدمن للقيام بذلك!", show_alert=True)

    command = CallbackQuery.matches[0].group(1)
    action_prefix = command.split('_')[1]  # Get the protection type like 'photo', 'video', etc.
    
    # Create buttons dynamically based on the protection type
    buttons = create_control_buttons(action_prefix, "1")
    
    await CallbackQuery.edit_message_text(
        "اختار القيود الآن ✨♥", reply_markup=buttons
    )

# Opening protections (فتح الحماية)
@app.on_callback_query(
    filters.regex(
        pattern=r"^(viddelet|photoun|frwdelet|rwadelet|mendelet|moldelet|opn_alkl)$"
    )
)
async def open_protection_handler(client: Client, CallbackQuery):
    a = await client.get_chat_member(CallbackQuery.message.chat.id, CallbackQuery.from_user.id)
    
    if a.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await CallbackQuery.answer("يجب أن تكون إدمن للقيام بذلك!", show_alert=True)

    command = CallbackQuery.matches[0].group(1)
    keybord = InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="jzhfjgh5")]])

    # Handle unlocking or enabling protections dynamically
    protection_list = {
        "photoun": photo_locked,
        "opn_alkl": [photo_locked, sticker_locked, video_locked, forward_locked, link_locked, mention_locked],
        "viddelet": video_locked,
        "frwdelet": forward_locked,
        "rwadelet": link_locked,
        "mendelet": mention_locked,
        "moldelet": sticker_locked,
    }

    try:
        # Remove the protection settings from the respective list
        if isinstance(protection_list[command], list):  # Multiple protections to be unlocked
            for protection in protection_list[command]:
                protection.remove(CallbackQuery.message.chat.id)
        else:
            protection_list[command].remove(CallbackQuery.message.chat.id)
        await CallbackQuery.edit_message_text(
            f"تم فتح {command} بنجاح ✨♥", reply_markup=keybord
        )
    except Exception as e:
        print(f"Error removing protection for {command}: {e}")
        await CallbackQuery.answer("حدث خطأ أثناء فتح الحماية!", show_alert=True)


from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus

# Helper function to handle adding chat IDs to protection lists
def add_to_protection_list(protection_list, chat_id, protection_type):
    if chat_id in protection_list:
        return f"{protection_type} مقفول بالفعل ✨♥"
    protection_list.append(chat_id)
    return f"تم قفل {protection_type} بنجاح ✨♥"

# Helper function to create the reply keyboard
def create_reply_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="jzhfjgh5")]])

# Main callback query handler for protection commands
@app.on_callback_query(
    filters.regex(
        pattern=r"^(photo_unmut1|photo_lock|photo_unban1|link_unmut1|link_lock|link_unban1|video_unmut1|video_lock|video_unban1|forward_unmut1|forward_lock|forward_unban1|sticker_unmut1|sticker_lock|sticker_unban1|mention_unmut1|mention_lock|mention_unban1|alkl_unmut1|alkl_lock|alkl_unban1)$"
    )
)
async def mearhjc(client: Client, CallbackQuery):
    a = await client.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    
    if a.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await CallbackQuery.answer(
            "يجب ان تكون ادمن للقيام بذلك!", show_alert=True
        )
    
    command = CallbackQuery.matches[0].group(1)
    chat_id = CallbackQuery.message.chat.id
    keybord = create_reply_keyboard()

    # Protection lists
    protection_lists = {
        "photo_mut": photo_mut,
        "video_mut": video_mut,
        "mention_mut": mention_mut,
        "forward_mut": forward_mut,
        "link_mut": link_mut,
        "sticker_mut": sticker_mut,
        
        "photo_ban": photo_ban,
        "video_ban": video_ban,
        "mention_ban": mention_ban,
        "forward_ban": forward_ban,
        "link_ban": link_ban,
        "sticker_ban": sticker_ban,
        
        "photo_locked": photo_locked,
        "video_locked": video_locked,
        "mention_locked": mention_locked,
        "forward_locked": forward_locked,
        "link_locked": link_locked,
        "sticker_locked": sticker_locked,
    }

    # Add chat_id to the corresponding protection list based on the command
    protection_type = command.split('_')[0]
    action_type = command.split('_')[1]

    # Handle "alkl" command which affects multiple protections
    if command == "alkl_unmut1":
        message = "تم قفل الكل بنجاح ✨♥"
        for protection in protection_lists.values():
            protection.append(chat_id)
        return await CallbackQuery.edit_message_text(message, reply_markup=keybord)
    
    if command == "alkl_unban1":
        message = "تم قفل الكل بنجاح ✨♥"
        for protection in protection_lists.values():
            protection.append(chat_id)
        return await CallbackQuery.edit_message_text(message, reply_markup=keybord)
    
    if command == "alkl_lock":
        message = "تم قفل الكل بنجاح ✨♥"
        for protection in protection_lists.values():
            protection.append(chat_id)
        return await CallbackQuery.edit_message_text(message, reply_markup=keybord)

    # Apply action to specific protection types
    if protection_type in protection_lists:
        protection_list = protection_lists[f"{protection_type}_{action_type}"]
        protection_type_name = protection_type.replace("_", " ")  # Make the name user-friendly
        response_message = add_to_protection_list(protection_list, chat_id, protection_type_name)
        return await CallbackQuery.edit_message_text(response_message, reply_markup=keybord)
    
    return await CallbackQuery.answer("حدث خطأ غير متوقع!", show_alert=True)


from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus

# Helper function to handle deletion and muting/locking/banning actions
async def handle_message(client, message, action_type, protection_list, action_message):
    if message.from_user.id == OWNER_ID or message.from_user.username in OWNER_USERNAME:
        return
    
    # Delete the message
    await message.delete()

    # Handle the protection lists
    group_id = message.chat.id
    user_id = message.from_user.id

    if group_id not in muted_users:
        muted_users[group_id] = []

    if user_id not in muted_users[group_id]:
        muted_users[group_id].append(user_id)
    else:
        print(action_message)

    # Handle ban or other action if applicable
    if action_type == "ban":
        try:
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            print(action_message)
        except Exception as e:
            print(f"Error banning: {e}")

# Handle photos
@app.on_message(
    filters.photo & filters.create(lambda _, __, message: message.chat.id in photo_mut)
)
async def handle_photo_mut(client, message):
    await handle_message(client, message, "mute", photo_mut, "صور")

@app.on_message(
    filters.photo & filters.create(lambda _, __, message: message.chat.id in photo_ban)
)
async def handle_photo_ban(client, message):
    await handle_message(client, message, "ban", photo_ban, "صور")

@app.on_message(
    filters.photo & filters.create(lambda _, __, message: message.chat.id in photo_locked)
)
async def handle_photo_locked(client, message):
    await handle_message(client, message, "lock", photo_locked, "صور")

# Handle videos
@app.on_message(
    filters.video & filters.create(lambda _, __, message: message.chat.id in video_mut)
)
async def handle_video_mut(client, message):
    await handle_message(client, message, "mute", video_mut, "فيديو")

@app.on_message(
    filters.video & filters.create(lambda _, __, message: message.chat.id in video_ban)
)
async def handle_video_ban(client, message):
    await handle_message(client, message, "ban", video_ban, "فيديو")

@app.on_message(
    filters.video & filters.create(lambda _, __, message: message.chat.id in video_locked)
)
async def handle_video_locked(client, message):
    await handle_message(client, message, "lock", video_locked, "فيديو")

# Handle forwarded messages
@app.on_message(
    filters.forwarded & filters.create(lambda _, __, message: message.chat.id in forward_mut)
)
async def handle_forward_mut(client, message):
    await handle_message(client, message, "mute", forward_mut, "توجيه")

@app.on_message(
    filters.forwarded & filters.create(lambda _, __, message: message.chat.id in forward_ban)
)
async def handle_forward_ban(client, message):
    await handle_message(client, message, "ban", forward_ban, "توجيه")

@app.on_message(
    filters.forwarded & filters.create(lambda _, __, message: message.chat.id in forward_locked)
)
async def handle_forward_locked(client, message):
    await handle_message(client, message, "lock", forward_locked, "توجيه")

# Handle stickers
@app.on_message(
    filters.sticker & filters.create(lambda _, __, message: message.chat.id in sticker_mut)
)
async def handle_sticker_mut(client, message):
    await handle_message(client, message, "mute", sticker_mut, "ملصق")

@app.on_message(
    filters.sticker & filters.create(lambda _, __, message: message.chat.id in sticker_ban)
)
async def handle_sticker_ban(client, message):
    await handle_message(client, message, "ban", sticker_ban, "ملصق")

@app.on_message(
    filters.sticker & filters.create(lambda _, __, message: message.chat.id in sticker_locked)
)
async def handle_sticker_locked(client, message):
    await handle_message(client, message, "lock", sticker_locked, "ملصق")

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from pyrogram.enums import ChatMemberStatus

# Helper function to mute, ban, or lock based on action type
async def handle_action(client, message, protection_list, action_type, action_message):
    if message.from_user.id == OWNER_ID or message.from_user.username in OWNER_USERNAME:
        return
    # Delete the message
    await message.delete()

    group_id = message.chat.id
    user_id = message.from_user.id
    if group_id not in muted_users:
        muted_users[group_id] = []

    if user_id not in muted_users[group_id]:
        muted_users[group_id].append(user_id)
    else:
        print(action_message)

    if action_type == "ban":
        try:
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            print(action_message)
        except Exception as e:
            print(f"Error banning: {e}")

# Function to handle mentions
async def handle_mentions(client, message, protection_list, action_type):
    if "@" in message.text:
        await handle_action(client, message, protection_list, action_type, "منشن")

# Function to handle links
async def handle_links(client, message, protection_list, action_type):
    if "https:" in message.text:
        await handle_action(client, message, protection_list, action_type, "رابط")

# Generalized handler for all media types (photo, video, sticker, etc.)
@app.on_message(filters.photo | filters.video | filters.sticker | filters.forwarded)
async def media_handler(client, message):
    # Handle each type of media based on muting, banning, or locking
    media_type_map = {
        "photo": {"muted": photo_mut, "banned": photo_ban, "locked": photo_locked},
        "video": {"muted": video_mut, "banned": video_ban, "locked": video_locked},
        "sticker": {"muted": sticker_mut, "banned": sticker_ban, "locked": sticker_locked},
        "forward": {"muted": forward_mut, "banned": forward_ban, "locked": forward_locked},
    }

    for media_type, action_dict in media_type_map.items():
        if isinstance(message, media_type):  # Check if message is of the current type
            group_id = message.chat.id
            if group_id in action_dict["muted"]:
                await handle_action(client, message, action_dict["muted"], "mute", media_type)
            elif group_id in action_dict["banned"]:
                await handle_action(client, message, action_dict["banned"], "ban", media_type)
            elif group_id in action_dict["locked"]:
                await handle_action(client, message, action_dict["locked"], "lock", media_type)
            return  # Stop processing once a relevant action is taken

# Function to set or unset chat permissions for lock/unlock commands
async def set_chat_permissions(client, message, lock_type, can_pin_messages, can_send_messages):
    group_id = message.chat.id
    chek = await client.get_chat_member(message.chat.id, message.from_user.id)

    if chek.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or message.from_user.id == OWNER_ID or message.from_user.username in OWNER_USERNAME:
        if group_id in mangof:
            return await message.reply_text(f"عذرا عزيزي [ {message.from_user.mention} ] الامر معطل من قبل مالك الجروب ✨✅")
        
        await client.set_chat_permissions(
            message.chat.id,
            ChatPermissions(can_pin_messages=can_pin_messages, can_send_messages=can_send_messages)
        )
        await message.reply_text(f"• تم {lock_type} التثبيت بواسطه ↤︎「 {message.from_user.mention}")
    else:
        return await message.reply_text(f"عزرا عزيزي{message.from_user.mention}\n هذا الامر يخص المالك والمشرفين فقط ✨♥")

# Lock and unlock chat functionality
@app.on_message(filters.command(["قفل الدردشه", "قفل الدردشة"], ""))
async def lock_chat(client, message):
    await set_chat_permissions(client, message, "قفل", can_pin_messages=False, can_send_messages=False)

@app.on_message(filters.command(["فتح الدردشه", "فتح الدردشة"], ""))
async def unlock_chat(client, message):
    await set_chat_permissions(client, message, "فتح", can_pin_messages=True, can_send_messages=True)

# Pinning lock and unlock functionality
@app.on_message(filters.command("قفل التثبيت", ""))
async def lock_pin(client, message):
    await set_chat_permissions(client, message, "قفل", can_pin_messages=False, can_send_messages=True)

@app.on_message(filters.command("فتح التثبيت", ""))
async def unlock_pin(client, message):
    await set_chat_permissions(client, message, "فتح", can_pin_messages=True, can_send_messages=True)

# Handle mentions in the chat
@app.on_message(group=676531)
async def delet_mention_mut(client, message):
    await handle_mentions(client, message, mention_mut, "mute")

@app.on_message(group=67653167)
async def delet_mention_ban(client, message):
    await handle_mentions(client, message, mention_ban, "ban")

@app.on_message(group=676531548)
async def delet_mention_locked(client, message):
    await handle_mentions(client, message, mention_locked, "lock")

# Handle links in the chat
@app.on_message(group=54534)
async def delet_link_mut(client, message):
    await handle_links(client, message, link_mut, "mute")

@app.on_message(group=5453454)
async def delet_link_ban(client, message):
    await handle_links(client, message, link_ban, "ban")

@app.on_message(group=5453464245)
async def delet_link_locked(client, message):
    await handle_links(client, message, link_locked, "lock")


from pyrogram.types import ChatPermissions
from pyrogram.enums import ChatMemberStatus

# Helper function to check if the user is authorized
async def is_authorized(client, message):
    chek = await client.get_chat_member(message.chat.id, message.from_user.id)
    return (
        chek.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or message.from_user.id == OWNER_ID
        or message.from_user.username in OWNER_USERNAME
    )

# Helper function to set chat permissions
async def set_chat_permissions(client, message, can_invite_users, can_send_media_messages, can_send_messages):
    group_id = message.chat.id
    if group_id in mangof:
        return await message.reply_text(
            f"عذرا عزيزي [ {message.from_user.mention} ] الامر معطل من قبل مالك الجروب ✨✅"
        )
    await client.set_chat_permissions(
        message.chat.id,
        ChatPermissions(
            can_invite_users=can_invite_users,
            can_send_media_messages=can_send_media_messages,
            can_send_messages=can_send_messages,
        ),
    )

# Helper function to mute, ban, or lock based on the action type
async def handle_action(client, message, protection_list, action_type, action_message):
    if message.from_user.id == OWNER_ID or message.from_user.username in OWNER_USERNAME:
        return
    await message.delete()

    group_id = message.chat.id
    user_id = message.from_user.id
    if group_id not in muted_users:
        muted_users[group_id] = []

    if user_id not in muted_users[group_id]:
        muted_users[group_id].append(user_id)
    else:
        print(action_message)

    if action_type == "ban":
        try:
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            print(action_message)
        except Exception as e:
            print(f"Error banning: {e}")

# Handle lock/unlock commands with permissions
@app.on_message(filters.command("قفل الدعوة", ""))
async def lock_invites(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        await set_chat_permissions(client, message, False, True, True)
        await message.reply_text(f"• تم قفل الدعوة بواسطه ↤︎「 {message.from_user.mention}」")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر يخص المالك والمشرفين فقط ✨♥")

@app.on_message(filters.command("فتح الدعوة", ""))
async def unlock_invites(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        await set_chat_permissions(client, message, True, True, True)
        await message.reply_text(f"• تم فتح الدعوة بواسطه ↤︎「 {message.from_user.mention}」")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر يخص المالك والمشرفين فقط ✨♥")

# Handle lock/unlock for media
@app.on_message(filters.command("قفل الميديا", ""))
async def lock_media(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        await set_chat_permissions(client, message, True, False, True)
        await message.reply_text("تم قفل الميديا")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر يخص المالك والمشرفين فقط ✨♥")

@app.on_message(filters.command("فتح الميديا", ""))
async def unlock_media(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        await set_chat_permissions(client, message, True, True, True)
        await message.reply_text("تم فتح الميديا")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر يخص المالك والمشرفين فقط ✨♥")

# Handle lock/unlock for animated messages
@app.on_message(filters.command("قفل المتحركات", ""))
async def lock_animated(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        await set_chat_permissions(client, message, False, True, True)
        await message.reply_text("تم قفل المتحركات")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر يخص المالك والمشرفين فقط ✨♥")

@app.on_message(filters.command("فتح المتحركات", ""))
async def unlock_animated(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        await set_chat_permissions(client, message, True, True, True)
        await message.reply_text("تم فتح المتحركات")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر يخص المالك والمشرفين فقط ✨♥")

# Handle lock/unlock for swearing
saap_locked = []

@app.on_message(filters.command(["قفل السب"], "") & filters.group, group=573555665565)
async def lock_swearing(client, message):
    if await is_authorized(client, message):
        if message.chat.id in saap_locked:
            return await message.reply_text("السب مقفول بالفعل ✨♥")
        saap_locked.append(message.chat.id)
        return await message.reply_text("تم قفل السب بنجاح ✨♥")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر لا يخصك✨♥")

@app.on_message(filters.command(["فتح السب"], "") & filters.group, group=57355566556)
async def unlock_swearing(client, message):
    if await is_authorized(client, message):
        if message.chat.id not in saap_locked:
            return await message.reply_text("السب مفتوح بالفعل ✨♥")
        saap_locked.remove(message.chat.id)
        return await message.reply_text("تم فتح السب بنجاح ✨♥")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention}\n هذا الامر لا يخصك✨♥")

# Handle swearing words
@app.on_message(group=5735545566)
async def delete_swearing(client, message):
    if not message.chat.id in saap_locked:
        return
    if message.from_user.id == OWNER_ID or message.from_user.username in OWNER_USERNAME:
        return
    swear_words = ["احا", "خخخ", "كسك", "كسمك", "عرص", "خول", "يبن", "كلب", "علق", "كسم", "انيك", "انيكك", "اركبك", "زبي"]
    for word in swear_words:
        if word in message.text:
            await message.delete()
            await message.reply_text(
                f"• عذراً عزيزي ↤︎「 {message.from_user.mention}  」\n • تم قفل ارسال السب هنا ."
            )
            return


from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus


# Helper function to check if a user is authorized (admin, owner, or bot owner)
async def is_authorized(client, message):
    chek = await client.get_chat_member(message.chat.id, message.from_user.id)
    return (
        chek.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or message.from_user.id == OWNER_ID
        or message.from_user.username in OWNER_USERNAME
    )


# Helper function to handle user role titles based on their status
async def get_user_title(client, message, user_id=None):
    user_id = user_id or message.from_user.id
    chat_id = message.chat.id
    user = await client.get_chat_member(chat_id, user_id)
    if user.status == ChatMemberStatus.OWNER:
        return "مالك الجروب"
    elif user.status == ChatMemberStatus.MEMBER:
        return "عضو حقير"
    elif user.status == ChatMemberStatus.ADMINISTRATOR:
        title = user.custom_title if user.custom_title else "مشرف"
        return title
    return None


@app.on_message(filters.command(["لقبي"], ""))
async def tit5le(client, message):
    if await joinch(message):
        return
    title = await get_user_title(client, message)
    if title:
        await message.reply_text(title)


@app.on_message(filters.command(["لقبه"], ""), group=6465)
async def title(client, message):
    if await joinch(message):
        return
    title = await get_user_title(client, message, message.reply_to_message.from_user.id)
    if title:
        await message.reply_text(title)


# Command to check user privileges
@app.on_message(filters.command(["صلاحياتي"], ""))
async def caesarprivileges(client, message):
    if await joinch(message):
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    cae = await client.get_chat_member(chat_id, user_id)
    if cae.status == ChatMemberStatus.OWNER:
        await message.reply_text("أنت مالك الجروب")
    elif cae.status == ChatMemberStatus.MEMBER:
        await message.reply_text("أنت عضو حقير")
    else:
        privileges = cae.privileges if cae else None
        privileges_list = {
            "ترقية الأعضاء": privileges.can_promote_members,
            "إدارة الدردشات الصوتية": privileges.can_manage_video_chats,
            "تثبيت الرسائل": privileges.can_pin_messages,
            "دعوة المستخدمين": privileges.can_invite_users,
            "تقييد الأعضاء": privileges.can_restrict_members,
            "حذف الرسائل": privileges.can_delete_messages,
            "تغيير معلومات الجروب": privileges.can_change_info,
        }
        
        # Format privileges
        privilege_text = "\n".join([f"{key}: {'✅' if value else '❌'}" for key, value in privileges_list.items()])
        await message.reply_text(f"صلاحياتك في الجروب:\n\n{privilege_text}")


# Command to show user rank
@app.on_message(filters.command(["رتبتي"], ""))
async def rotpty(client, message):
    if await joinch(message):
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    cae = await client.get_chat_member(chat_id, user_id)
    if message.from_user.username in OWNER_USERNAME:
        await message.reply_text("**مطور السورس شخصيا 🫡♥**")
    elif message.from_user.id == OWNER_ID:
        await message.reply_text("**انت مطوري روح قلبي 🥹♥**")
    elif cae.status == ChatMemberStatus.OWNER:
        await message.reply_text("**أنت مالك الخرابه 😂♥**")
    elif cae.status == ChatMemberStatus.MEMBER:
        await message.reply_text("**انت مجرد عضو 🙂**")
    else:
        await message.reply_text(f"**انت مشرف في الجروب 🌚♥**")


# Handle mute/unmute permissions
unmute_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)

mute_permission = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_send_polls=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_pin_messages=False,
    can_invite_users=True,
)

muttof = []


from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
import os
from telegraph import upload_file

# Helper function to check if user is authorized
async def is_authorized(client, message):
    chek = await client.get_chat_member(message.chat.id, message.from_user.id)
    return (
        chek.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or message.from_user.id == OWNER_ID
        or message.from_user.username in OWNER_USERNAME
    )

# Helper function to set chat permissions (lock/unlock)
async def set_chat_permissions(client, message, can_invite_users, can_send_media_messages, can_send_messages):
    if message.chat.id in mangof:
        return await message.reply_text(f"عذرا عزيزي [ {message.from_user.mention} ] الامر معطل من قبل مالك الجروب ✨✅")
    await client.set_chat_permissions(
        message.chat.id,
        ChatPermissions(
            can_invite_users=can_invite_users,
            can_send_media_messages=can_send_media_messages,
            can_send_messages=can_send_messages,
        ),
    )

# General lock/unlock handler for restrictions
async def lock_unlock_handler(client, message, action_type, protection_list, action_message, success_msg):
    if await is_authorized(client, message):
        if action_type == "lock":
            protection_list.append(message.chat.id)
            await message.reply_text(success_msg)
        elif action_type == "unlock":
            if message.chat.id in protection_list:
                protection_list.remove(message.chat.id)
                await message.reply_text(success_msg)
            else:
                await message.reply_text("الامر مفعل بالفعل ✅")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention} هذا الامر لا يخصك✨♥")

# Handle mute/unmute for specific commands
@app.on_message(filters.command(["قفل التقييد", "تعطيل التقييد"], ""))
async def muttlock(client, message):
    await lock_unlock_handler(client, message, "lock", muttof, "تم تعطيل التقييد بنجاح ✅🔒", "تم معطل من قبل🔒")

@app.on_message(filters.command(["فتح التقييد", "تفعيل التقييد"], ""))
async def muttopen(client, message):
    await lock_unlock_handler(client, message, "unlock", muttof, "تم فتح التقييد بنجاح ✅🔓", "التقييد مفعل من قبل ✅")

@app.on_message(filters.command(["الغاء تقييد", "الغاء التقييد"], ""))
async def mu54te(client, message):
    if await joinch(message):
        return
    group_id = message.chat.id
    chek = await client.get_chat_member(message.chat.id, message.from_user.id)
    if await is_authorized(client, message):
        if message.chat.id not in muttof:
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.reply_to_message.from_user.id,
                permissions=unmute_permissions,
            )
            await message.reply_text(f"✅ ¦ تـم الغاء التقييد بـنجـاح\n {message.reply_to_message.from_user.mention} ")
    else:
        await message.reply_text(f"عزرا عزيزي {message.from_user.mention} هذا الامر لا يخصك✨♥")

# Handle muting a user (with check for ownership)
@app.on_message(filters.command(["تقييد"], ""))
async def m6765ute(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        if message.chat.id in muttof:
            return
        if message.reply_to_message.from_user.username in OWNER_USERNAME:
            await message.reply_text("• عذرآ لا تستطيع استخدام الأمر على مطور السورس")
        else:
            mute_permission = ChatPermissions(can_send_messages=False)
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.reply_to_message.from_user.id,
                permissions=mute_permission,
            )
            await message.reply_text(f"✅ ¦ تـم التقييد بـنجـاح\n {message.reply_to_message.from_user.mention} ")

# Handle clearing muted users
@app.on_message(filters.command(["مسح المقيدين"], ""))
async def unm54ute(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        global restricted_users
        count = len(restricted_users)
        for user in restricted_users:
            await client.restrict_chat_member(
                chat_id=message.chat.id, user_id=user, permissions=unmute_permissions
            )
            restricted_users.remove(user)
        await message.reply_text(f"↢ تم مسح {count} من المقيدين")

# Get list of restricted users
@app.on_message(filters.command(["المقيدين"], ""))
async def get_restr_users(client, message):
    if await joinch(message):
        return
    if await is_authorized(client, message):
        global restricted_users
        count = len(restricted_users)
        user_ids = [str(user.id) for user in restricted_users]
        response = f"⌔ قائمة المقيدين وعددهم : {count}\n"
        response += "⋖⊶◎⊷⌯𝚂𝙾𝚄𝚁𝙲𝙴 𝙲𝙰𝙴𝚂𝙰𝚁⌯⊶◎⊷⋗\n"
        response += "\n".join(user_ids)
        await message.reply_text(response)

# Handle banning and enabling/disabling ban & kick
gaaof = []
@app.on_message(filters.command(["تعطيل الحظر", "تعطيل الطرد"], ""))
async def gaalock(client, message):
    await lock_unlock_handler(client, message, "lock", gaaof, "تم تعطيل الطرد و الحظر بنجاح ✅🔒", "تم معطل من قبل🔒")

@app.on_message(filters.command(["فتح الطرد", "تفعيل الطرد", "تفعيل الحظر"], ""))
async def gaaopen(client, message):
    await lock_unlock_handler(client, message, "unlock", gaaof, "تم فتح الطرد و الحظر بنجاح ✅🔓", "الطرد و الحظر مفعل من قبل ✅")

# Handle media files for Telegraph
@app.on_message(
    filters.command(["تليجراف", "/telegraph", "/tm", "/tgm"], ""), group=973
)
async def telegraph(client, message):
    if await joinch(message):
        return
    replied = message.reply_to_message
    if not replied:
        return await message.reply("الرد على ملف وسائط مدعوم ")
    
    # Validate media type
    if not (
        (replied.photo and replied.photo.file_size <= 5242880)
        or (replied.animation and replied.animation.file_size <= 55242880)
        or (
            replied.video
            and replied.video.file_name.endswith(".mp4")
            and replied.video.file_size <= 55242880
        )
        or (
            replied.document
            and replied.document.file_name.endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".mp4")
            )
            and replied.document.file_size <= 55242880
        )
    ):
        return await message.reply("غير مدعوم !")
    
    # Download and upload to Telegraph
    download_location = await client.download_media(
        message=message.reply_to_message, file_name="root/downloads/"
    )
    try:
        response = upload_file(download_location)
    except Exception as document:
        await message.reply(message, text=document)
    else:
        button_s = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "فتح الرابط 🔗", url=f"https://telegra.ph{response[0]}"
                    )
                ]
            ]
        )
        await message.reply(
            f"**الرابط »**\n`https://telegra.ph{response[0]}`",
            disable_web_page_preview=True,
            reply_markup=button_s,
        )
    finally:
        os.remove(download_location)
