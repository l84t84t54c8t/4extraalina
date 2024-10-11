from AlinaMusic import app
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid, RPCError


@app.on_message(filters.group)
async def delete_story(client, message):
    try:
        # Check if the message contains a story
        if message.story:
            story_id = message.story.id
            user_id = message.story.from_user.id  # Get the user who sent the story

            try:
                # Attempt to delete the story
                await message.delete()
                await message.reply_text(
                    "⛔ Stories are not allowed and have been deleted."
                )
                print(f"Deleted story with ID: {story_id} from user: {user_id}")

            except PeerIdInvalid:
                print(
                    f"Invalid Peer ID for story in chat {message.chat.id}. Cannot delete the story."
                )
                await message.reply_text(
                    "⚠️ The story could not be deleted due to an invalid peer ID."
                )

            except RPCError as e:
                print(f"Failed to delete the story: {e}")
                await message.reply_text(
                    "⚠️ Error occurred while trying to delete the story."
                )
        else:
            print("No story found in the message.")

    except AttributeError:
        # Handle cases where the message doesn't contain a story attribute
        print(f"Message in chat {message.chat.id} does not contain a story.")

    except RPCError as e:
        print(f"Failed to process story: {e}")
        await message.reply_text("⚠️ Error occurred while processing the story.")
