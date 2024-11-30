from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError


@app.on_message(filters.story)
async def delete_story(client, message):
    chat_id = message.chat.id

    # Ensure the story is sent by a user
    if message.from_user is None:
        return

    try:
        # Check if the bot is an admin with "Delete Stories of Others" permission
        chat_member = await app.get_chat_member(chat_id, (await app.get_me()).id)
        if chat_member.status != ChatMemberStatus.ADMINISTRATOR:
            print(f"Bot is not an admin in chat {chat_id}")
            return
        
        # Delete the story if it's from a regular member
        if chat_member.privileges.delete_stories_of_others:
            await message.delete()
            print(f"Deleted a story in chat {chat_id}")
        else:
            print(f"Bot lacks the permission to delete stories in chat {chat_id}")

    except RPCError as e:
        print(f"Failed to delete story in chat {chat_id}: {e}")



"""
from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden, PeerIdInvalid, RPCError


# Story Deletion
@app.on_message(filters.story)
async def delete_story(_, message):
    chat_id = message.chat.id

    # Check if deletion is enabled for this chat
    if not await is_deletion_enabled(chat_id):
        return

    # Ensure from_user exists before proceeding
    if not message.from_user:
        return  # Exit if there's no user attached to the message

    # Skip deletion if the message is from the bot owner
    if message.from_user.id in SUDOERS:
        return

    try:
        # Get the sender's chat member status
        member = await app.get_chat_member(chat_id, message.from_user.id)

        # Check if the user is a regular member (not admin or owner)
        if member.status == ChatMemberStatus.MEMBER:
            # Attempt to delete the story message
            await message.delete()
    except MessageDeleteForbidden:
        print("Bot does not have permission to delete the story.")
    except PeerIdInvalid:
        print("Invalid Peer ID. The user might not be in the group.")
    except RPCError as e:
        print(f"Failed to delete the story: {e}")
"""
