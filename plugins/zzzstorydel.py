from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError


@app.on_message(filters.group, group=101)  # Capture all messages
async def delete_story_messages(client, message):
    if message.chat is None or message.from_user is None:
        return  # Exit if no chat or user info

    # Check if the message is a story
    if not message.story:
        return  # Skip non-story messages

    chat_id = message.chat.id  # Define chat ID

    # Check if story deletion is enabled for this chat
    if not await is_deletion_enabled(chat_id):
        return

    if message.from_user.id in SUDOERS:
        return

    try:
        # Get the user's status (member, admin, etc.)
        chat_member = await client.get_chat_member(chat_id, message.from_user.id)
        if chat_member.status == ChatMemberStatus.MEMBER:
            # Delete the story if the user is a regular member
            await message.delete()
    except RPCError as e:
        print(f"Failed to delete story message: {e}")
