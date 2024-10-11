from AlinaMusic import app
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid, RPCError, StoryInvalid


@app.on_message(filters.group)
async def detect_and_delete_story(client, message):
    # First, check if the message contains media that might be a story
    try:
        if message.media and message.media.peer and hasattr(message.media, "story"):
            # Get story details using Pyrogram's `get_stories` method from the document
            story_id = message.media.id
            user_id = message.media.peer.id

            try:
                # Fetch the story to interact with it
                story = await client.get_stories(user_id, story_id)

                # If the story is found, delete it
                if story:
                    await message.delete()
                    await message.reply_text(
                        "⛔ Forwarded stories are not allowed and have been deleted."
                    )

            except PeerIdInvalid:
                print(
                    f"Invalid Peer ID for story in chat {message.chat.id}. Cannot delete the story."
                )
                await message.reply_text(
                    "⚠️ The story could not be deleted due to an invalid peer ID."
                )

            except StoryInvalid:
                print(f"Story is invalid or could not be fetched for user {user_id}")
                await message.reply_text(
                    "⚠️ This story could not be found or is invalid."
                )

    except RPCError as e:
        print(f"Failed to delete story due to: {e}")
        await message.reply_text("⚠️ Error occurred while trying to delete the story.")
