from AlinaMusic import app
from pyrogram import enums, filters

from utils.permissions import adminsOnly

BOT_ID = app.id


@app.on_message(
    filters.command(
        ["unbanll", "لادانی دەرکراوەکان", "لادانی باندکراوەکان"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
)
@adminsOnly("can_restrict_members")
async def unban_all(_, msg):
    chat_id = msg.chat.id
    x = 0
    bot = await app.get_chat_member(chat_id, BOT_ID)
    bot_permission = bot.privileges.can_restrict_members == True
    if bot_permission:
        banned_users = []
        async for m in app.get_chat_members(
            chat_id, filter=enums.ChatMembersFilter.BANNED
        ):
            if m.user:  # Ensure m.user is not None
                banned_users.append(m.user.id)

        # Send message with total number of banned users found
        ok = await app.send_message(
            chat_id,
            f"**کۆی {len(banned_users)} بەکارهێنەری باندکراو دۆزرایەوە\n\nباندیان لادەدەم . . **",
        )

        for user_id in banned_users:
            try:
                await app.unban_chat_member(chat_id, user_id)
                x += 1

                # Edit message every 5 unbans to show progress
                if x % 5 == 0:
                    await ok.edit_text(
                        f"**لادانی باندی {x} لە {len(banned_users)} بەکارهێنەر**"
                    )

            except Exception:
                pass

        # Edit final message to show completion
        await ok.edit_text(f"**باندی {len(banned_users)} بەکارهێنەر لادرا**")

    else:
        await msg.reply_text(
            "**من مافی ئەوەم نییە بەکارهێنەران سنووردار بکەم یان تۆ لە گەشەپێدەران نیت🖤•**"
        )
