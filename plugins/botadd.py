import random

from AlinaMusic import app
from AlinaMusic.utils.database import delete_served_chat, get_assistant
from config import LOG_GROUP_ID
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

photo = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
    "https://graph.org/file/9340f44e4a181b18ac663.jpg",
    "https://graph.org/file/50037e072302b4eff55ba.jpg",
    "https://graph.org/file/39f39cf6c6c68170f6bf2.jpg",
    "https://graph.org/file/abf9931642773bc27ad7f.jpg",
    "https://graph.org/file/60764ec9d2b1fda50c2d1.jpg",
    "https://graph.org/file/a90c116b776c90d58f5e8.jpg",
    "https://graph.org/file/b2822e1b60e62caa43ceb.jpg",
    "https://graph.org/file/84998ca9871e231df0897.jpg",
    "https://graph.org/file/6c5493fd2f6c403486450.jpg",
    "https://graph.org/file/9dd91a4a794f15e5dadb3.jpg",
    "https://graph.org/file/0a2fb6e502f6c9b6a04ac.jpg",
    "https://graph.org/file/774380facd73524f27d26.jpg",
]


@app.on_message(filters.new_chat_members, group=-10)
async def join_watcher(_, message):
    try:
        userbot = await get_assistant(message.chat.id)
        chat = message.chat
        for members in message.new_chat_members:
            if members.id == app.id:
                count = await app.get_chat_members_count(chat.id)
                link = await app.export_chat_invite_link(message.chat.id)
                username = (
                    message.chat.username if message.chat.username else "گرووپی تایبەت"
                )
                msg = (
                    f"**📝 بۆتی گۆرانی زیادکرا بۆ گرووپ\n\n**"
                    f"**____________________________________\n\n**"
                    f"**📌 ناوی گرووپ : {message.chat.title}\n**"
                    f"**🍂 ئایدی گرووپ :** `{message.chat.id}`\n"
                    f"**🛰 بەستەری گرووپ: [گرووپ]({link})\n**"
                    f"**🔐 یوزەری گرووپ: @{username}\n**"
                    f"**📈 ژماری ئەندام : {count}\n**"
                    f"**🤔 زیادکرا لەلایەن : {message.from_user.mention}**"
                )
                await app.send_photo(
                    LOG_GROUP_ID,
                    photo=random.choice(photo),
                    caption=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    f"😍 زیادکرا لەلایەن 😍",
                                    url=f"tg://openmessage?user_id={message.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )
                await add_served_chat(message.chat.id)
                # await userbot.join_chat(link)

    except Exception as e:
        print(f"Error: {e}")


@app.on_message(filters.left_chat_member, group=-12)
async def on_left_chat_member(_, message: Message):
    try:
        userbot = await get_assistant(message.chat.id)

        left_chat_member = message.left_chat_member
        if left_chat_member and left_chat_member.id == (await app.get_me()).id:
            remove_by = (
                message.from_user.mention
                if message.from_user
                else "بەکارهێنەری نەناسراو"
            )
            chat = message.chat  # Retrieve the chat object here
            title = chat.title
            username = f"@{chat.username}" if chat.username else "گرووپی تایبەت"
            # Check if the group has a photo
            if chat.photo:
                photo_file = await app.download_media(chat.photo.big_file_id)
            else:
                # Select a random photo from the list if no group photo exists
                photo_file = random.choice(photo)

            chat_id = chat.id
            left = f"<b>✫ #دەرکردنی_بۆت ✫\n\nناوی گرووپ : {title}\n\nئایدی گرووپ : {chat_id}\n\nدەرکرا لەلایەن : {remove_by}\n\nبۆتی : @{app.username}</b>"
            await app.send_photo(
                LOG_GROUP_ID,
                photo=photo_file,
                caption=left,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"نوێکارییەکانی ئەلینا 🍻",
                                url=f"https://t.me/MGIMT",
                            )
                        ]
                    ]
                ),
            )
            await delete_served_chat(chat_id)
            await userbot.leave_chat(chat_id)
    except Exception as e:
        print(f"Error: {e}")
