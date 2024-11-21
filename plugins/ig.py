import re

import requests
from AlinaMusic import app
import requests
from pyrogram import Client, filters

# Regex pattern to match Instagram URLs
instagram_url_pattern = r"(https?://(?:www\.)?instagram\.com/[-a-zA-Z0-9@:%._\+~#=]{2,256}/[-a-zA-Z0-9@:%._\+~#=]+)"

@app.on_message(filters.regex(instagram_url_pattern))
async def down(app, message):
    try:
        link = message.text
        json_data = {'url': link}
        response = requests.post('https://insta.savetube.me/downloadPostVideo', json=json_data).json()

        # Extract video and thumbnail
        thu = response['post_video_thumbnail']
        video = response['post_video_url']

        # Send thumbnail as a photo
        await message.reply_photo(thu, caption="**← کەمێک چاوەڕێ بکە .. ڤیدیۆ دادەبەزێت ...\n⧉• لەلایەن : @IQMCBOT**")

        # Send video directly
        caption = (
            "**✅꒐ بە سەرکەوتوویی داگرترا\n🎸꒐ بۆتی @IQMCBOT**"
        )
        await app.send_video(message.chat.id, video, caption=caption)

    except Exception as e:
        print(f"Error: {e}")
        await message.reply("**لینك هەڵەیە ئەزیزم**")
