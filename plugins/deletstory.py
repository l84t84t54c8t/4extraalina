from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from YukkiMusic import app


@app.on_message(filters.forwarded)
async def delete_forwarded_stories(client, message):
    # Check if the forwarded message is a story
    if message.forward_from and message.forward_from.is_bot:
        # Check if the message was forwarded by a regular member (not a bot)
        chat_member = await client.get_chat_member(
            message.chat.id, message.forward_from.id
        )
        if chat_member.status == ChatMemberStatus.MEMBER:
            # Delete the message if it's a story
            if message.photo or message.video or message.audio or message.document:
                await message.delete()
