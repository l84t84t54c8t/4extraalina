from AlinaMusic import app
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatPrivileges
from pyrogram.errors import RPCError
from AlinaMusic.misc import SUDOERS  # Import your SUDOERS list from the correct location
from AlinaMusic.utils.database import is_deletion_enabled  # Import your DB function

@app.on_message(filters.story)
async def delete_story(_, message):
    if not message.from_user:
        return  # Exit if there's no sender attached to the story

    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if story deletion is enabled for this chat from the database
    if not await is_deletion_enabled(chat_id):
        print(f"Story deletion is disabled for chat {chat_id}")
        return  # Skip deletion if it's disabled for this chat

    try:
        # Get the bot's membership details
        bot_member = await app.get_chat_member(chat_id, (await app.get_me()).id)

        # Check if the bot is an admin with the "can_delete_stories" privilege
        if (
            bot_member.status == ChatMemberStatus.ADMINISTRATOR
            and isinstance(bot_member.privileges, ChatPrivileges)
            and bot_member.privileges.can_delete_stories
        ):
            # Skip deletion if the message is from a user in SUDOERS (including bot owner)
            if user_id in SUDOERS:
                print(f"Story from a privileged user (SUDOER) not deleted in chat {chat_id}")
                return  # Skip deletion for users in the SUDOERS list

            # Get the membership details of the user who posted the story
            user_member = await app.get_chat_member(chat_id, user_id)

            # Delete the story only if the user is a regular member
            if user_member.status == ChatMemberStatus.MEMBER:
                await message.delete()
                print(f"Deleted a story from a member in chat {chat_id}")
            else:
                print(f"Story from admin/owner not deleted in chat {chat_id}")
        else:
            print(f"Bot lacks permission to delete stories in chat {chat_id}")

    except RPCError as e:
        print(f"Error occurred while deleting story in chat {chat_id}: {e}")


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
