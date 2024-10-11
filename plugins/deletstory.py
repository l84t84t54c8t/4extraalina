from AlinaMusic import app
from pyrogram import Client, filters
from pyrogram.errors import RPCError, PeerIdInvalid


@app.on_message(filters.forwarded & filters.group)
async def delete_forwarded_story(client, message):
    try:
        # Check if the forwarded message has a valid peer and is a story
        if message.forward_from and message.forward_from.is_story:
            try:
                # Try to delete the forwarded story
                await message.delete()
                print(f"Deleted forwarded story from user {message.forward_from.id} in chat {message.chat.id}")
                
                # Optionally notify the group
                await message.reply_text("⛔ Forwarded stories are not allowed and have been deleted.")
            
            except PeerIdInvalid:
                # Handle the case where the peer ID is invalid or the bot cannot resolve it
                print(f"Invalid Peer ID for forwarded story in chat {message.chat.id}. Cannot delete the message.")
                await message.reply_text("⚠️ The forwarded story could not be deleted due to an invalid peer ID.")
    
    except RPCError as e:
        print(f"Failed to delete message: {e}")
