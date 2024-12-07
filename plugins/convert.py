import os
import time
from pyrogram import filters, Client
from pyrogram.types import Message
from utils.tools import convert_to_gif, runcmd

TEMP_DIR = "./temp/"

from AlinaMusic import app


@app.on_message(filters.command("stog"))
async def sticker_to_gif(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await hellbot.delete(
            message, "Reply to an animated/video sticker to convert it to gif."
        )

    hell = await hellbot.edit(message, "Converting ...")

    replied_sticker = message.reply_to_message.sticker

    if replied_sticker.is_animated:
        is_video = False
    elif replied_sticker.is_video:
        is_video = True
    else:
        return await hellbot.delete(hell, "Reply to an animated/video sticker.")

    dwl_path = await message.reply_to_message.download(Config.TEMP_DIR)
    gif_path = await convert_to_gif(dwl_path, is_video)

    await message.reply_animation(gif_path)
    await hellbot.delete(hell, "Converted to gif successfully!")

    os.remove(dwl_path)
    os.remove(gif_path)


@app.on_message(filters.command("stoi"))
async def sticker_to_image(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await hellbot.delete(
            message, "Reply to an sticker to convert it to image."
        )

    hell = await hellbot.edit(message, "Converting ...")
    fileName = f"image_{round(time.time())}.png"
    dwl_path = await message.reply_to_message.download(f"{Config.TEMP_DIR}{fileName}")

    await message.reply_photo(dwl_path)
    await hellbot.delete(hell, "Converted to image successfully!")

    os.remove(dwl_path)


@app.on_message(filters.command("itos"))
async def image_to_sticker(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await hellbot.delete(
            message, "Reply to an image to convert it to sticker."
        )

    hell = await hellbot.edit(message, "Converting ...")
    fileName = f"sticker_{round(time.time())}.webp"
    dwl_path = await message.reply_to_message.download(f"{Config.TEMP_DIR}{fileName}")

    await message.reply_sticker(dwl_path)
    await hellbot.delete(hell, "Converted to sticker successfully!")

    os.remove(dwl_path)


@app.on_message(filters.command("ftoi"))
async def file_to_image(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await hellbot.delete(message, "Reply to a file to convert it to image.")

    if message.reply_to_message.document.mime_type.split("/")[0] != "image":
        return await hellbot.delete(message, "Reply to an image file.")

    hell = await hellbot.edit(message, "Converting ...")
    fileName = f"image_{round(time.time())}.png"
    dwl_path = await message.reply_to_message.download(f"{Config.TEMP_DIR}{fileName}")

    await message.reply_photo(dwl_path)
    await hellbot.delete(hell, "Converted to image successfully!")

    os.remove(dwl_path)


@on_message("itof", allow_stan=True)
async def image_to_file(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await hellbot.delete(message, "Reply to an image to convert it to file.")

    hell = await hellbot.edit(message, "Converting ...")
    fileName = f"file_{round(time.time())}.png"
    dwl_path = await message.reply_to_message.download(f"{Config.TEMP_DIR}{fileName}")

    await message.reply_document(dwl_path)
    await hellbot.delete(hell, "Converted to file successfully!")

    os.remove(dwl_path)


@app.on_message(filters.command("tovoice"))
async def media_to_voice(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await hellbot.delete(message, "Reply to a media to convert it to voice.")
    hell = await hellbot.edit(message, "Converting ...")
    dwl_path = await message.reply_to_message.download(f"{Config.TEMP_DIR}")
    voice_path = f"{round(time.time())}.ogg"

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

    _, err, _, _ = await runcmd(" ".join(cmd_list))

    if os.path.exists(voice_path):
        await message.reply_voice(voice_path)
        await hellbot.delete(hell, "Converted to voice successfully!")
        os.remove(voice_path)
    else:
        await hellbot.error(hell, f"`{err}`")

    os.remove(dwl_path)


@app.on_message(filters.command(("tomp3"))
async def media_to_mp3(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await hellbot.delete(message, "Reply to a media to convert it to mp3.")

    hell = await hellbot.edit(message, "Converting ...")
    dwl_path = await message.reply_to_message.download(f"{Config.TEMP_DIR}")
    mp3_path = f"{round(time.time())}.mp3"

    cmd_list = [
        "ffmpeg",
        "-i",
        dwl_path,
        "-vn",
        mp3_path,
    ]

    _, stderr, _, _ = await runcmd(" ".join(cmd_list))

    if os.path.exists(mp3_path):
        await message.reply_audio(mp3_path)
        await hellbot.delete(hell, "Converted to mp3 successfully!")
        os.remove(mp3_path)
    else:
        await hellbot.error(hell, f"`{stderr}`")

    os.remove(dwl_path)
