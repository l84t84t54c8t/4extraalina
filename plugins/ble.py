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


@app.on_message(filters.command(["دلی", "دڵی", "dli", "dlly"], "") & filters.group)
async def heart_animation(app, message):
    try:
        # Check if the command was used as a reply to another user
        if message.reply_to_message:
            replied_user = message.reply_to_message.from_user  # Get the replied user
            target_id = message.reply_to_message.message_id  # ID of the replied message
            if replied_user:
                # Send animation reply to the replied user's message
                msg = await message.reply_to_message.reply("🧡")
        else:
            # If it's not a reply, reply to the sender
            msg = await message.reply("🧡.")

        # Animation sequence
        deq = deque(list("❤️🧡💛💚💙💜🖤"))
        for _ in range(20):  # Reduced iterations
            await asyncio.sleep(0.3)  # Increased sleep interval
            await msg.edit("".join(deq))
            deq.rotate(1)

    except FloodWait as e:
        await asyncio.sleep(e.value)  # Handle FloodWait exception
