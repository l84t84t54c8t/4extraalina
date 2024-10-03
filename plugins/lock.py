from pyrogram import enums, filters
from pyrogram.types import ChatPermissions
from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb

# MongoDB collections
locksdb = mongodb.locks

# Fetch current chat permissions
async def get_current_permissions(client, chat_id):
    chat = await client.get_chat(chat_id)
    return chat.permissions

# Lock Command (Only admins or the owner can lock features)
@app.on_message(filters.command("lock") & filters.group)
async def lock_features(_, message):
    user_status = await app.get_chat_member(message.chat.id, message.from_user.id)
    
    if user_status.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        await message.reply_text("Only admins can lock features.")
        return

    # Command format: /lock <feature>
    if len(message.command) < 2:
        await message.reply_text("Please specify what you want to lock (e.g., /lock messages, /lock media, /lock forwarded, /lock all).")
        return

    feature_to_lock = message.command[1].lower()
    
    # Fetch current permissions
    current_permissions = await get_current_permissions(client, message.chat.id)

    # Create a permissions object to modify
    permissions = ChatPermissions(
        can_send_messages=current_permissions.can_send_messages,
        can_send_media_messages=current_permissions.can_send_media_messages,
        can_send_stickers=current_permissions.can_send_stickers,
        can_send_animations=current_permissions.can_send_animations,
        can_send_games=current_permissions.can_send_games,
        can_use_inline_bots=current_permissions.can_use_inline_bots,
        can_send_polls=current_permissions.can_send_polls,
        can_add_web_page_previews=current_permissions.can_add_web_page_previews,
        can_send_custom_emojis=current_permissions.can_send_custom_emojis,
        can_send_voice_notes=current_permissions.can_send_voice_notes,
        can_send_video_notes=current_permissions.can_send_video_notes,
    )

    # Lock the specified feature
    if feature_to_lock == "messages":
        permissions.can_send_messages = False
    elif feature_to_lock == "media":
        permissions.can_send_media_messages = False
    elif feature_to_lock == "stickers":
        permissions.can_send_stickers = False
    elif feature_to_lock == "gifs":
        permissions.can_send_animations = False
    elif feature_to_lock == "polls":
        permissions.can_send_polls = False
    elif feature_to_lock == "games":
        permissions.can_send_games = False
    elif feature_to_lock == "inline":
        permissions.can_use_inline_bots = False
    elif feature_to_lock == "web":
        permissions.can_add_web_page_previews = False
    elif feature_to_lock == "emoji":
        permissions.can_send_custom_emojis = False
    elif feature_to_lock == "voice":
        permissions.can_send_voice_notes = False
    elif feature_to_lock == "video_notes":
        permissions.can_send_video_notes = False
    elif feature_to_lock == "all":
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_stickers=False,
            can_send_animations=False,
            can_send_games=False,
            can_use_inline_bots=False,
            can_send_polls=False,
            can_add_web_page_previews=False,
            can_send_custom_emojis=False,
            can_send_voice_notes=False,
            can_send_video_notes=False
        )
    elif feature_to_lock == "forwarded":
        await lock_feature_db(message.chat.id, "forwarded")
        await message.reply_text("Locked forwarded messages successfully.")
        return
    else:
        await message.reply_text(f"Unknown lock feature: {feature_to_lock}. Available options: messages, media, stickers, gifs, polls, games, inline, web, emoji, voice, video_notes, forwarded, all.")
        return

    try:
        # Apply the new permissions to the group
        await app.set_chat_permissions(message.chat.id, permissions=permissions)
        await message.reply_text(f"Locked {feature_to_lock} successfully.")
    except Exception as e:
        await message.reply_text(f"Failed to lock {feature_to_lock}: {str(e)}")


# Unlock Command (Only admins or the owner can unlock features)
@app.on_message(filters.command("unlock") & filters.group)
async def unlock_features(_, message):
    user_status = await app.get_chat_member(message.chat.id, message.from_user.id)

    if user_status.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        await message.reply_text("Only admins can unlock features.")
        return

    # Command format: /unlock <feature>
    if len(message.command) < 2:
        await message.reply_text("Please specify what you want to unlock (e.g., /unlock messages, /unlock media, /unlock forwarded, /unlock all).")
        return

    feature_to_unlock = message.command[1].lower()
    
    # Fetch current permissions
    current_permissions = await get_current_permissions(client, message.chat.id)

    # Create a permissions object to modify
    permissions = ChatPermissions(
        can_send_messages=current_permissions.can_send_messages,
        can_send_media_messages=current_permissions.can_send_media_messages,
        can_send_stickers=current_permissions.can_send_stickers,
        can_send_animations=current_permissions.can_send_animations,
        can_send_games=current_permissions.can_send_games,
        can_use_inline_bots=current_permissions.can_use_inline_bots,
        can_send_polls=current_permissions.can_send_polls,
        can_add_web_page_previews=current_permissions.can_add_web_page_previews,
        can_send_custom_emojis=current_permissions.can_send_custom_emojis,
        can_send_voice_notes=current_permissions.can_send_voice_notes,
        can_send_video_notes=current_permissions.can_send_video_notes,
    )

    # Unlock the specified feature
    if feature_to_unlock == "messages":
        permissions.can_send_messages = True
    elif feature_to_unlock == "media":
        permissions.can_send_media_messages = True
    elif feature_to_unlock == "stickers":
        permissions.can_send_stickers = True
    elif feature_to_unlock == "gifs":
        permissions.can_send_animations = True
    elif feature_to_unlock == "polls":
        permissions.can_send_polls = True
    elif feature_to_unlock == "games":
        permissions.can_send_games = True
    elif feature_to_unlock == "inline":
        permissions.can_use_inline_bots = True
    elif feature_to_unlock == "web":
        permissions.can_add_web_page_previews = True
    elif feature_to_unlock == "emoji":
        permissions.can_send_custom_emojis = True
    elif feature_to_unlock == "voice":
        permissions.can_send_voice_notes = True
    elif feature_to_unlock == "video_notes":
        permissions.can_send_video_notes = True
    elif feature_to_unlock == "all":
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_stickers=True,
            can_send_animations=True,
            can_send_games=True,
            can_use_inline_bots=True,
            can_send_polls=True,
            can_add_web_page_previews=True,
            can_send_custom_emojis=True,
            can_send_voice_notes=True,
            can_send_video_notes=True
        )
    elif feature_to_unlock == "forwarded":
        await unlock_feature_db(message.chat.id, "forwarded")
        await message.reply_text("Unlocked forwarded messages successfully.")
        return
    else:
        await message.reply_text(f"Unknown unlock feature: {feature_to_unlock}. Available options: messages, media, stickers, gifs, polls, games, inline, web, emoji, voice, video_notes, forwarded, all.")
        return

    try:
        # Apply the new permissions to the group
        await app.set_chat_permissions(message.chat.id, permissions=permissions)
        await message.reply_text(f"Unlocked {feature_to_unlock} successfully.")
    except Exception as e:
        await message.reply_text(f"Failed to unlock {feature_to_unlock}: {str(e)}")



# Command to show lock status in the group
@app.on_message(filters.command("lockstatus") & filters.group)
async def lock_status(_, message):
    locked_features = await get_locked_features(message.chat.id)

    if not locked_features:
        await message.reply_text("No features are currently locked in this group.")
    else:
        await message.reply_text(f"Locked features: {', '.join(locked_features)}")


# Forwarded message handler (to enforce the lock on forwarded messages)
@app.on_message(filters.forwarded & filters.group)
async def forwarded_message_handler(_, message):
    # Check if forwarded messages are locked in this chat by querying MongoDB
    if await is_locked(message.chat.id, "forwarded"):
        try:
            await message.delete()
            await message.reply_text("Forwarded messages are locked in this group.")
        except Exception as e:
            await message.reply_text(f"Failed to delete forwarded message: {str(e)}")
