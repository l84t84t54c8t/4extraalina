import os
from AlinaMusic import app
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMember

# Dictionary to store group settings
group_settings = {}

# Function to check if the user is in the channel
async def is_user_subscribed(user_id, channel_username):
    try:
        member = await app.get_chat_member(channel_username, user_id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.MEMBER]
    except Exception:
        return False

# Command handler to set the force subscribe channel
@app.on_message(filters.command("set_channel") & filters.group)
async def set_channel(client: Client, message: Message):
    # Check if the sender is an admin
    if not message.chat.has_protected_content or not (await app.get_chat_member(message.chat.id, message.from_user.id)).status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        await message.reply_text("You must be an admin to use this command.")
        return

    # Extract the channel username from the message
    channel_username = message.text.split()[1] if len(message.command) > 1 else None

    if not channel_username:
        await message.reply_text("Please provide the channel username (e.g., @YourChannel).")
        return

    # Store the channel username
    group_settings[message.chat.id] = {'channel': channel_username}
    await message.reply_text(f"Force subscribe channel set to {channel_username}.")

# Message handler to check membership on every message in the group
@app.on_message(filters.group)
async def check_subscription(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if the channel is set for the group
    if chat_id in group_settings:
        channel_username = group_settings[chat_id]['channel']
        
        # Check if the user is subscribed
        if not await is_user_subscribed(user_id, channel_username):
            # Delete the user's message
            await message.delete()
            
            # Send a warning message to the user in the chat
            await message.reply_text(
                f"You must join the channel @{channel_username} to send messages in this group. Please subscribe and try again."
            )


