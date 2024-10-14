from AlinaMusic import app
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus


# Story Deletion
@app.on_message(filters.group)
async def delete_story(_, message):
    chat_id = message.chat.id
    # Check if story
    if not await is_deletion_enabled(chat_id):
        return

    # Ensure from_user exists before proceeding
    if message.from_user is None:
        return  # Exit if there's no user attached to the message

    # Check if the message contains a story
    if message.story:
        try:
            # Get the sender's chat member status
            member = await app.get_chat_member(message.chat.id, message.from_user.id)

            # Check if the user is a regular member (not admin or owner)
            if member.status == ChatMemberStatus.MEMBER:
                # Attempt to delete the story message
                await message.delete()

        except (PeerIdInvalid, RPCError) as e:
            print(f"Failed to delete the story: {e}")
        except MessageDeleteForbidden:
            print("Bot does not have permission to delete the story.")
