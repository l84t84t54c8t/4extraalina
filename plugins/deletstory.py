from AlinaMusic import app
from pyrogram import Client, filters
from pyrogram.errors import RPCError, PeerIdInvalid


@app.on_message(filters.group)
async def detect_and_delete_story(client, message):
    try:
        # Check if the message contains a story
        if message.story:
            story_id = message.story.id
            user_id = message.story.from_user.id  # Get the user who sent the story

            try:
                # Fetch the story details (not always necessary, but added for demonstration)
                story = await client.get_stories(user_id, story_id)

                # Delete the story from the chat
                await message.delete()
                await message.reply_text("⛔ Forwarded stories are not allowed and have been deleted.")

            except PeerIdInvalid:
                print(f"Invalid Peer ID for story in chat {message.chat.id}. Cannot delete the story.")
                await message.reply_text("⚠️ The story could not be deleted due to an invalid peer ID.")

            except RPCError as e:
                print(f"Failed to delete the story: {e}")
                await message.reply_text("⚠️ Error occurred while trying to delete the story.")
        else:
            print("No story found in the message.")
    
    except AttributeError:
        # Handle cases where the message doesn't contain a story attribute
        print(f"Message in chat {message.chat.id} does not contain a story.")
    
    except RPCError as e:
        print(f"Failed to process story: {e}")
        await message.reply_text("⚠️ Error occurred while processing the story.")


