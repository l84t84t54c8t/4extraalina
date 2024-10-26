from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# MongoDB collection for custom replies
custom_reply_db = (
    mongodb.custom_replies
)  # Ensure you have a collection named 'custom_replies'


# Command to add a new custom reply with multiple buttons
@app.on_message(filters.command("addreply") & SUDOERS)
async def add_custom_reply(client, message):
    if not message.reply_to_message:
        await message.reply_text(
            "Please reply to the content you want to add as a reply."
        )
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text(
            "Usage: /addreply <trigger_word> <button_text:url;button_text:url>"
        )
        return

    trigger_word = parts[1].split()[0]  # Get the trigger word from the command
    reply_message = message.reply_to_message

    # Capture message type and content
    if reply_message.text:
        response_type = "text"
        response_content = reply_message.text
    elif reply_message.photo:
        response_type = "photo"
        response_content = reply_message.photo.file_id
    elif reply_message.sticker:
        response_type = "sticker"
        response_content = reply_message.sticker.file_id
    elif reply_message.document:
        response_type = "document"
        response_content = reply_message.document.file_id
    elif reply_message.audio:
        response_type = "audio"
        response_content = reply_message.audio.file_id
    elif reply_message.animation:
        response_type = "animation"
        response_content = reply_message.animation.file_id
    else:
        await message.reply_text("Unsupported message type.")
        return

    # Check for buttons in the command after the trigger word
    button_data = parts[1][
        len(trigger_word) :
    ].strip()  # Get everything after the trigger word
    buttons = []
    if button_data:
        button_pairs = button_data.split(";")
        for pair in button_pairs:
            button_parts = pair.split(":")
            if len(button_parts) == 2:
                button_text, url = button_parts[0].strip(), button_parts[1].strip()
                buttons.append([InlineKeyboardButton(button_text, url=url)])

    # Insert into MongoDB
    update_data = {
        "trigger_word": trigger_word,
        "response_type": response_type,
        "response_content": response_content,
        "buttons": buttons if buttons else None,
    }
    await custom_reply_db.update_one(
        {"trigger_word": trigger_word}, {"$set": update_data}, upsert=True
    )

    await message.reply_text(f"Reply added for trigger word '{trigger_word}'!")


# Inline query handler for custom replies
@app.on_inline_query()
async def inline_query_handler(client, inline_query):
    trigger_data = await custom_reply_db.find_one({"trigger_word": inline_query.query})

    if trigger_data:
        response_type = trigger_data["response_type"]
        response_content = trigger_data["response_content"]
        buttons = trigger_data.get("buttons")

        # Create the InlineKeyboardMarkup if buttons exist
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

        # Prepare the result for inline query
        if response_type == "text":
            result = [
                InlineQueryResultArticle(
                    id="1",
                    title="Response",
                    input_message_content=InputTextMessageContent(response_content),
                    reply_markup=reply_markup,
                )
            ]
        elif response_type == "photo":
            result = [
                InlineQueryResultPhoto(
                    id="1",
                    photo_url=response_content,
                    thumb_url=response_content,
                    reply_markup=reply_markup,
                )
            ]
        elif response_type == "document":
            result = [
                InlineQueryResultDocument(
                    id="1",
                    document_url=response_content,
                    title="Document",
                    reply_markup=reply_markup,
                )
            ]
        elif response_type == "audio":
            result = [
                InlineQueryResultAudio(
                    id="1",
                    audio_url=response_content,
                    title="Audio",
                    reply_markup=reply_markup,
                )
            ]
        elif response_type == "animation":
            result = [
                InlineQueryResultAnimation(
                    id="1",
                    animation_url=response_content,
                    title="Animation",
                    reply_markup=reply_markup,
                )
            ]
        elif response_type == "sticker":
            result = [
                InlineQueryResultSticker(
                    id="1", sticker_file=response_content, reply_markup=reply_markup
                )
            ]
        else:
            return  # Unsupported type

        await inline_query.answer(result)


# Command to delete an existing custom reply
@app.on_message(filters.command("delreply") & SUDOERS)
async def delete_custom_reply(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text("Usage: /delreply <trigger_word>")
        return

    trigger_word = parts[1]

    # Remove from MongoDB
    result = await custom_reply_db.delete_one({"trigger_word": trigger_word})
    if result.deleted_count > 0:
        await message.reply_text(f"Reply for trigger word '{trigger_word}' deleted!")
    else:
        await message.reply_text(f"No reply found for trigger word '{trigger_word}'.")


"""
from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup, filters

# MongoDB collection for custom replies
custom_reply_db = (
    mongodb.custom_replies
)  # Ensure you have a collection named 'custom_replies'


# Command to add a new custom reply with multiple buttons
@app.on_message(filters.command("addreply") & SUDOERS)
async def add_custom_reply(client, message):
    if not message.reply_to_message:
        await message.reply_text(
            "Please reply to the content you want to add as a reply."
        )
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text(
            "Usage: /addreply <trigger_word> <button_text:url;button_text:url>"
        )
        return

    trigger_word = parts[1].split()[0]  # Get the trigger word from the command
    reply_message = message.reply_to_message

    # Capture message type and content
    if reply_message.text:
        response_type = "text"
        response_content = reply_message.text
    elif reply_message.photo:
        response_type = "photo"
        response_content = reply_message.photo.file_id
    elif reply_message.sticker:
        response_type = "sticker"
        response_content = reply_message.sticker.file_id
    elif reply_message.document:
        response_type = "document"
        response_content = reply_message.document.file_id
    elif reply_message.audio:
        response_type = "audio"
        response_content = reply_message.audio.file_id
    elif reply_message.animation:
        response_type = "animation"
        response_content = reply_message.animation.file_id
    else:
        await message.reply_text("Unsupported message type.")
        return

    # Check for buttons in the command after the trigger word
    button_data = parts[1][
        len(trigger_word) :
    ].strip()  # Get everything after the trigger word
    buttons = []
    if button_data:
        button_pairs = button_data.split(";")
        for pair in button_pairs:
            button_parts = pair.split(":")
            if len(button_parts) == 2:
                button_text, url = button_parts[0].strip(), button_parts[1].strip()
                buttons.append([InlineKeyboardButton(button_text, url=url)])

    # Insert into MongoDB
    update_data = {
        "trigger_word": trigger_word,
        "response_type": response_type,
        "response_content": response_content,
        "buttons": buttons if buttons else None,
    }
    await custom_reply_db.update_one(
        {"trigger_word": trigger_word}, {"$set": update_data}, upsert=True
    )

    await message.reply_text(f"Reply added for trigger word '{trigger_word}'!")


# Automatically reply when a trigger word is detected
@app.on_message(filters.text & (filters.group | filters.private))
async def reply_to_trigger_word(client, message):
    try:
        # Check if the message text matches a trigger word in the database
        trigger_data = await custom_reply_db.find_one({"trigger_word": message.text})
        if trigger_data:
            response_type = trigger_data["response_type"]
            response_content = trigger_data["response_content"]
            buttons = trigger_data.get("buttons")

            # Create the InlineKeyboardMarkup if buttons exist
            reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

            # Reply based on the response type
            if response_type == "text":
                await message.reply_text(response_content, reply_markup=reply_markup)
            elif response_type == "photo":
                await message.reply_photo(response_content, reply_markup=reply_markup)
            elif response_type == "document":
                await message.reply_document(
                    response_content, reply_markup=reply_markup
                )
            elif response_type == "audio":
                await message.reply_audio(response_content, reply_markup=reply_markup)
            elif response_type == "animation":
                await message.reply_animation(
                    response_content, reply_markup=reply_markup
                )
            elif response_type == "sticker":
                await message.reply_sticker(response_content, reply_markup=reply_markup)
            else:
                await message.reply_text("Unknown response type.")
    except Exception as e:
        print(e)


# Command to delete an existing custom reply
@app.on_message(filters.command("delreply") & SUDOERS)
async def delete_custom_reply(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply_text("Usage: /delreply <trigger_word>")
        return

    trigger_word = parts[1]

    # Remove from MongoDB
    result = await custom_reply_db.delete_one({"trigger_word": trigger_word})
    if result.deleted_count > 0:
        await message.reply_text(f"Reply for trigger word '{trigger_word}' deleted!")
    else:
        await message.reply_text(f"No reply found for trigger word '{trigger_word}'.")

"""
