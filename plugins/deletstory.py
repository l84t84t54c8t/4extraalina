from AlinaMusic import app
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid, RPCError


@app.on_message(filters.group)
async def detect_and_delete_story(client, message):
    try:
        # Check if the message contains media and if that media is a story
        if message.media and message.media.peer and hasattr(message.media, "story"):
            story_id = message.media.id
            user_id = message.media.peer.id

            try:
                # Fetch the story from the user
                story = await client.get_stories(user_id, story_id)

                # If a story is found, delete the message
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

            except RPCError as e:
                print(f"Failed to delete the story: {e}")
                await message.reply_text(
                    "⚠️ Error occurred while trying to delete the story."
                )

    except RPCError as e:
        print(f"Failed to detect or delete story: {e}")
        await message.reply_text("⚠️ Error occurred while processing the story.")
