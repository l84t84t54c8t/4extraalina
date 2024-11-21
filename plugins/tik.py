from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from AlinaMusic import app
import requests

# Regex to match only TikTok links
tiktok_regex = r"(https?://(?:www\.)?tiktok\.com/[\w\-/]+)"

@app.on_message(filters.regex(tiktok_regex))
async def Start(app, message):
    try:
        msg = message.text
        url = requests.get(f'https://tikwm.com/api/?url={msg}').json()
        music = url['data']['music']
        region = url['data']['region']
        tit = url['data']['title']
        vid = url['data']['play']
        ava = url['data']['author']['avatar']
        name = url['data']['music_info']['author']
        time = url['data']['duration']
        sh = url['data']['share_count']
        com = url['data']['comment_count']
        wat = url['data']['play_count']
        
        # Send photo with caption
        await app.send_photo(
            message.chat.id, ava,
            caption=(
                f"**✧ ¦ ناو : {name}\n"
                f"✧ ¦ وڵات : {region}\n\n"
                f"✧ ¦ ژمارەی بینەر : {wat}\n"
                f"✧ ¦ ژمارەی کۆمێنت : {com}\n"
                f"✧ ¦ ژمارەی شەیرەکان : {sh}\n"
                f"✧ ¦ درێژی ڤیدیۆ : {time}**"
            )
        )
        
        # Send video with title
        await app.send_video(
        message.chat.id,
        vid,
        caption=f"{tit}",
        reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=_["S_B_4"],
                            url=f"{SUPPORT_CHANNEL}",
                        )
                    ]
                ]
            ),
        )
    except Exception as e:
        print(f"Error: {e}")
