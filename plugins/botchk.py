import asyncio
from datetime import datetime

from AlinaMusic import app
from AlinaMusic.utils.database import get_assistant
from strings.filter import command

# Assuming Userbot is defined elsewhere

last_checked_time = None


@app.on_message(
    command(
        [
            "/botcheck",
            "/botchk",
            "پشکنینی بوت",
            "چالاکی بوت",
            "پشکنینی بۆت",
            "چالاکی بۆت",
        ]
    )
)
async def check_bots_command(client, message):
    global last_checked_time
    try:
        # Start the Pyrogram client
        userbot = await get_assistant(message.chat.id)

        # Get current time before sending messages
        start_time = datetime.now()

        # Extract bot username from command
        command_parts = message.command
        if len(command_parts) == 2:
            bot_username = command_parts[1]
            response = ""  # Define response variable
            try:
                bot = await userbot.get_users(bot_username)
                bot_id = bot.id
                await asyncio.sleep(0.5)
                await userbot.send_message(bot_id, "/start")
                await asyncio.sleep(3)
                # Check if bot responded to /start message
                async for bot_message in userbot.get_chat_history(bot_id, limit=1):
                    if bot_message.from_user.id == bot_id:
                        response += f"**⇜ پشکنین بۆ {bot.mention} **\n l\n**⇜ بۆت: چالاکە ✅\n\n**"
                    else:
                        response += f"**⇜ پشکنین بۆ [{bot.mention}](tg://user?id={bot.id})**\n l\n**⇜ بۆت: ناچالاکە ❌**\n\n"
            except Exception:
                response += f"**╭⎋ {bot_username}\n l\n⇜ تۆ یوزەری بۆتی هەڵەت پێداوم تکایە دڵنیابەوە لەوەی کە یوزەرەکە ڕاستە**\n\n"
            # Update last checked time
            last_checked_time = start_time.strftime("%Y-%m-%d")
            await message.reply_text(
                f"**{response}⏲️ کۆتا پشکنین: {last_checked_time} **"
            )
        else:
            await message.reply_text(
                "**⇜ فەرمانت هەڵە بەکارهێنا\n\n⇜ تکایە بەم شێوازە بیکە /botcheck یوزەری بۆت**\n\n**⇜ نموونە :** `/botcheck @IQM2BOT`"
            )
    except Exception as e:
        await message.reply_text(f"**⇜ هەڵەیەك ڕوویدا: {e}**")
        print(f"Error occurred during /botschk command: {e}")
