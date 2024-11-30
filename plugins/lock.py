from AlinaMusic import app
from pyrogram import filters
from pyrogram.types import ChatPermissions

from utils.permissions import adminsOnly


# mongo_commands.py

from AlinaMusic.core.mongo import mongodb

# MongoDB collection for storing locked permissions
locksdb = mongodb.locke

# Function to lock a permission for a chat
async def lock_permission(chat_id: int, permission_key: str) -> bool:
    """Lock a specific permission in MongoDB."""
    update_data = {permission_key: False}
    result = await locksdb.update_one(
        {"chat_id": chat_id},
        {"$set": update_data},
        upsert=True,
    )
    return result.modified_count > 0 or result.upserted_id is not None

# Function to unlock a permission for a chat
async def unlock_permission(chat_id: int, permission_key: str) -> bool:
    """Unlock a specific permission in MongoDB."""
    update_data = {permission_key: True}
    result = await locksdb.update_one(
        {"chat_id": chat_id},
        {"$set": update_data},
        upsert=True,
    )
    return result.modified_count > 0 or result.upserted_id is not None

# Function to lock all permissions for a chat
async def lock_all_permissions(chat_id: int) -> bool:
    """Lock all permissions for a chat."""
    update_data = {key: False for key in ["messages", "media", "polls", "other", "web_preview", "invite", "pin", "info"]}
    result = await locksdb.update_one(
        {"chat_id": chat_id},
        {"$set": update_data},
        upsert=True,
    )
    return result.modified_count > 0 or result.upserted_id is not None

# Function to unlock all permissions for a chat
async def unlock_all_permissions(chat_id: int) -> bool:
    """Unlock all permissions for a chat."""
    update_data = {key: True for key in ["messages", "media", "polls", "other", "web_preview", "invite", "pin", "info"]}
    result = await locksdb.update_one(
        {"chat_id": chat_id},
        {"$set": update_data},
        upsert=True,
    )
    return result.modified_count > 0 or result.upserted_id is not None

# Function to get locked permissions for a chat
async def get_locked_permissions(chat_id: int) -> dict:
    """Get all locked permissions for a chat."""
    data = await locksdb.find_one({"chat_id": chat_id})
    return data or {}


# Expanded permission map
PERMISSION_MAP = {
    "messages": "can_send_messages",
    "media": "can_send_media_messages",
    "polls": "can_send_polls",
    "gif": "can_send_other_messages",
    "sticker": "can_send_other_messages",
    "web_preview": "can_add_web_page_previews",
    "invite": "can_invite_users",
    "pin": "can_pin_messages",
    "info": "can_change_info",
}

# Lock specific permission

# Lock specific permission and store in MongoDB
@app.on_message(filters.command("lock") & filters.group)
async def lock_permission_handler(client, message):
    if len(message.command) < 2:
        await message.reply(
            "Please specify the permission to lock (e.g., /lock media) or use /lock all to lock all permissions."
        )
        return

    permission_key = message.command[1].lower()

    try:
        if permission_key == "all":
            # Lock all permissions
            if await lock_all_permissions(message.chat.id):
                await message.reply("All permissions have been locked!")
            else:
                await message.reply("Failed to lock all permissions.")
        else:
            # Lock a specific permission
            permission_name = PERMISSION_MAP.get(permission_key)
            if not permission_name:
                await message.reply(
                    f"Invalid permission type: {permission_key}. Use one of {', '.join(PERMISSION_MAP.keys())} or 'all'."
                )
                return

            if await lock_permission(message.chat.id, permission_key):
                await message.reply(f"{permission_key.capitalize()} has been locked!")
            else:
                await message.reply(f"Failed to lock {permission_key}.")
    except Exception as e:
        await message.reply(f"Error while locking: {e}")


# Unlock specific permission and remove from MongoDB
@app.on_message(filters.command("unlock") & filters.group)
async def unlock_permission_handler(client, message):
    if len(message.command) < 2:
        await message.reply(
            "Please specify the permission to unlock (e.g., /unlock media) or use /unlock all to unlock all permissions."
        )
        return

    permission_key = message.command[1].lower()

    try:
        if permission_key == "all":
            # Unlock all permissions
            if await unlock_all_permissions(message.chat.id):
                await message.reply("All permissions have been unlocked!")
            else:
                await message.reply("Failed to unlock all permissions.")
        else:
            # Unlock a specific permission
            permission_name = PERMISSION_MAP.get(permission_key)
            if not permission_name:
                await message.reply(
                    f"Invalid permission type: {permission_key}. Use one of {', '.join(PERMISSION_MAP.keys())} or 'all'."
                )
                return

            if await unlock_permission(message.chat.id, permission_key):
                await message.reply(f"{permission_key.capitalize()} has been unlocked!")
            else:
                await message.reply(f"Failed to unlock {permission_key}.")
    except Exception as e:
        await message.reply(f"Error while unlocking: {e}")


# View currently locked permissions stored in MongoDB
@app.on_message(filters.command("locks") & filters.group)
async def view_locked_permissions(client, message):
    locked_permissions = await get_locked_permissions(message.chat.id)
    if locked_permissions:
        locked_permissions_list = "\n".join(
            [f"{key.capitalize()} is locked 🚫" for key, value in locked_permissions.items() if value is False]
        )
        await message.reply(f"**Locked Permissions:**\n\n{locked_permissions_list}")
    else:
        await message.reply("No permissions are currently locked.")


# View all permissions


@app.on_message(filters.command("grouppermissions") & filters.group)
async def view_locks(client, message):
    try:
        chat = await client.get_chat(message.chat.id)
        current_permissions = chat.permissions or ChatPermissions()

        # Generate a readable format of permissions
        permissions_status = []
        for key, attribute in PERMISSION_MAP.items():
            is_allowed = getattr(
                current_permissions, attribute, True
            )  # Default to True
            status = "Unlocked ✅" if is_allowed else "Locked 🚫"
            permissions_status.append(f"{key.capitalize()}: {status}")

        # Send the permissions as a message
        permissions_text = "\n".join(permissions_status)
        await message.reply(f"**Current Chat Permissions:**\n\n{permissions_text}")
    except Exception as e:
        await message.reply(f"Failed to retrieve permissions: {e}")


# Show available lock types
@app.on_message(filters.command("locktypes") & filters.group)
async def lock_types(client, message):
    lock_types = "\n".join([f"{key}" for key in PERMISSION_MAP.keys()])
    lock_types += "\nall"
    await message.reply(f"**Available lock types:**\n\n{lock_types}")


__MODULE__ = "locks"

__HELP__ = """
**Locks**

Use this to lock group permissions.
Allows you to lock and unlock permission types in the chat.

**Usage:**
• /lock `<type>`: Lock Chat permission.
• /unlock `<type>`: Unlock Chat permission.
• /locks: View Chat permission.
• /locktypes: Check available lock types!

**Example:**
`/lock media`: this locks all the media messages in the chat."""
