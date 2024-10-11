from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden, PeerIdInvalid, RPCError

# MongoDB collection for settings
settingsdb = mongodb.settings  # Ensure you have a collection named 'settings'


# Function to enable a feature (story or forwarded deletion)
async def set_deletion_feature(chat_id: int, feature: str, status: bool):
    update_data = {feature: status}
    result = await settingsdb.update_one(
        {"chat_id": chat_id}, {"$set": update_data}, upsert=True
    )
    return result.modified_count > 0 or result.upserted_id is not None


# Function to check if a feature (story or forwarded deletion) is enabled
async def is_deletion_enabled(chat_id: int, feature: str) -> bool:
    data = await settingsdb.find_one({"chat_id": chat_id})
    if not data:
        return False  # Default to disabled if no data exists
    return data.get(feature, False)  # Default to False if not set


# Command to enable story or forwarded deletion
@app.on_message(filters.command("enable_delete") & filters.group)
async def enable_delete(client, message):
    chat_id = message.chat.id
    feature = message.command[1] if len(message.command) > 1 else None

    if feature not in ["story", "forwarded"]:
        await message.reply_text("Usage: /enable_delete <story|forwarded>")
        return

    is_enabled = await is_deletion_enabled(chat_id, feature)

    if is_enabled:
        await message.reply_text(
            f"{feature.capitalize()} deletion is already **enabled**."
        )
    else:
        await set_deletion_feature(chat_id, feature, True)
        await message.reply_text(f"{feature.capitalize()} deletion is now **enabled**.")


# Command to disable story or forwarded deletion
@app.on_message(filters.command("disable_delete") & filters.group)
async def disable_delete(client, message):
    chat_id = message.chat.id
    feature = message.command[1] if len(message.command) > 1 else None

    if feature not in ["story", "forwarded"]:
        await message.reply_text("Usage: /disable_delete <story|forwarded>")
        return

    is_enabled = await is_deletion_enabled(chat_id, feature)

    if not is_enabled:
        await message.reply_text(
            f"{feature.capitalize()} deletion is already **disabled**."
        )
    else:
        await set_deletion_feature(chat_id, feature, False)
        await message.reply_text(
            f"{feature.capitalize()} deletion is now **disabled**."
        )


# Story Deletion
@app.on_message(filters.group)
async def delete_story(client, message):
    chat_id = message.chat.id

    # Check if story deletion is enabled
    if not await is_deletion_enabled(chat_id, "story"):
        return

    # Ensure from_user exists before proceeding
    if message.from_user is None:
        return  # Exit if there's no user attached to the message

    # Check if the message contains a story
    if message.story:
        try:
            # Get the sender's chat member status
            member = await client.get_chat_member(message.chat.id, message.from_user.id)

            # Check if the user is a regular member (not admin or owner)
            if member.status == ChatMemberStatus.MEMBER:
                # Attempt to delete the story message
                await message.delete()
                await message.reply_text(
                    "⛔ Stories are not allowed and have been deleted."
                )
                print(
                    f"Deleted story with ID: {message.story.id} from user: {message.from_user.id}"
                )
            else:
                print(
                    f"User {message.from_user.id} is an admin or owner. Story will not be deleted."
                )

        except (PeerIdInvalid, RPCError) as e:
            print(f"Failed to delete the story: {e}")
            await message.reply_text(
                "⚠️ Error occurred while trying to delete the story."
            )
        except MessageDeleteForbidden:
            print("Bot does not have permission to delete the story.")


# Forwarded Message Deletion
@app.on_message(filters.forwarded)
async def delete_forwarded(app, m):
    if m.chat is None or m.from_user is None:
        return  # Exit the function if they are None

    # Check if forwarded deletion is enabled
    if not await is_deletion_enabled(m.chat.id, "forwarded"):
        return

    try:
        chat_member = await app.get_chat_member(m.chat.id, m.from_user.id)
        su = chat_member.status

        if su == ChatMemberStatus.MEMBER:
            await m.delete()
    except MessageDeleteForbidden:
        print("Bot does not have permission to delete the message.")
    except Exception as e:
        print(f"An error occurred: {e}")
