from AlinaMusic import app
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError
from pyrogram.types import ChatPrivileges


@app.on_message(filters.story)
async def delete_story(_, message):
    if not message.from_user:
        return  # Exit if there's no sender attached to the story

    chat_id = message.chat.id

    try:
        # Get the bot's membership details in the chat
        bot_member = await app.get_chat_member(chat_id, (await app.get_me()).id)

        # Check if the bot is an admin with specific privileges
        if (
            bot_member.status == ChatMemberStatus.ADMINISTRATOR
            # Ensure privileges are present
            and isinstance(bot_member.privileges, ChatPrivileges)
            and bot_member.privileges.can_delete_stories
        ):
            await message.delete()
            print(f"Deleted a story in chat {chat_id}")
        else:
            print(f"Bot is missing 'can_delete_stories' privilege in chat {chat_id}")

    except RPCError as e:
        print(f"Error occurred while deleting story in chat {chat_id}: {e}")
