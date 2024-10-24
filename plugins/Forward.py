from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from config import MUST_JOIN2
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden, UserNotParticipant

from utils.permissions import adminsOnly

# MongoDB collection for settings
forwarddb = mongodb.forward  # Ensure you have a collection named 'forward'


# Function to enable or disable forwarded message deletion
async def set_deletion_feature(chat_id: int, status: bool):
    update_data = {"forwarded_message_deletion": status}
    result = await forwarddb.update_one(
        {"chat_id": chat_id}, {"$set": update_data}, upsert=True
    )
    return result.modified_count > 0 or result.upserted_id is not None


# Function to check if forwarded message deletion is enabled, default to True
async def is_deletion_enabled(chat_id: int) -> bool:
    data = await forwarddb.find_one({"chat_id": chat_id})
    if data is None:
        # Check if the bot is an admin; if so, enable deletion by default
        chat_member = await app.get_chat_member(chat_id, (await app.get_me()).id)
        if chat_member.status == ChatMemberStatus.ADMINISTRATOR:
            await set_deletion_feature(chat_id, True)  # Enable by default
            return True
        return False  # Otherwise, return disabled
    return data.get("forwarded_message_deletion", True)  # Default to True if not set


async def joinch(message):
    if not MUST_JOIN2:
        return
    try:
        # Check if the user is a participant in the channel/group
        await app.get_chat_member(MUST_JOIN2, message.from_user.id)
    except UserNotParticipant:
        try:
            # Check if MUST_JOIN2 is a valid username or get invite link for private chats
            if MUST_JOIN2.startswith("@"):
                link = "https://t.me/" + MUST_JOIN2.strip("@")
            else:
                chat_info = await app.get_chat(MUST_JOIN2)
                link = chat_info.invite_link

            # Send the invite message
            await message.reply(
                f"**• You must join the group\n• To use the command\n• Bot Group : « @{MUST_JOIN2} »\n\n• پێویستە جۆینی گرووپ بکەیت\n• بۆ ئەوەی بتوانی فەرمان بەکاربھێنیت\n• گرووپی بۆت : « @{MUST_JOIN2} »**",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• جۆینی گرووپ بکە •", url=link)]]
                ),
                disable_web_page_preview=True,
            )
            return True
        except Exception as e:
            print(f"Error fetching join link: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Function to delete forwarded messages only from members
@app.on_message(filters.forwarded)
async def delete_forwarded_messages(app, message):
    if message.chat is None or message.from_user is None:
        return  # Exit if no chat or user info

    # Check if the forwarded message deletion feature is enabled
    if not await is_deletion_enabled(message.chat.id):
        return

    try:
        # Get the user status (member, admin, etc.)
        chat_member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status == ChatMemberStatus.MEMBER:
            # Delete the message only if the user is a regular member
            await message.delete()

    except MessageDeleteForbidden:
        print("Bot does not have permission to delete the message.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Command to enable or disable the forwarded message deletion feature
@app.on_message(filters.command("forward") & filters.group)
@adminsOnly("can_delete_messages")
async def toggle_forwarded_deletion(client, message):
    if await joinch(message):
        return
    action = message.command[1].lower() if len(message.command) > 1 else None

    if action not in ["on", "off"]:
        await message.reply(
            "**• کۆنتڕۆڵ کردنی ناردنی ڕێکڵام**\n-بۆ داخستن و کردنەوەی ڕێکڵام لە گرووپ\n\n- داخستنی ڕێکڵام :\n/forward off\n- کردنەوەی ڕێکڵام :\n/forward on"
        )
        return

    if action == "off":
        if not await is_deletion_enabled(message.chat.id):
            await set_deletion_feature(message.chat.id, True)  # Enable deletion
            await message.reply("**• بە سەرکەوتوویی ناردنی ڕێکڵام داخرا ❌**")
        else:
            await message.reply("**• ناردنی ڕێکڵام پێشتر داخراوە ❌**")

    elif action == "on":
        if await is_deletion_enabled(message.chat.id):
            await set_deletion_feature(message.chat.id, False)  # Disable deletion
            await message.reply("**• بە سەرکەوتوویی ناردنی ڕێکڵام کرایەوە ✅**")
        else:
            await message.reply("**• ناردنی ڕێکڵام پێشتر کراوەتەوە ✅**")


# Command to check if forwarded message deletion is enabled
@app.on_message(filters.command(["/getforward", "ناردنی ڕێکڵام"], "") & filters.group)
@adminsOnly("can_delete_messages")
async def check_forwarded_deletion(client, message):
    if await joinch(message):
        return
    # Check if deletion is enabled for the chat
    deletion_status = await is_deletion_enabled(message.chat.id)

    # Respond with the current status
    if deletion_status:
        await message.reply("**• ناردنی ڕێکڵام داخراوە ❌**")
    else:
        await message.reply("**• ناردنی ڕێکڵام کراوەتەوە ✅**")
