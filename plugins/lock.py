from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus  # Import ChatMemberStatus
from pyrogram.types import ChatPermissions, Message

from utils.permissions import adminsOnly

# MongoDB collection for storing locked permissions
lockdb = mongodb.lock

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

# Lock specific permission and store in MongoDB


@app.on_message(filters.command("lock") & filters.group)
@adminsOnly("can_change_info")
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

            # Store all locked permissions in MongoDB
            await lockdb.update_one(
                {"chat_id": message.chat.id},
                {"$set": {permission_key: False for permission_key in PERMISSION_MAP}},
                upsert=True,
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

            # Store the locked permission in MongoDB
            await lockdb.update_one(
                {"chat_id": message.chat.id},
                {"$set": {permission_key: False}},
                upsert=True,
            )

            await message.reply(f"{permission_key.capitalize()} has been locked!")
    except Exception as e:
        await message.reply(f"Failed to lock {permission_key}: {e}")


# Unlock specific permission and remove from MongoDB
@app.on_message(filters.command("unlock") & filters.group)
@adminsOnly("can_change_info")
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

            # Remove all locked permissions from MongoDB
            await lockdb.update_one(
                {"chat_id": message.chat.id},
                {"$set": {permission_key: True for permission_key in PERMISSION_MAP}},
                upsert=True,
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

            # Remove the unlocked permission from MongoDB
            await lockdb.update_one(
                {"chat_id": message.chat.id},
                {"$set": {permission_key: True}},
                upsert=True,
            )

            await message.reply(f"{permission_key.capitalize()} has been unlocked!")
    except Exception as e:
        await message.reply(f"Failed to unlock {permission_key}: {e}")


# View currently locked permissions stored in MongoDB
@app.on_message(filters.command("locks") & filters.group)
@adminsOnly("can_change_info")
async def view_locks(client, message):
    data = await lockdb.find_one({"chat_id": message.chat.id})
    if data:
        locked_permissions_list = "\n".join(
            [
                f"{key.capitalize()} is locked 🚫"
                for key, value in data.items()
                if value is False
            ]
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
@app.on_message(filters.command("locktypes"))
async def lock_types(client, message):
    lock_types = "\n".join([f"{key}" for key in PERMISSION_MAP.keys()])
    lock_types += "\nall"
    await message.reply(f"**Available lock types:**\n\n{lock_types}")


# MongoDB collection for storing group settings (disabled or enabled)
# Assuming you have a 'group_settings' collection in your MongoDB
group_settings_collection = mongodb.group_settings

# Command to enable or disable the functionality (with or without slash)


@app.on_message(filters.group & filters.text)
@adminsOnly("can_change_info")
async def toggle_group_settings(client: Client, message: Message):
    chat_id = message.chat.id  # Using chat_id to identify the group
    command = message.text.strip().lower()

    # Check if the message starts with 'disable' or 'enable' (with or without
    # slash)
    if command in ["disable", "/disable", "داخستنی گرووپ"]:
        # Update the MongoDB to disable the group
        await group_settings_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"disabled": True}},
            upsert=True,  # This will insert the document if it doesn't exist
        )
        await message.reply_text(
            "**گرووپ داخرا\nئێستا هەموو نامەیەک لەم گرووپەدا ڕێگەپێنەدراوە.**"
        )
    elif command in ["enable", "/enable", "کردنەوەی گرووپ"]:
        # Update the MongoDB to enable the group
        await group_settings_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"disabled": False}},
            upsert=True,  # This will insert the document if it doesn't exist
        )
        await message.reply_text(
            "**گرووپ کرایەوە\nئێستا هەموو نامەیەک لەم گرووپەدا ڕێگەپێدراوە.**"
        )


# Check and delete specified message types (only for regular members)
@app.on_message(filters.group)
async def check_and_delete_messages(client: Client, message: Message):
    chat_id = message.chat.id  # Using chat_id here

    # Fetch the group settings from MongoDB
    group_data = await group_settings_collection.find_one({"chat_id": chat_id})

    # If the group settings are not found or the group is not disabled, skip
    if not group_data or not group_data.get("disabled", False):
        return

    try:
        # Get the user status (member, admin, etc.)
        chat_member = await app.get_chat_member(message.chat.id, message.from_user.id)

        # If the user is a regular member (not admin or owner), delete their
        # message
        if chat_member.status == ChatMemberStatus.MEMBER:
            # Check if the message is text or any other type and delete it
            if message.text or message.caption or message.story:  # Text or captioned messages
                await message.delete()
            else:
                # For other message types, check attributes
                for message_type in [
                    "photo",
                    "video",
                    "audio",
                    "document",
                    "poll",
                    "animation",
                    "sticker",
                    "voice",
                    "video_note",
                ]:
                    if getattr(message, message_type, None):
                        await message.delete()
                        break
    except Exception as e:
        print(f"Error: {e}")


"""
# Dictionary to track enabled/disabled state for groups
group_settings = {}

# Command to enable or disable the functionality (with or without slash)


@app.on_message(filters.group & filters.text)
async def toggle_group_settings(client: Client, message: Message):
    chat_id = message.chat.id  # Using chat_id to identify the group
    command = message.text.strip().lower()

    # Check if the message starts with 'disable' or 'enable' (with or without
    # slash)
    if command in ["disable", "/disable", "داخستنی گرووپ"]:
        group_settings[chat_id] = {"disabled": True}
        await message.reply_text(
            "**گرووپ داخرا\nئێستا هەموو نامەیەک لەم گرووپەدا ڕێگەپێنەدراوە.**"
        )
    elif command in ["enable", "/enable", "کردنەوەی گرووپ"]:
        group_settings[chat_id] = {"disabled": False}
        await message.reply_text(
            "**گرووپ کرایەوە\nئێستا هەموو نامەیەک لەم گرووپەدا ڕێگەپێدراوە.**"
        )


# Check and delete specified message types (only for regular members)


# Check and delete specified message types (only for regular members)
# Check and delete specified message types
@app.on_message(filters.group)
async def check_and_delete_messages(client: Client, message: Message):
    group_id = message.chat.id

    # Skip if the group is not disabled
    if not group_settings.get(group_id, False):
        return

    try:
        # Get the user status (member, admin, etc.)
        chat_member = await app.get_chat_member(message.chat.id, message.from_user.id)

        # If the user is a regular member (not admin or owner), delete their
        # message
        if chat_member.status == ChatMemberStatus.MEMBER:
            # Check if the message is text or any other type and delete it
            if message.text or message.caption:  # Text or captioned messages
                await message.delete()
            else:
                # For other message types, check attributes
                for message_type in [
                    "photo",
                    "video",
                    "audio",
                    "document",
                    "poll",
                    "animation",
                    "sticker",
                    "voice",
                    "video_note",
                ]:
                    if getattr(message, message_type, None):
                        await message.delete()
                        break
    except Exception as e:
        print(f"Error: {e}")
"""

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
