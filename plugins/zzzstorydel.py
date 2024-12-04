from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError


@app.on_message(filters.group, group=101)  # Capture all group messages
async def delete_story_messages(client, message):
    # Skip if the message is not a story
    if not message.story:
        return

    # Skip if the message has no sender (e.g., anonymous admin messages)
    if message.from_user is None:
        return

    chat_id = message.chat.id

    # Check if story deletion is enabled for the group
    if not await is_deletion_enabled(chat_id):
        return

    # Skip deletion if the user is in SUDOERS
    if message.from_user.id in SUDOERS:
        return

    try:
        # Check the user's status in the group
        chat_member = await client.get_chat_member(chat_id, message.from_user.id)
        if chat_member.status == ChatMemberStatus.MEMBER:
            await message.delete()  # Delete the story if the user is a regular member
    except RPCError as e:
        # Log any errors for debugging
        print(f"Error while deleting story message in chat {chat_id}: {e}")
