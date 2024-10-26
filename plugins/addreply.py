from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from pyrogram import filters

# MongoDB collection for custom replies
custom_reply_db = mongodb.custom_replies  # Ensure you have a collection named 'custom_replies'

# Command to add a new custom reply (only for bot owner)
@app.on_message(filters.command("addreply") & SUDOERS)
async def add_custom_reply(client, message):
    try:
        # Command format: /addreply <trigger_word> <response_type> <response_content>
        parts = message.text.split(maxsplit=3)
        if len(parts) < 4:
            await message.reply_text(
                "Usage: /addreply <trigger_word> <response_type> <response_content>"
            )
            return

        trigger_word = parts[1]
        response_type = parts[2]
        response_content = parts[3]  # All remaining content after the third split

        # Insert into MongoDB
        update_data = {
            "trigger_word": trigger_word,
            "response_type": response_type,
            "response_content": response_content,
        }
        await custom_reply_db.update_one(
            {"trigger_word": trigger_word}, {"$set": update_data}, upsert=True
        )

        await message.reply_text(f"Reply added for trigger word '{trigger_word}'!")
    except Exception as e:
        await message.reply_text("Error adding reply.")
        print(e)

# Automatically reply when a trigger word is detected
@app.on_message(filters.text & (filters.group | filters.private))
async def reply_to_trigger_word(client, message):
    try:
        # Check if the message text matches a trigger word in the database
        trigger_data = await custom_reply_db.find_one({"trigger_word": message.text})
        if trigger_data:
            response_type = trigger_data["response_type"]
            response_content = trigger_data["response_content"]

            # Reply based on the response type
            if response_type == "text":
                await message.reply_text(response_content)
            elif response_type == "photo":
                await message.reply_photo(response_content)
            elif response_type == "document":
                await message.reply_document(response_content)
            elif response_type == "audio":
                await message.reply_audio(response_content)
            elif response_type == "animation":
                await message.reply_animation(response_content)
            elif response_type == "sticker":
                await message.reply_sticker(response_content)
            else:
                await message.reply_text("Unknown response type.")
    except Exception as e:
        print(e)
