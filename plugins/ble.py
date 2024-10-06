import asyncio
from collections import deque

from AlinaMusic import app
from pyrogram import filters
from pyrogram.errors import FloodWait

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


@app.on_message(filters.command(["دڵی", "دلی", "dly", "dli", "dlly", "dlli"], ""))
async def hearts_animation(app, message):
    try:
        animation_interval = 0.5  # Increased to reduce spamming
        animation_ttl = range(20)  # Reduced the number of iterations
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
            await msg.edit(animation_chars[i % len(animation_chars)])
    except FloodWait as e:
        await asyncio.sleep(e.value)  # Wait for the required time


@app.on_message(filters.command(["muah", "mua7", "مواح"], ""))
async def kiss_animation(app, message):
    try:
        msg = await message.reply("😗.")
        deq = deque(list("😗😙😚😚😘"))
        for _ in range(20):  # Reduced iterations
            await asyncio.sleep(0.3)  # Increased sleep interval
            await msg.edit("".join(deq))
            deq.rotate(1)
    except FloodWait as e:
        await asyncio.sleep(e.value)  # Wait for the required time


@app.on_message(filters.command(["دل", "دڵ", "dl", "dll"], ""))
async def heart_animation(app, message):
    try:
        msg = await message.reply("🧡.")
        deq = deque(list("❤️🧡💛💚💙💜🖤"))
        for _ in range(20):  # Reduced iterations
            await asyncio.sleep(0.3)  # Increased sleep interval
            await msg.edit("".join(deq))
            deq.rotate(1)
    except FloodWait as e:
        await asyncio.sleep(e.value)  # Wait for the required time
