from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden, PeerIdInvalid, RPCError

# MongoDB collection for settings
storydb = mongodb.story  # Ensure you have a collection named 'settings'


# Function to enable or disable story deletion
async def set_deletion_feature(chat_id: int, status: bool):
    update_data = {"story": status}
    result = await storydb.update_one(
        {"chat_id": chat_id}, {"$set": update_data}, upsert=True
    )
    return result.modified_count > 0 or result.upserted_id is not None


# Function to check if story deletion is enabled
async def is_deletion_enabled(chat_id: int) -> bool:
    data = await storydb.find_one({"chat_id": chat_id})
    if not data:
        return False  # Default to disabled if no data exists
    return data.get("story", False)  # Default to False if not set


# Command to enable or disable story deletion
@app.on_message(filters.command("story") & filters.group)
async def toggle_delete(client, message):
    chat_id = message.chat.id
    action = message.command[1].lower() if len(message.command) > 1 else None

    if action not in ["on", "off"]:
        await message.reply_text("**• کۆنتڕۆڵ کردنی ناردنی ستۆری**\n-بۆ داخستن و کردنەوەی ستۆری لە گرووپ\n- داخستنی ستۆری :/story off\n- کردنەوەی ستۆری : /story on")
        return

    if action == "on":
        if await is_deletion_enabled(chat_id):
            await message.reply_text("**• سڕینەوەی ستۆری پێشتر چالاککراوە ✅**")
        else:
            await set_deletion_feature(chat_id, True)
            await message.reply_text("**• بە سەرکەوتوویی سڕینەوەی ستۆری چالاککرا ✅**")
    
    elif action == "off":
        if not await is_deletion_enabled(chat_id):
            await message.reply_text("**• سڕینەوەی ستۆری پێشتر ناچالاککراوە ✅**")
        else:
            await set_deletion_feature(chat_id, False)
            await message.reply_text("**• بە سەرکەوتوویی سڕینەوەی ستۆری ناچالاککرا ✅**")


# Story Deletion
@app.on_message(filters.group)
async def delete_story(client, message):
    chat_id = message.chat.id

    # Check if story deletion is enabled
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
                print(f"Deleted story with ID: {message.story.id} from user: {message.from_user.id}")
            else:
                print(f"User {message.from_user.id} is an admin or owner. Story will not be deleted.")

        except (PeerIdInvalid, RPCError) as e:
            print(f"Failed to delete the story: {e}")
        except MessageDeleteForbidden:
            print("Bot does not have permission to delete the story.")
