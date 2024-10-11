from AlinaMusic import app

from pyrogram import Client, filters
from pyrogram.errors import RPCError


@app.on_message(filters.forwarded & filters.group)
async def delete_forwarded_media(client, message):
    try:
        # Check if the forwarded message contains media (photo, video, etc.)
        if message.media:
            # Delete the forwarded media
            await message.delete()
            await message.reply_text("⛔ Forwarded media is not allowed and has been deleted.")
        else:
            print("No media found in the forwarded message.")

    except RPCError as e:
        print(f"Failed to delete media: {e}")
        await message.reply_text("⚠️ Error occurred while trying to delete the forwarded media.")
