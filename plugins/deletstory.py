from AlinaMusic.core.mongo import mongodb
from AlinaMusic import app
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError, PeerIdInvalid

# Database collection for settings
storydb = mongodb.story  # Ensure you have a collection named 'story' in your MongoDB

# Function to enable story deletion
async def set_story_deletion_on(chat_id: int) -> bool:
    result = await storydb.update_one(
        {"chat_id": chat_id}, {"$set": {"delete_story": True}}, upsert=True
    )
    return result.modified_count > 0 or result.upserted_id is not None

# Function to disable story deletion
async def set_story_deletion_off(chat_id: int) -> bool:
    result = await storydb.update_one(
        {"chat_id": chat_id}, {"$set": {"delete_story": False}}, upsert=True
    )
    return result.modified_count > 0

# Function to check if story deletion is enabled
async def is_story_deletion_on(chat_id: int) -> bool:
    data = await storydb.find_one({"chat_id": chat_id})
    if not data:
        return True  # Default to enabled if not found
    return data.get("delete_story", True)  # Default to True if not set

@app.on_message(filters.command("toggle_delete") & filters.group)
async def toggle_delete(client, message):
    chat_id = message.chat.id
    is_enabled = await is_story_deletion_on(chat_id)
    
    if is_enabled:
        await set_story_deletion_off(chat_id)
        await message.reply_text("Story deletion is now **disabled**.")
    else:
        await set_story_deletion_on(chat_id)
        await message.reply_text("Story deletion is now **enabled**.")

@app.on_message(filters.group)
async def delete_story(client, message):
    # Check the current status of the story deletion feature
    chat_id = message.chat.id
    if not await is_story_deletion_on(chat_id):
        return  # Exit if deletion is disabled

    # Check if the message contains a story
    if message.story:
        try:
            # Get the sender's chat member status
            member = await client.get_chat_member(message.chat.id, message.from_user.id)

            # Check if the user is a regular member (not admin or owner)
            if member.status == ChatMemberStatus.MEMBER:
                # Attempt to delete the story message
                await message.delete()
                await message.reply_text("**• ببوورە ئەزیزم ناردنی ستۆری قەدەغەکراوە ⛔**")
                print(f"Deleted story with ID: {message.story.id} from user: {message.from_user.id}")
            else:
                print(f"User {message.from_user.id} is an admin or owner. Story will not be deleted.")
                
        except (PeerIdInvalid, RPCError) as e:
            print(f"Failed to delete the story: {e}")
            await message.reply_text("⚠️ Error occurred while trying to delete the story.")
    else:
        print("No story found in the message.")
