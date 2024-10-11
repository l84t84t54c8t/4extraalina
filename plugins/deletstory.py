from AlinaMusic import app
from pyrogram import Client, filters
from pyrogram.errors import RPCError, PeerIdInvalid


@app.on_message(filters.group)
async def delete_story(client, message):
    # Check if the message contains a story
    if message.story:
        try:
            # Attempt to delete the story message
            await message.delete()
            await message.reply_text("⛔ Stories are not allowed and have been deleted.")
            print(f"Deleted story with ID: {message.story.id} from user: {message.story.from_user.id}")
        except (PeerIdInvalid, RPCError) as e:
            print(f"Failed to delete the story: {e}")
            await message.reply_text("⚠️ Error occurred while trying to delete the story.")
    else:
        print("No story found in the message.")
