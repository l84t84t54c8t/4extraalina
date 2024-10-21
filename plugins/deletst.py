from AlinaMusic import app
from AlinaMusic.utils.database import is_deletion_enabled, set_deletion_feature
from AlinaMusic.utils.permissions import adminsOnly
from pyrogram import filters

from .Forward import joinch


# Command to enable or disable story deletion
@app.on_message(filters.command("story") & filters.group)
@adminsOnly("can_delete_messages")
async def toggle_delete(_, message):
    if await joinch(message):
        return
    chat_id = message.chat.id
    action = message.command[1].lower() if len(message.command) > 1 else None

    if action not in ["on", "off"]:
        await message.reply_text(
            "**• کۆنتڕۆڵ کردنی ناردنی ستۆری**\n-بۆ داخستن و کردنەوەی ستۆری لە گرووپ\n\n- داخستنی ستۆری :\n/story off\n- کردنەوەی ستۆری :\n/story on"
        )
        return

    if action == "on":
        if await is_deletion_enabled(chat_id):
            await set_deletion_feature(chat_id, False)  # Disable deletion
            await message.reply_text(
                "**• بە سەرکەوتوویی سڕینەوەی ستۆری ناچالاککرا ✅**"
            )
        else:
            await message.reply_text("**• سڕینەوەی ستۆری پێشتر ناچالاککراوە ✅**")

    elif action == "off":
        if not await is_deletion_enabled(chat_id):
            await set_deletion_feature(chat_id, True)  # Enable deletion
            await message.reply_text("**• بە سەرکەوتوویی سڕینەوەی ستۆری چالاککرا ✅**")
        else:
            await message.reply_text("**• سڕینەوەی ستۆری پێشتر چالاککراوە ✅**")


@app.on_message(filters.command("getstory") & filters.group)
@adminsOnly("can_delete_messages")
async def check_forwarded_deletion(client, message):
    if await joinch(message):
        return
    # Check if deletion is enabled for the chat
    deletion_status = await is_deletion_enabled(message.chat.id)

    # Respond with the current status
    if deletion_status:
        await message.reply("**• سڕینەوەی ستۆری چالاککراوە ✅**")
    else:
        await message.reply("**• سڕینەوەی ستۆری ناچالاککراوە ❌**")
