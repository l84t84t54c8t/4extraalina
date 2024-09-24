import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from AlinaMusic import app
from AlinaMusic.misc import SUDOERS

BOT_ID = app.id


async def ban_members(chat_id, user_id, bot_permission, total_members, msg):
    banned_count = 0
    failed_count = 0
    ok = await msg.reply_text(
        f"Total members found: {total_members}\n**Started Banning..**"
    )

    while failed_count <= 30:
        async for member in app.get_chat_members(chat_id):
            if failed_count > 30:
                break  # Stop if failed bans exceed 30

            try:
                if member.user.id != user_id and member.user.id not in SUDOERS:
                    await app.ban_chat_member(chat_id, member.user.id)
                    banned_count += 1

                    if banned_count % 5 == 0:
                        try:
                            await ok.edit_text(
                                f"Banned {banned_count} members out of {total_members}"
                            )
                        except Exception:
                            pass  # Ignore if edit fails

            except FloodWait as e:
                await asyncio.sleep(e.x)  # Wait for the flood time and continue
            except Exception:
                failed_count += 1

        if failed_count <= 30:
            await asyncio.sleep(
                5
            )  # Retry every 5 seconds if failed bans are within the limit

    await ok.edit_text(
        f"Total banned: {banned_count}\nFailed bans: {failed_count}\nStopped as failed bans exceeded limit."
    )


@app.on_message(filters.command("banall") & SUDOERS)
async def ban_all(_, msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id  # ID of the user who issued the command

    bot = await app.get_chat_member(chat_id, BOT_ID)
    bot_permission = bot.privileges.can_restrict_members

    if bot_permission:
        total_members = 0
        async for _ in app.get_chat_members(chat_id):
            total_members += 1

        await ban_members(chat_id, user_id, bot_permission, total_members, msg)

    else:
        await msg.reply_text(
            "Either I don't have the right to restrict users or you are not in sudo users"
        )
