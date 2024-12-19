from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# List of forced join channels and join status
forced_channels = []
join_required = True


@app.on_message(filters.text & filters.private)
async def handle_commands(client: Client, message: Message):
    global join_required

    # Restrict access to SUDOERS only
    if message.from_user.id not in SUDOERS:
        await message.reply(
            "⛔ ئەم فەرمانە تەنها بۆ بەڕێوەبەرە تایبەتیەکانە.\n⛔ This command is restricted to SUDOERS."
        )
        return

    text = message.text.strip().lower()

    if text in ["زیادکردنی جۆین", "add join"]:
        reply = await message.chat.ask(
            "کەناڵەکانەوە بنووسە:\nEnter the channel:",
            filters=filters.text & filters.user(message.from_user.id),
            reply_to_message_id=message.id,
        )
        channel_id = reply.text.strip()

        if channel_id not in forced_channels:
            forced_channels.append(channel_id)
            await message.reply(
                f"کەناڵ {channel_id} بۆ لیست جوین ئەجباری زیاد کرا.\nChannel {channel_id} has been added to the forced join list."
            )
        else:
            await message.reply(
                "ئەم کەناڵە پێشتر بە لیستەکە هەیە.\nThis channel is already in the list."
            )

    elif text in ["لیستی جۆین", "show join list"]:
        if forced_channels:
            buttons = [
                [
                    InlineKeyboardButton(
                        text="جۆین بە / Join Channel",
                        url=f"https://t.me/{channel.replace('@', '')}",
                    )
                ]
                for channel in forced_channels
            ]
            buttons.append(
                [InlineKeyboardButton("من جۆینم / Joined", callback_data="check_join")]
            )
            await message.reply(
                "لیستی کەناڵەکانە جوین ئەجباری:\nList of forced join channels:",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            await message.reply("هیچ کەناڵێکە نیە.\nNo channels in the list.")

    elif text in ["سڕینەوەی جۆین", "remove join"]:
        reply = await message.chat.ask(
            "کەناڵی کە دەتەوێت بسڕیتەوە بنووسە:\nEnter the channel to remove:",
            filters=filters.text & filters.user(message.from_user.id),
            reply_to_message_id=message.id,
        )
        channel_id = reply.text.strip()

        if channel_id in forced_channels:
            forced_channels.remove(channel_id)
            await message.reply(
                f"کەناڵ {channel_id} لە لیستەکە سڕایەوە.\nChannel {channel_id} has been removed from the list."
            )
        else:
            await message.reply(
                "ئەم کەناڵە لە لیستەکە نیە.\nThis channel is not in the list."
            )

    elif text in ["چالاککردنی جۆین", "enable join"]:
        join_required = True
        await message.reply("جوین ئەجباری چالاک بووە.\nForced join has been enabled.")

    elif text in ["ناچالاککردنی جۆین", "disable join"]:
        join_required = False
        await message.reply(
            "جوین ئەجباری تەواو نەبووە.\nForced join has been disabled."
        )


@app.on_callback_query(filters.regex("check_join"))
async def check_user_join(client: Client, callback_query):
    if join_required and forced_channels:
        user_id = callback_query.from_user.id

        not_joined = []
        for channel in forced_channels:
            try:
                await client.get_chat_member(channel, user_id)
            except BaseException:
                not_joined.append(channel)

        if not not_joined:
            await callback_query.message.reply(
                "😎 باشە! ئێستا دەتوانیت بۆت بەکاربهێنیت!\nAwesome! You can now use the bot!"
            )
        else:
            await callback_query.message.reply(
                "🤨 جۆینی کەناڵت نەکرددوە!\nYou haven't joined all the channels yet!"
            )


@app.on_message(filters.private, group=-3)
async def enforce_join(client: Client, message: Message):
    if join_required and forced_channels:

        not_joined = []
        for channel in forced_channels:
            try:
                await client.get_chat_member(channel, message.from_user.id)
            except BaseException:
                not_joined.append(channel)

        if not_joined:
            buttons = [
                [
                    InlineKeyboardButton(
                        text="بەشداریکردن لە کەناڵ / Join Channel",
                        url=f"https://t.me/{channel.replace('@', '')}",
                    )
                ]
                for channel in not_joined
            ]
            buttons.append(
                [InlineKeyboardButton("من جۆینم / Joined", callback_data="check_join")]
            )
            await message.reply(
                "بۆ بەکارهێنانی بۆت، پێویستە لە کەناڵ بیت:\nTo use the bot, join the following channels first:",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return
