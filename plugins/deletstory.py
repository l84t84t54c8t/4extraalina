from AlinaMusic import app
from pyrogram import Client, filters
from pyrogram.errors import RPCError


@app.on_message(filters.forwarded & filters.group)
async def delete_forwarded_story(client, message):
    try:
        # Check if the forwarded message is a story
        if message.forward_from and message.forward_from.is_story:
            # Log the deletion action
            print(f"Deleting forwarded story from user {message.forward_from.id} in chat {message.chat.id}")
            
            # Delete the forwarded message (story)
            await message.delete()
            
            # Optionally send a message to the group explaining why it was deleted
            await message.reply_text("⛔ Forwarded stories are not allowed in this group and have been deleted.")
    
    except RPCError as e:
        print(f"Failed to delete message: {e}")
