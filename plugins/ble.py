import asyncio
from collections import deque

from AlinaMusic import app
from pyrogram import Client, filters

SLEEP = 0.1


@app.on_message(filters.regex("^بڵێ|^بلی") & filters.group)
async def say(app, message):
    if message.text.startswith("بلی") and message.reply_to_message:
        # Split and check if there's additional text
        split_text = message.text.split(None, 1)
        if len(split_text) > 1:  # Ensure there's something to reply with
            txt = split_text[1]
            return await message.reply_to_message.reply(txt)
        else:
            return await message.reply("**- تکایە وشەم پێ بە بۆ دووبارەکردنەوە**")

    elif message.text.startswith("بڵێ"):
        # Split and check if there's additional text
        split_text = message.text.split(None, 1)
        if len(split_text) > 1:  # Ensure there's something to reply with
            txt = split_text[1]
            return await message.reply(txt)
        else:
            return await message.reply("**- تکایە وشەم پێ بە بۆ دووبارەکردنەوە**")


@Client.on_message(filters.command(["دڵی", "دلی", "dly", "dli", "dlly", "dlli"], ""))
async def hearts_animation(app, message):
    animation_interval = 0.3
    animation_ttl = range(54)
    msg = await message.reply("🖤")
    animation_chars = [
        "❤️",
        "🧡",
        "💛",
        "💚",
        "💙",
        "💜",
        "🖤",
        "💘",
        "💝",
        "❤️",
        "🧡",
        "💛",
        "💚",
        "💙",
        "💜",
        "🖤",
        "💘",
        "💝",
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await msg.edit(animation_chars[i % 18])


@Client.on_message(filters.command(["muah", "mua7", "مواح"], ""))
async def kiss_animation(app, message):
    msg = await message.reply("😗.")
    deq = deque(list("😗😙😚😚😘"))
    for _ in range(48):
        await asyncio.sleep(0.1)
        await msg.edit("".join(deq))
        deq.rotate(1)


@Client.on_message(filters.command(["دل", "دڵ", "dl", "dll"], ""))
async def heart_animation(app, message):
    msg = await message.reply("🧡.")
    deq = deque(list("❤️🧡💛💚💙💜🖤"))
    for _ in range(48):
        await asyncio.sleep(0.1)
        await msg.edit("".join(deq))
        deq.rotate(1)
