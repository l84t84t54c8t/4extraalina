from AlinaMusic import app
from pyrogram import filters
from pyrogram.types import ChatPermissions

from utils.permissions import adminsOnly

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


@app.on_message(filters.command("lock") & filters.group)
@adminsOnly("can_restrict_members")
async def lock_permission(client, message):
    if len(message.command) < 2:
        await message.reply(
            "Please specify the permission to lock (e.g., /lock media) or use /lock all to lock all permissions."
        )
        return

    permission_key = message.command[1].lower()

    try:
        if permission_key == "all":
            # Lock all permissions
            updated_permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_change_info=False,
            )
            await client.set_chat_permissions(
                chat_id=message.chat.id, permissions=updated_permissions
            )
            await message.reply("All permissions have been locked!")
        else:
            # Lock a specific permission
            permission_name = PERMISSION_MAP.get(permission_key)

            if not permission_name:
                await message.reply(
                    f"Invalid permission type: {permission_key}. Use one of {', '.join(PERMISSION_MAP.keys())} or 'all'."
                )
                return

            # Get current permissions and create a new permissions object
            chat = await client.get_chat(message.chat.id)
            current_permissions = chat.permissions or ChatPermissions()
            updated_permissions = ChatPermissions(
                **{
                    key: getattr(current_permissions, key)
                    for key in PERMISSION_MAP.values()
                }
            )
            # Disable the specified permission
            setattr(updated_permissions, permission_name, False)

            await client.set_chat_permissions(
                chat_id=message.chat.id, permissions=updated_permissions
            )
            await message.reply(f"{permission_key.capitalize()} has been locked!")
    except Exception as e:
        await message.reply(f"Failed to lock {permission_key}: {e}")


# Unlock specific permission
@app.on_message(filters.command("unlock") & filters.group)
@adminsOnly("can_restrict_members")
async def unlock_permission(client, message):
    if len(message.command) < 2:
        await message.reply(
            "Please specify the permission to unlock (e.g., /unlock media) or use /unlock all to unlock all permissions."
        )
        return

    permission_key = message.command[1].lower()

    try:
        if permission_key == "all":
            # Unlock all permissions
            updated_permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_change_info=True,
            )
            await client.set_chat_permissions(
                chat_id=message.chat.id, permissions=updated_permissions
            )
            await message.reply("All permissions have been unlocked!")
        else:
            # Unlock a specific permission
            permission_name = PERMISSION_MAP.get(permission_key)

            if not permission_name:
                await message.reply(
                    f"Invalid permission type: {permission_key}. Use one of {', '.join(PERMISSION_MAP.keys())} or 'all'."
                )
                return

            # Get current permissions and create a new permissions object
            chat = await client.get_chat(message.chat.id)
            current_permissions = chat.permissions or ChatPermissions()
            updated_permissions = ChatPermissions(
                **{
                    key: getattr(current_permissions, key)
                    for key in PERMISSION_MAP.values()
                }
            )
            # Enable the specified permission
            setattr(updated_permissions, permission_name, True)

            await client.set_chat_permissions(
                chat_id=message.chat.id, permissions=updated_permissions
            )
            await message.reply(f"{permission_key.capitalize()} has been unlocked!")
    except Exception as e:
        await message.reply(f"Failed to unlock {permission_key}: {e}")


# View current permissions
@app.on_message(filters.command("locks") & filters.group)
async def view_locks(client, message):
    try:
        chat = await client.get_chat(message.chat.id)
        current_permissions = chat.permissions or ChatPermissions()

        # Generate a readable format of permissions
        permissions_status = []
        for key, attribute in PERMISSION_MAP.items():
            is_allowed = getattr(current_permissions, attribute, True)  # Default to True
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
