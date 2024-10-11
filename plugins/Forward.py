from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden, PeerIdInvalid, RPCError

# MongoDB collection for settings
forwarddb = mongodb.forward  # Ensure you have a collection named 'settings'

# Function to enable or disable forwarded message deletion
async def set_deletion_feature(chat_id: int, status: bool):
    update_data = {"forwarded_message_deletion": status}
    result = await forwarddb.update_one(
        {"chat_id": chat_id}, {"$set": update_data}, upsert=True
    )
    return result.modified_count > 0 or result.upserted_id is not None

# Function to check if forwarded message deletion is enabled
async def is_deletion_enabled(chat_id: int) -> bool:
    data = await forwarddb.find_one({"chat_id": chat_id})
    if not data:
        return False  # Default to disabled if no data exists
    return data.get("forwarded_message_deletion", True)  # Default to True if not set

@app.on_message(filters.forwarded)
async def gjgh(app, m):
    # Ensure m.chat and m.from_user are not None
    if m.chat is None or m.from_user is None:
        return  # Exit the function if they are None

    # Check if the forwarded message deletion feature is enabled
    if not await is_deletion_enabled(m.chat.id):
        return

    try:
        chat_member = await app.get_chat_member(m.chat.id, m.from_user.id)
        su = chat_member.status

        # Check if the user's status is "member"
        if su == ChatMemberStatus.MEMBER:
            await m.delete()

    except MessageDeleteForbidden:
        print("Bot does not have permission to delete the message.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to toggle the forwarded message deletion feature
@app.on_message(filters.command("forwarded") & filters.group)
@adminsOnly("can_delete_messages")
async def toggle_forwarded_deletion(app, message):
    if len(message.command) != 2:
        await message.reply("**• کۆنتڕۆڵ کردنی ناردنی ڕێکڵام**\n-بۆ داخستن و کردنەوەی ڕێکڵام لە گرووپ\n\n- داخستنی ڕێکڵام :\n/forward off\n- کردنەوەی ڕێکڵام :\n/forward on"
        )
        return

    status = message.command[1].lower()
    if status not in ["on", "off"]:
        await message.reply("**تکایە بنووسە 'on' یان 'off'**")
        return

    # Set the new status based on user input
    new_status = status == "on"
    await set_deletion_feature(message.chat.id, new_status)
    status_text = "enabled" if new_status else "disabled"
    await message.reply(f"Forwarded message deletion has been {status_text}.")
