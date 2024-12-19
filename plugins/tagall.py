import asyncio

from AlinaMusic import app
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait, RPCError

# Global variable to keep track of active tagging chats
SPAM_CHATS = []


async def is_admin(chat_id, user_id):
    """Check if a user is an admin in the chat."""
    try:
        admin_ids = [
            admin.user.id
            async for admin in app.get_chat_members(
                chat_id, filter=ChatMembersFilter.ADMINISTRATORS
            )
        ]
        return user_id in admin_ids
    except RPCError as e:
        print(f"Error checking admin status: {e}")
        return False


@app.on_message(
    filters.command(["all", "allmention", "mentionall", "tagall"], prefixes=["/", "@"])
)
async def tag_all_users(_, message):
    """Tag all users in the chat."""
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "**پڕۆسەی تاگکردن چالاکە، بۆ وەستاندن بەکاربهێنە ➥ /cancel**"
        )

    replied = message.reply_to_message
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not text and not replied:
        return await message.reply_text(
            "**نامەیەک بنووسە یان ڕیپلە بکە.** `@all Hi Friends`"
        )

    SPAM_CHATS.append(message.chat.id)
    user_count = 0
    mention_text = ""

    try:
        async for member in app.get_chat_members(message.chat.id):
            if message.chat.id not in SPAM_CHATS:
                break
            if member.user.is_deleted or member.user.is_bot:
                continue
            user_count += 1
            mention_text += (
                f"[{member.user.first_name}](tg://user?id={member.user.id})  "
            )
            if user_count == 7:
                if replied:
                    await replied.reply_text(
                        mention_text, disable_web_page_preview=True
                    )
                else:
                    await message.reply_text(
                        f"{text}\n\n{mention_text}", disable_web_page_preview=True
                    )
                await asyncio.sleep(2)
                user_count = 0
                mention_text = ""

        if user_count > 0:
            if replied:
                await replied.reply_text(mention_text, disable_web_page_preview=True)
            else:
                await message.reply_text(
                    f"{text}\n\n{mention_text}", disable_web_page_preview=True
                )
    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
    except RPCError as e:
        print(f"Error during tagging: {e}")
    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except ValueError:
            pass


@app.on_message(
    filters.command(
        [
            "stopmention",
            "cancel",
            "cancelmention",
            "offmention",
            "mentionoff",
            "cancelall",
        ],
        prefixes=["/", "@"],
    )
)
async def cancelcmd(_, message):
    """Stop the tagging process."""
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if message.chat.id in SPAM_CHATS:
        SPAM_CHATS.remove(message.chat.id)
        await message.reply_text("**پڕۆسەی تاگ بە سەرکەوتوویی وەستا**")
    else:
        await message.reply_text("**پڕۆسەی تاگکردن بوونی نییە**")


@app.on_message(
    filters.command(["admin", "report"], prefixes=["/", "@"]) & filters.group
)
async def admintag_with_reporting(client, message):
    """Tag all admins or report a user to admins."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    admins = [
        admin.user.id
        async for admin in client.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]

    if message.command[0] == "report":
        if user_id in admins:
            return await message.reply_text("**You can't report other admins.**")

    reply = message.reply_to_message or message
    reported_user_id = reply.from_user.id if reply.from_user else None
    if reported_user_id and (reported_user_id in admins or reported_user_id == chat_id):
        return await message.reply_text("**You are trying to report an admin!**")

    text = "Reported the user to admins!\n"
    for admin_id in admins:
        admin = await client.get_chat_member(chat_id, admin_id)
        if not admin.user.is_bot and not admin.user.is_deleted:
            text += f"[\u2063](tg://user?id={admin_id})"

    await reply.reply_text(text)


@app.on_message(filters.command(["alladmins", "tagadmins"], prefixes=["/", "@"]))
async def tag_all_admins(_, message):
    """Tag all admins in the chat."""
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "**پڕۆسەی تاگکردن چالاکە، بۆ وەستاندن بەکاربهێنە ➥ /cancel**"
        )

    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    replied = message.reply_to_message
    mention_text = ""
    admin_count = 0

    SPAM_CHATS.append(message.chat.id)

    try:
        async for admin in app.get_chat_members(
            message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            if message.chat.id not in SPAM_CHATS:
                break
            if admin.user.is_deleted or admin.user.is_bot:
                continue
            admin_count += 1
            mention_text += f"[{admin.user.first_name}](tg://user?id={admin.user.id})  "
            if admin_count == 7:
                if replied:
                    await replied.reply_text(
                        mention_text, disable_web_page_preview=True
                    )
                else:
                    await message.reply_text(
                        f"{text}\n\n{mention_text}", disable_web_page_preview=True
                    )
                await asyncio.sleep(2)
                admin_count = 0
                mention_text = ""

        if admin_count > 0:
            if replied:
                await replied.reply_text(mention_text, disable_web_page_preview=True)
            else:
                await message.reply_text(
                    f"{text}\n\n{mention_text}", disable_web_page_preview=True
                )
    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
    except RPCError as e:
        print(f"Error during admin tagging: {e}")
    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except ValueError:
            pass


__MODULE__ = "Tᴀɢᴀʟʟ"
__HELP__ = """

@all ᴏʀ /all | /tagall ᴏʀ  @tagall | /mentionall ᴏʀ  @mentionall [ᴛᴇxᴛ] ᴏʀ [ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ] ᴛᴏ ᴛᴀɢ ᴀʟʟ ᴜsᴇʀ's ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ʙᴛ ʙᴏᴛ

/admins | @admin | /report [ᴛᴇxᴛ] ᴏʀ [ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ] ᴛᴏ ᴛᴀɢ ᴀʟʟ ᴀᴅᴍɪɴ's ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ


/cancel Oʀ @cancel |  /offmention Oʀ @offmention | /mentionoff Oʀ @mentionoff | /cancelall Oʀ @cancelall - ᴛᴏ sᴛᴏᴘ ʀᴜɴɴɪɴɢ ᴀɴʏ ᴛᴀɢ ᴘʀᴏᴄᴇss

**__Nᴏᴛᴇ__** Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ᴜsᴇ ᴛʜᴇ Aᴅᴍɪɴs ᴏғ Cʜᴀᴛ ᴀɴᴅ ᴍᴀᴋᴇ Sᴜʀᴇ Bᴏᴛ ᴀɴᴅ ᴀssɪsᴛᴀɴᴛ ɪs ᴀɴ ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ's
"""
