import os
import shutil  # To clean up the directory

import instaloader
from AlinaMusic import app
from pyrogram import filters

# Create an Instaloader instance
loader = instaloader.Instaloader()

# Regex to match Instagram URLs
instagram_url_pattern = r"(https?://(?:www\.)?instagram\.com/[-a-zA-Z0-9@:%._\+~#=]{2,256}/[-a-zA-Z0-9@:%._\+~#=]+)"

# Login credentials for Instagram
USERNAME = "xv.7amo"
PASSWORD = "7amo754531@##@"

# Log in to Instagram
try:
    loader.login(USERNAME, PASSWORD)
except instaloader.exceptions.BadCredentialsException:
    print("Invalid Instagram credentials. Please check your username and password.")


@app.on_message(filters.regex(instagram_url_pattern))
async def download_instagram(client, message):
    try:
        url = message.matches[0].group(0)
        await message.reply_text("Downloading the Instagram video... Please wait.")

        # Extract shortcode
        shortcode = url.split("/")[-2]

        # Authenticate and fetch post
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if not post.is_video:
            await message.reply_text("The provided URL does not contain a video.")
            return

        # Proceed with downloading
        target_folder = "downloads"
        loader.download_post(post, target=target_folder)

        video_file = None
        for file in os.listdir(target_folder):
            if file.endswith(".mp4"):
                video_file = os.path.join(target_folder, file)
                break

        if not video_file:
            await message.reply_text("Failed to locate the downloaded video.")
            return

        await client.send_video(
            chat_id=message.chat.id,
            video=video_file,
            caption="Here is your downloaded Instagram video!",
        )
        shutil.rmtree(target_folder)

    except instaloader.exceptions.LoginRequiredException:
        await message.reply_text(
            "Authentication required to access this post. Please update the bot with valid credentials."
        )
    except Exception as e:
        await message.reply_text(
            f"An error occurred while processing your request: {e}"
        )
        print(f"Error: {e}")
