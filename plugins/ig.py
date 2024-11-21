import os
import shutil  # To clean up the directory
import instaloader
from AlinaMusic import app
from pyrogram import filters

# Create an Instaloader instance
loader = instaloader.Instaloader()

# Regex to match Instagram URLs
instagram_url_pattern = r"(https?://(?:www\.)?instagram\.com/[-a-zA-Z0-9@:%._\+~#=]{2,256}/[-a-zA-Z0-9@:%._\+~#=]+)"

# Handler to download Instagram video via link
@app.on_message(filters.regex(instagram_url_pattern))
async def download_instagram(client, message):
    try:
        # Extract the URL from the message
        url = message.matches[0].group(0)

        await message.reply_text("**← کەمێک چاوەڕێ بکە .. ڤیدیۆ دادەبەزێت ...**")

        # Extract shortcode from URL
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if not post.is_video:
            await message.reply_text("**ئەو لینکەی بەمنت داوە ڤیدیۆ نییە**")
            return

        # Download the video to a target folder
        target_folder = "downloads"
        loader.download_post(post, target=target_folder)

        # Locate the video file in the downloaded folder
        video_file = None
        for file in os.listdir(target_folder):
            if file.endswith(".mp4"):
                video_file = os.path.join(target_folder, file)
                break

        if not video_file:
            await message.reply_text("**شکستی هێنا لە دۆزینەوەی ڤیدیۆکە**")
            return

        # Send the video to the user
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file,
            caption="**✅ ꒐ بە سەرکەوتوویی داگرترا\n🎸 ꒐ @IQMCBOT**",
        )

        # Clean up the downloads folder
        shutil.rmtree(target_folder)

    except Exception as e:
        await message.reply_text(
            f"An error occurred while processing your request: {e}"
        )
        print(f"Error: {e}")
