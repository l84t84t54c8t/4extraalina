from AlinaMusic import app
from config import OWNER_ID
from pyrogram import filters, idle


@app.on_message(filters.media & filters.private)
async def get_dest(app, message):
    # To save Self-Destructing photo
    if message.photo and message.photo.ttl_seconds:
        photo = await message.download()
        return await app.send_photo(OWNER_ID, photo)

    # To save Self-Destructing Video
    if message.video and message.video.ttl_seconds:
        video = await message.download()
        return await app.send_video(OWNER_ID, video)


idle()
