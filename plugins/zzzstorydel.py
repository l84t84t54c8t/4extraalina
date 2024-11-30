from AlinaMusic import app
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden

# Function to delete forwarded messages only from members


@app.on_message(filters.story)
async def delete_forwarded_messages(app, message):
    if message.chat is None or message.from_user is None:
        return  # Exit if no chat or user info

    # Check if the forwarded message deletion feature is enabled
    if not await is_deletion_enabled(message.chat.id):
        return

    try:
        # Get the user status (member, admin, etc.)
        chat_member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status == ChatMemberStatus.MEMBER:
            # Delete the message only if the user is a regular member
            await message.delete()

    except MessageDeleteForbidden:
        print("Bot does not have permission to delete the message.")
    except Exception as e:
        print(f"An error occurred: {e}")


"""
from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import is_deletion_enabled
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError
from pyrogram.types import ChatPrivileges


@app.on_message(filters.story)
async def delete_story(_, message):
    if not message.from_user:
        return  # Exit if there's no sender attached to the story

    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if deletion is enabled for this chat
    if not await is_deletion_enabled(chat_id):
        return

    # Skip deletion if the message is from the bot owner
    if message.from_user.id in SUDOERS:
        return

    try:
        # Get the bot's membership details
        bot_member = await app.get_chat_member(chat_id, (await app.get_me()).id)

        # Check if the bot is an admin with the "can_delete_stories" privilege
        if (
            bot_member.status == ChatMemberStatus.ADMINISTRATOR
            and isinstance(bot_member.privileges, ChatPrivileges)
            and bot_member.privileges.can_delete_stories
        ):
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
