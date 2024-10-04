from AlinaMusic import app
from pyrogram import filters

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
