import os
import time

from AlinaMusic import app
from pyrogram import filters
from pyrogram.types import Message

# Ensure these are correctly implemented
from utils.tools import convert_to_gif, runcmd

TEMP_DIR = "./temp/"


@app.on_message(filters.command("togif"))
async def sticker_to_gif(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply_text(
            "Reply to an animated/video sticker to convert it to a GIF."
        )

    progress_message = await message.reply_text("Converting sticker to GIF...")
    sticker = message.reply_to_message.sticker

    # Check sticker type
    if not (sticker.is_animated or sticker.is_video):
        return await progress_message.edit("Reply to an animated or video sticker.")

    try:
        dwl_path = await message.reply_to_message.download(file_name=TEMP_DIR)
        gif_path = await convert_to_gif(dwl_path, sticker.is_video)
        await message.reply_animation(gif_path)
        await progress_message.delete()
        os.remove(gif_path)
    except Exception as e:
        await progress_message.edit(f"An error occurred:\n`{str(e)}`")
    finally:
        if os.path.exists(dwl_path):
            os.remove(dwl_path)


@app.on_message(filters.command("tophoto"))
async def sticker_to_image(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply_text("Reply to a sticker to convert it to an image.")

    progress_message = await message.reply_text("Converting sticker to image...")
    try:
        dwl_path = await message.reply_to_message.download(
            file_name=f"{TEMP_DIR}image_{round(time.time())}.png"
        )
        await message.reply_photo(dwl_path)
        await progress_message.delete()
    except Exception as e:
        await progress_message.edit(f"An error occurred:\n`{str(e)}`")
    finally:
        if os.path.exists(dwl_path):
            os.remove(dwl_path)


@app.on_message(filters.command("tosticker"))
async def image_to_sticker(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("Reply to an image to convert it to a sticker.")

    progress_message = await message.reply_text("Converting image to sticker...")
    try:
        dwl_path = await message.reply_to_message.download(
            file_name=f"{TEMP_DIR}sticker_{round(time.time())}.webp"
        )
        await message.reply_sticker(dwl_path)
        await progress_message.delete()
    except Exception as e:
        await progress_message.edit(f"An error occurred:\n`{str(e)}`")
    finally:
        if os.path.exists(dwl_path):
            os.remove(dwl_path)


@app.on_message(filters.command("toimage"))
async def file_to_image(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("Reply to a file to convert it to an image.")

    if not message.reply_to_message.document.mime_type.startswith("image/"):
        return await message.reply_text("The file must be an image.")

    progress_message = await message.reply_text("Converting file to image...")
    try:
        dwl_path = await message.reply_to_message.download(
            file_name=f"{TEMP_DIR}image_{round(time.time())}.png"
        )
        await message.reply_photo(dwl_path)
        await progress_message.delete()
    except Exception as e:
        await progress_message.edit(f"An error occurred:\n`{str(e)}`")
    finally:
        if os.path.exists(dwl_path):
            os.remove(dwl_path)


@app.on_message(filters.command("tofile"))
async def image_to_file(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("Reply to an image to convert it to a file.")

    progress_message = await message.reply_text("Converting image to file...")
    try:
        dwl_path = await message.reply_to_message.download(
            file_name=f"{TEMP_DIR}file_{round(time.time())}.png"
        )
        await message.reply_document(dwl_path)
        await progress_message.delete()
    except Exception as e:
        await progress_message.edit(f"An error occurred:\n`{str(e)}`")
    finally:
        if os.path.exists(dwl_path):
            os.remove(dwl_path)


@app.on_message(filters.command("tovoice"))
async def media_to_voice(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply_text(
            "Reply to a media file to convert it to a voice note."
        )

    progress_message = await message.reply_text("Converting media to voice...")
    try:
        dwl_path = await message.reply_to_message.download(file_name=TEMP_DIR)
        voice_path = os.path.join(TEMP_DIR, f"voice_{round(time.time())}.ogg")
        cmd_list = [
            "ffmpeg",
            "-i",
            dwl_path,
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            voice_path,
        ]
        _, stderr, _, _ = await runcmd(" ".join(cmd_list))

        if os.path.exists(voice_path):
            await message.reply_voice(voice_path)
            await progress_message.delete()
            os.remove(voice_path)
        else:
            await progress_message.edit(f"Conversion failed:\n`{stderr}`")
    except Exception as e:
        await progress_message.edit(f"An error occurred:\n`{str(e)}`")
    finally:
        if os.path.exists(dwl_path):
            os.remove(dwl_path)


@app.on_message(filters.command("tomp3"))
async def media_to_mp3(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply_text(
            "Reply to a media message to convert it to MP3."
        )

    progress_message = await message.reply_text("Converting media to MP3...")
    try:
        dwl_path = await message.reply_to_message.download(file_name=TEMP_DIR)
        mp3_path = os.path.join(TEMP_DIR, f"audio_{round(time.time())}.mp3")
        cmd_list = ["ffmpeg", "-i", dwl_path, "-vn", mp3_path]
        _, stderr, _, _ = await runcmd(" ".join(cmd_list))

        if os.path.exists(mp3_path):
            await message.reply_audio(mp3_path, caption="Here is your MP3 file!")
            await progress_message.delete()
            os.remove(mp3_path)
        else:
            await progress_message.edit(f"Conversion failed:\n`{stderr}`")
    except Exception as e:
        await progress_message.edit(f"An error occurred:\n`{str(e)}`")
    finally:
        if os.path.exists(dwl_path):
            os.remove(dwl_path)
