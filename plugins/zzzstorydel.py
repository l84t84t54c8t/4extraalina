from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden, PeerIdInvalid, RPCError


# Story Deletion
@app.on_message(filters.story, group=70)
async def delete_story(client, message):
    chat_id = message.chat.id

    # Check if deletion is enabled for this chat
    if not await is_deletion_enabled(chat_id):
        return

    # Ensure from_user exists before proceeding
    if message.from_user is None:
        return  # Exit if there's no user attached to the message

    # Skip deletion if the message is from the bot owner
    if message.from_user.id == SUDOERS:
        return

    try:
        # Get the sender's chat member status
        member = await app.get_chat_member(chat_id, message.from_user.id)

        # Check if the user is a regular member (not admin or owner)
        if member.status == ChatMemberStatus.MEMBER:
            # Attempt to delete the story message
            await message.delete()

    except (PeerIdInvalid, RPCError) as e:
        print(f"Failed to delete the story: {e}")
    except MessageDeleteForbidden:
        print("Bot does not have permission to delete the story.")
