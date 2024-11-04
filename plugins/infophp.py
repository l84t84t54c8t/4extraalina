from typing import Optional, Union

from AlinaMusic import app as Hiroko
from PIL import Image, ImageDraw, ImageFont
from pyrogram import enums
from pyrogram.types import *
from string.filters import command

# Function to get font and resize text


def get_font(font_size, font_path):
    return ImageFont.truetype(font_path, font_size)


def resize_text(text_size, text):
    return (text[:text_size] + "...").upper() if len(text) > text_size else text.upper()


async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None,
):
    bg = Image.open(bg_path)

    if profile_path:
        img = Image.open(profile_path)
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), img.size], 0, 360, fill=255)

        circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        resized = circular_img.resize((400, 400))
        bg.paste(resized, (440, 160), resized)

    img_draw = ImageDraw.Draw(bg)

    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46, font_path),
        fill=(255, 255, 255),
    )

    path = f"downloads/userinfo_img_{user_id}.png"
    bg.save(path)
    return path


# Function to get user status
async def userstatus(user_id):
    try:
        user = await Hiroko.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "User was seen recently."
        elif x == enums.UserStatus.LAST_WEEK:
            return "User was seen last week."
        elif x == enums.UserStatus.LONG_AGO:
            return "User was seen long ago."
        elif x == enums.UserStatus.OFFLINE:
            return "User is offline."
        elif x == enums.UserStatus.ONLINE:
            return "User is online."
    except Exception as e:
        print(f"Error fetching user status: {e}")
        return "**هەندێك هەڵە ڕوویدا!**"


# Command handler for /info and /userinfo
@Hiroko.on_message(command(["/info", "/userinfo", "info", "id", "ا", "ئایدی"]))
async def userinfo(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        # Determine user ID based on the context
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            user_id = message.command[1]

        user_info = await Hiroko.get_chat(user_id)
        user = await Hiroko.get_users(user_id)
        status = await userstatus(user.id)

        # Safely retrieve user information
        id = user_info.id
        name = user_info.first_name or "نەناسراو"
        username = user_info.username or "نییەتی"
        mention = user.mention or "بەردەست نییە"
        bio = user_info.bio or "بەردەست نییە"

        # Check if user has a profile photo
        if user.photo and user.photo.big_file_id:
            photo = await Hiroko.download_media(user.photo.big_file_id)
            welcome_photo = await get_userinfo_img(
                bg_path="assets/userinfo.png",
                font_path="assets/hiroko.ttf",
                user_id=user_id,
                profile_path=photo,
            )
        else:
            # Use the background image when there is no profile photo
            welcome_photo = await get_userinfo_img(
                bg_path="assets/userinfo.png",
                font_path="assets/hiroko.ttf",
                user_id=user_id,
            )

        await message.reply_photo(
            photo=welcome_photo,
            caption=f"""**زانیاری بەڕێزت♥🙇🏻‍♂️\n
 ✧ ¦ نـاوت ← {mention}
 ✧ ¦ یـوزەرت ← @{username}
 ✧ ¦ ئـایدی ← `{id}`
 ✧ ¦ ئـەکـتـیـڤـی بـەکـارهـێـنـەر ←\n`{status}`\n
 ✧ ¦ بـایـۆ ← {bio}\n\n
            **""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            name, url=f"https://t.me/{message.from_user.username}"
                        )
                    ],
                ]
            ),
        )

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
