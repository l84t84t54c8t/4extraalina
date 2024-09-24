from AlinaMusic import app
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus


@app.on_message(filters.forwarded)
async def gjgh(app, m):
    # Ensure m.chat and m.from_user are not None
    if m.chat is None or m.from_user is None:
        return  # Exit the function if they are None

    # Fetch the chat member status
    chat_member = await app.get_chat_member(m.chat.id, m.from_user.id)
    su = chat_member.status

    # Check if the user's status is "member"
    if su == ChatMemberStatus.MEMBER:
        await m.delete()
