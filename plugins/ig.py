import re

import requests
from AlinaMusic import app
from pyrogram import filters

# Regex pattern to match Instagram URLs
instagram_url_pattern = r"(https?://(?:www\.)?instagram\.com/[-a-zA-Z0-9@:%._\+~#=]{2,256}/[-a-zA-Z0-9@:%._\+~#=]+)"


@app.on_message(filters.regex(instagram_url_pattern))
async def download_instagram_video(client, message):
    try:
        # Extract the Instagram link from the message
        link = re.search(instagram_url_pattern, message.text).group(1)

        # Make a request to fetch the video
        json_data = {"url": link}
        response = requests.post(
            "https://insta.savetube.me/downloadPostVideo", json=json_data
        ).json()

        # Extract video and thumbnail
        thu = response["post_video_thumbnail"]
        video = response["post_video_url"]

        # Send thumbnail as a photo
        await message.reply_photo(
            thu, caption="*ڤیدیۆکە دابەزاندنی دەستپێدەکات...*\n\n⧉• 𝙎𝙊𝙐𝙍𝘾𝞝 𝙄𝙌 - @MGIMT"
        )

        # Send video directly
        caption = (
            "**بە سەرکەوتوویی داگرترا لەلایەن :\n**"
            "**⧉• 𝙎𝙊𝙐𝙍𝘾𝞝 𝙄𝙌 - @MGIMT\n\n**"
            "**@EHS4SS - جۆینی ئەم کەناڵە شازە بکە♥️⚡️**"
        )
        await app.send_video(
            message.chat.id, video, caption=caption, parse_mode="markdown"
        )

    except Exception as e:
        print(f"Error: {e}")
        await message.reply("**ببورە، هەڵەیەک ڕوویدا! تکایە دوبارە هەوڵدەوە.**")
