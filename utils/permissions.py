import logging
from functools import wraps
from traceback import format_exc

from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from pyrogram.errors import ChatWriteForbidden
from pyrogram.types import Message

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def member_permissions(chat_id: int, user_id: int) -> list[str]:
    """
    Retrieve a user's permissions in a chat.
    """
    perms = []
    member = (await app.get_chat_member(chat_id, user_id)).privileges
    if not member:
        return perms
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_video_chats:
        perms.append("can_manage_video_chats")
    return perms


async def bot_permissions(chat_id: int) -> list[str]:
    """
    Retrieve the bot's permissions in a chat.
    """
    return await member_permissions(chat_id, app.id)


async def authorised(func, client, message: Message, *args, **kwargs):
    """
    Wrapper for handling authorised actions with error management.
    """
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        logging.error(
            f"Bot lacks permission to write in chat {message.chat.id}. Leaving the chat."
        )
        await app.leave_chat(message.chat.id)
    except Exception as e:
        logging.exception(f"Error in authorised function: {e}")
        try:
            await message.reply_text(f"**Error:** {str(e)}")
        except ChatWriteForbidden:
            await app.leave_chat(message.chat.id)
        logging.debug(f"Traceback: {format_exc()}")


async def unauthorised(message: Message, permission: str, bot_lacking_permission=False):
    """
    Notify a user of unauthorised access.
    """
    chat_id = message.chat.id
    text = (
        f"**👮🏻 | ببورە، تۆ ڕۆڵی نییە**\n"
        f"**👮🏻 | پێویستە ڕۆڵی  __{permission}__ هەبێت!**"
    )
    if bot_lacking_permission:
        text = f"**❌ بۆت ڕۆڵی نییە\nڕۆڵی:** `{permission}`."

    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        logging.error(f"Bot cannot send messages in chat {chat_id}. Leaving the chat.")
        await app.leave_chat(chat_id)


def adminsOnly(permission: str):
    """
    Decorator to enforce admin-only commands with specific permissions.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(client, message: Message, *args, **kwargs):
            chat_id = message.chat.id

            # Check bot's permissions
            bot_perms = await bot_permissions(chat_id)
            if permission not in bot_perms:
                return await unauthorised(
                    message, permission, bot_lacking_permission=True
                )

            # Handle anonymous admins
            if not message.from_user:
                if message.sender_chat and message.sender_chat.id == chat_id:
                    return await authorised(func, client, message, *args, **kwargs)
                return await unauthorised(message, permission)

            # Handle regular users and SUDOERS
            user_id = message.from_user.id
            if user_id in SUDOERS:
                return await authorised(func, client, message, *args, **kwargs)

            user_perms = await member_permissions(chat_id, user_id)
            if permission not in user_perms:
                return await unauthorised(message, permission)

            return await authorised(func, client, message, *args, **kwargs)

        return wrapper

    return decorator
