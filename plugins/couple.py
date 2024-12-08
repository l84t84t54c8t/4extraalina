import os
import random

from AlinaMusic import app
from config import BANNED_USERS, OWNER_ID
from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.permissions import adminsOnly

# Lock state variable (you can also use a database)
command_locked = False


@app.on_message(filters.command("lock_couples") & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def lock_couples_command(app, message):
    global command_locked
    command_locked = True
    await message.reply_text("The 'couples' command has been locked! 🔒")


@app.on_message(filters.command("unlock_couples") & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def unlock_couples_command(app, message):
    global command_locked
    command_locked = False
    await message.reply_text("The 'couples' command has been unlocked! 🔓")


@app.on_message(
    filters.command(
        ["couples", "couple", "kapl", "قل", "کەپل", "کەپڵ"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & ~BANNED_USERS
)
async def couples(app, message):
    global command_locked
    if command_locked:
        return await message.reply_text("This command is currently locked! 🔒")

    cid = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("**تەنیا لە گرووپ کارەکات😂🙂**")

    try:
        msg = await message.reply_text("**دوو ئاشقە شێتەکە دیاری دەکرێت😂🙂🫶🏻!**")
        list_of_users = []

        async for member in app.get_chat_members(message.chat.id, limit=50):
            if not member.user.is_bot and not member.user.is_deleted:
                list_of_users.append(member.user.id)

        if len(list_of_users) < 2:
            return await msg.edit("Not enough members to form a couple! 😢")

        c1_id = random.choice(list_of_users)
        c2_id = random.choice(list_of_users)
        while c1_id == c2_id:
            c2_id = random.choice(list_of_users)

        photo1 = (await app.get_chat(c1_id)).photo
        photo2 = (await app.get_chat(c2_id)).photo

        N1 = (await app.get_users(c1_id)).mention
        N2 = (await app.get_users(c2_id)).mention

        try:
            p1 = await app.download_media(photo1.big_file_id, file_name="pfp.png")
        except Exception:
            p1 = "assets/upic.png"
        try:
            p2 = await app.download_media(photo2.big_file_id, file_name="pfp1.png")
        except Exception:
            p2 = "assets/upic.png"

        OWNER = OWNER_ID[0] if isinstance(OWNER_ID, list) else OWNER_ID

        img1 = Image.open(p1)
        img2 = Image.open(p2)
        img = Image.open("assets/cppic.png")

        img1 = img1.resize((437, 437))
        img2 = img2.resize((437, 437))

        mask = Image.new("L", img1.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img1.size, fill=255)

        mask1 = Image.new("L", img2.size, 0)
        draw = ImageDraw.Draw(mask1)
        draw.ellipse((0, 0) + img2.size, fill=255)

        img1.putalpha(mask)
        img2.putalpha(mask1)

        img.paste(img1, (116, 160), img1)
        img.paste(img2, (789, 160), img2)

        img.save(f"test_{cid}.png")

        TXT = f"""**
کەپڵەکان دیاری کران 💍🌚 :
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
{N1} + {N2} = ❣️
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
پیرۆزە 😂🎉
**
"""
        await app.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        await message.reply_photo(
            f"test_{cid}.png",
            caption=TXT,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="👻 خاوەنی بۆت 👻", user_id=OWNER)]]
            ),
        )
        await msg.delete()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cleanup
        try:
            os.remove("pfp.png")
            os.remove("pfp1.png")
            os.remove(f"test_{cid}.png")
        except Exception:
            pass
