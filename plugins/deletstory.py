from AlinaMusic import app
from pyrogram import Client, filters
from pyrogram.errors import RPCError, PeerIdInvalid
from pyrogram.enums import ChatMemberStatus

@app.on_message(filters.group)
async def delete_story(client, message):
    # Check if the message contains a story
    if message.story:
        try:
            # Get the sender's chat member status
            member = await client.get_chat_member(message.chat.id, message.from_user.id)

            # Check if the user is a regular member (not admin or owner)
            if member.status == ChatMemberStatus.MEMBER:
                # Attempt to delete the story message
                await message.delete()
                await message.reply_text("**• ببوورە ئەزیزم ناردنی ستۆری قەدەغەکراوە ⛔**")
                print(f"Deleted story with ID: {message.story.id} from user: {message.from_user.id}")
            else:
                print(f"User {message.from_user.id} is an admin or owner. Story will not be deleted.")
                
        except (PeerIdInvalid, RPCError) as e:
            print(f"Failed to delete the story: {e}")
            await message.reply_text("⚠️ Error occurred while trying to delete the story.")
    else:
        print("No story found in the message.")

