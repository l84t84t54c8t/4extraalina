from AlinaMusic import app
from pyrogram import filters
from pyrogram.types import ChatPermissions

# Expanded permission map
PERMISSION_MAP = {
    "messages": "can_send_messages",
    "media": "can_send_media_messages",
    "polls": "can_send_polls",
    "other": "can_send_other_messages",
    "web_preview": "can_add_web_page_previews",
    "invite": "can_invite_users",
    "pin": "can_pin_messages",
    "info": "can_change_info",
}

# Lock specific permission


@app.on_message(filters.command("lock") & filters.group)
async def lock_permission(client, message):
    if len(message.command) < 2:
        await message.reply(
            "Please specify the permission to lock (e.g., /lock media)."
        )
        return

    permission_key = message.command[1].lower()
    permission_name = PERMISSION_MAP.get(permission_key)

    if not permission_name:
        await message.reply(
            f"Invalid permission type: {permission_key}. Use one of {', '.join(PERMISSION_MAP.keys())}."
        )
        return

    try:
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
async def unlock_permission(client, message):
    if len(message.command) < 2:
        await message.reply(
            "Please specify the permission to unlock (e.g., /unlock media)."
        )
        return

    permission_key = message.command[1].lower()
    permission_name = PERMISSION_MAP.get(permission_key)

    if not permission_name:
        await message.reply(
            f"Invalid permission type: {permission_key}. Use one of {', '.join(PERMISSION_MAP.keys())}."
        )
        return

    try:
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
