from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

# List of forced join channels and join status
forced_channels = []
join_required = True


@app.on_message(filters.private & filters.command(["addjoin", "زیادکردنی_جۆین"]))
async def add_join(client: Client, message: Message):
    global forced_channels

    # Restrict access to SUDOERS only
    if message.from_user.id not in SUDOERS:
        await message.reply(
            "⛔ این دستور فقط برای مدیران مجاز است.\n⛔ This command is restricted to SUDOERS."
        )
        return

    await message.reply(
        "لینک یا آیدی عددی کانال را ارسال کنید:\nSend the link or numeric ID of the channel:"
    )
    response = await app.listen(message.chat.id, timeout=60)
    if response and response.text:
        channel_id = response.text.strip()

        if channel_id not in forced_channels:
            forced_channels.append(channel_id)
            await message.reply(
                f"کانال {channel_id} به لیست جوین اجباری اضافه شد.\nChannel {channel_id} has been added to the forced join list."
            )
        else:
            await message.reply(
                "این کانال قبلاً در لیست وجود دارد.\nThis channel is already in the list."
            )
    else:
        await message.reply("⛔ زمان برای ارسال پاسخ تمام شد.\n⛔ Timeout while waiting for your response.")


@app.on_message(filters.private & filters.command(["showjoin", "جۆینن"]))
async def show_join_list(client: Client, message: Message):
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


@app.on_message(filters.private & filters.command(["removejoin", "حذف_جوین"]))
async def remove_join(client: Client, message: Message):
    global forced_channels

    # Restrict access to SUDOERS only
    if message.from_user.id not in SUDOERS:
        await message.reply(
            "⛔ این دستور فقط برای مدیران مجاز است.\n⛔ This command is restricted to SUDOERS."
        )
        return

    await message.reply(
        "لینک یا آیدی کانالی که می‌خواهید حذف کنید را ارسال کنید:\nSend the link or ID of the channel to remove:"
    )
    response = await app.listen(message.chat.id, timeout=60)
    if response and response.text:
        channel_id = response.text.strip()

        if channel_id in forced_channels:
            forced_channels.remove(channel_id)
            await message.reply(
                f"کانال {channel_id} از لیست حذف شد.\nChannel {channel_id} has been removed from the list."
            )
        else:
            await message.reply(
                "این کانال در لیست وجود ندارد.\nThis channel is not in the list."
            )
    else:
        await message.reply("⛔ زمان برای ارسال پاسخ تمام شد.\n⛔ Timeout while waiting for your response.")


@app.on_callback_query(filters.regex("check_join"))
async def check_user_join(client: Client, callback_query: CallbackQuery):
    global forced_channels

    user_id = callback_query.from_user.id
    not_joined = []

    for channel in forced_channels:
        try:
            await client.get_chat_member(channel, user_id)
        except Exception:
            not_joined.append(channel)

    if not not_joined:
        await callback_query.answer(
            "😎 عالی! حالا می‌تونی از ربات استفاده کنی!\nAwesome! You can now use the bot!",
            show_alert=True,
        )
    else:
        await callback_query.answer(
            "🤨 هنوز عضو همه کانال‌ها نشدی!\nYou haven't joined all the channels yet!",
            show_alert=True,
        )


@app.on_message(filters.private, group=-3)
async def enforce_join(client: Client, message: Message):
    if join_required and forced_channels:
        not_joined = []

        for channel in forced_channels:
            try:
                await client.get_chat_member(channel, message.from_user.id)
            except Exception:
                not_joined.append(channel)

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
