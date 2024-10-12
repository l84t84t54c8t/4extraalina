from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden, PeerIdInvalid, RPCError

from utils.permissions import adminsOnly

# MongoDB collection for settings
storydb = mongodb.story  # Ensure you have a collection named 'story'


# Function to enable or disable story deletion
async def set_deletion_feature(chat_id: int, status: bool):
    update_data = {"story": status}
    result = await storydb.update_one(
        {"chat_id": chat_id}, {"$set": update_data}, upsert=True
    )
    return result.modified_count > 0 or result.upserted_id is not None


# Function to check if story deletion is enabled, default to True
async def is_deletion_enabled(chat_id: int) -> bool:
    data = await storydb.find_one({"chat_id": chat_id})
    if data is None:
        # Check if the bot is an admin; if so, enable deletion by default
        chat_member = await app.get_chat_member(chat_id, (await app.get_me()).id)
        if chat_member.status == ChatMemberStatus.ADMINISTRATOR:
            await set_deletion_feature(chat_id, True)  # Enable by default
            return True
        return False  # Otherwise, return disabled
    return data.get("story", True)  # Default to True if not set


# Command to enable or disable story deletion
@app.on_message(filters.command("story")& filters.group)
@adminsOnly("can_delete_messages")
async def toggle_delete(client, message):
    chat_id = message.chat.id
    action = message.command[1].lower() if len(message.command) > 1 else None

    if action not in ["on", "off"]:
        await message.reply_text(
            "**• کۆنتڕۆڵ کردنی ناردنی ستۆری**\n-بۆ داخستن و کردنەوەی ستۆری لە گرووپ\n\n- داخستنی ستۆری :\n/story off\n- کردنەوەی ستۆری :\n/story on"
        )
        return

    if action == "off":
        if await is_deletion_enabled(chat_id):
            await set_deletion_feature(chat_id, False)  # Disable deletion
            await message.reply_text(
                "**• بە سەرکەوتوویی سڕینەوەی ستۆری ناچالاککرا ✅**"
            )
        else:
            await message.reply_text("**• سڕینەوەی ستۆری پێشتر ناچالاککراوە ✅**")

    elif action == "on":
        if not await is_deletion_enabled(chat_id):
            await set_deletion_feature(chat_id, True)  # Enable deletion
            await message.reply_text("**• بە سەرکەوتوویی سڕینەوەی ستۆری چالاککرا ✅**")
        else:
            await message.reply_text("**• سڕینەوەی ستۆری پێشتر چالاککراوە ✅**")


# Story Deletion
@app.on_message(filters.group)
async def delete_story(client, message):
    chat_id = message.chat.id
    # Check if story
    if not await is_deletion_enabled(chat_id):
        return

    # Ensure from_user exists before proceeding
    if message.from_user is None:
        return  # Exit if there's no user attached to the message

    # Check if the message contains a story
    if message.story:
        try:
            # Get the sender's chat member status
            member = await client.get_chat_member(message.chat.id, message.from_user.id)

            # Check if the user is a regular member (not admin or owner)
            if member.status == ChatMemberStatus.MEMBER:
                # Attempt to delete the story message
                await message.delete()

        except (PeerIdInvalid, RPCError) as e:
            print(f"Failed to delete the story: {e}")
        except MessageDeleteForbidden:
            print("Bot does not have permission to delete the story.")
