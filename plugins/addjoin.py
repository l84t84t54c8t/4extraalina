from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from AlinaMusic.misc import SUDOERS
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

addjoin = mongodb.addjoin

# Default value for join_required in DB
if addjoin.count_documents({}) == 0:
    addjoin.insert_one({"join_required": True})


@app.on_message(filters.text & filters.private)
async def handle_commands(client: Client, message: Message):
    # Restrict access to SUDOERS only
    if message.from_user.id not in SUDOERS:
        await message.reply(
            "⛔ این دستور فقط برای مدیران مجاز است.\n⛔ This command is restricted to SUDOERS."
        )
        return

    text = message.text.strip().lower()

    # Access forced channels from DB
    forced_channels = [channel["channel_id"] for channel in addjoin.find()]

    # Handle adding a join channel
    if text in ["اضافه کردن جوین", "add join"]:
        reply = await message.chat.ask(
            "کانال را وارد کنید:\nEnter the channel:",
            filters=filters.text & filters.user(message.from_user.id),
            reply_to_message_id=message.id,
        )
        channel_id = reply.text.strip()

        if addjoin.count_documents({"channel_id": channel_id}) == 0:
            addjoin.insert_one({"channel_id": channel_id})
            await message.reply(
                f"کانال {channel_id} به لیست جوین اجباری اضافه شد.\nChannel {channel_id} has been added to the forced join list."
            )
        else:
            await message.reply(
                "این کانال قبلاً در لیست وجود دارد.\nThis channel is already in the list."
            )

    # Show join channels
    elif text in ["نمایش لیست جوین", "show join list"]:
        if forced_channels:
            buttons = [
                [
                    InlineKeyboardButton(
                        text="عضویت در کانال / Join Channel",
                        url=f"https://t.me/{channel.replace('@', '')}",
                    )
                ]
                for channel in forced_channels
            ]
            buttons.append(
                [InlineKeyboardButton("عضو شدم / Joined", callback_data="check_join")]
            )
            await message.reply(
                "لیست کانال‌های جوین اجباری:\nList of forced join channels:",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await message.reply(
                "هیچ کانالی در لیست وجود ندارد.\nNo channels in the list."
            )

    # Handle removing a join channel
    elif text in ["حذف جوین", "remove join"]:
        reply = await message.chat.ask(
            "کانالی که می‌خواهید حذف کنید را وارد کنید:\nEnter the channel to remove:",
            filters=filters.text & filters.user(message.from_user.id),
            reply_to_message_id=message.id,
        )
        channel_id = reply.text.strip()

        if addjoin.count_documents({"channel_id": channel_id}) > 0:
            addjoin.delete_one({"channel_id": channel_id})
            await message.reply(
                f"کانال {channel_id} از لیست حذف شد.\nChannel {channel_id} has been removed from the list."
            )
        else:
            await message.reply(
                "این کانال در لیست وجود ندارد.\nThis channel is not in the list."
            )

    # Enable forced join
    elif text in ["جوین روشن", "enable join"]:
        addjoin.update_one({}, {"$set": {"join_required": True}})
        await message.reply("جوین اجباری فعال شد.\nForced join has been enabled.")

    # Disable forced join
    elif text in ["جوین خاموش", "disable join"]:
        addjoin.update_one({}, {"$set": {"join_required": False}})
        await message.reply("جوین اجباری غیرفعال شد.\nForced join has been disabled.")


@app.on_callback_query(filters.regex("check_join"))
async def check_user_join(client: Client, callback_query):
    join_required = addjoin.find_one().get("join_required", True)

    if join_required and addjoin.count_documents({}) > 0:
        user_id = callback_query.from_user.id

        not_joined = []
        for channel in addjoin.find():
            try:
                await client.get_chat_member(channel["channel_id"], user_id)
            except BaseException:
                not_joined.append(channel["channel_id"])

        if not not_joined:
            await callback_query.message.reply(
                "😎 عالی! حالا می‌تونی از ربات استفاده کنی!\nAwesome! You can now use the bot!"
            )
        else:
            await callback_query.message.reply(
                "🤨 هنوز عضو همه کانال‌ها نشدی!\nYou haven't joined all the channels yet!"
            )


@app.on_message(filters.private, group=-3)
async def enforce_join(client: Client, message: Message):
    join_required = addjoin.find_one().get("join_required", True)

    if join_required and addjoin.count_documents({}) > 0:

        not_joined = []
        for channel in addjoin.find():
            try:
                await client.get_chat_member(
                    channel["channel_id"], message.from_user.id
                )
            except BaseException:
                not_joined.append(channel["channel_id"])

        if not_joined:
            buttons = [
                [
                    InlineKeyboardButton(
                        text="عضویت در کانال / Join Channel",
                        url=f"https://t.me/{channel.replace('@', '')}",
                    )
                ]
                for channel in not_joined
            ]
            buttons.append(
                [InlineKeyboardButton("عضو شدم / Joined", callback_data="check_join")]
            )
            await message.reply(
                "برای استفاده از ربات، ابتدا در کانال‌های زیر عضو شوید:\nTo use the bot, join the following channels first:",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return
