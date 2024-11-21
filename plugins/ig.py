import os
import shutil  # To clean up the directory

import instaloader
from AlinaMusic import app
from pyrogram import filters

# Create an Instaloader instance
loader = instaloader.Instaloader()

# Command handler to download Instagram video


@app.on_message(filters.command(["download_instagram"]))
async def download_instagram(client, message):
    try:
        # Check if a URL was provided
        if len(message.command) < 2:
            await message.reply_text(
                "Please provide an Instagram post URL.\nUsage: `/download_instagram <url>`"
            )
            return

        # Extract URL from the command
        url = message.command[1]

        # Validate URL
        if not "instagram.com" in url:
            await message.reply_text(
                "Invalid URL. Please provide a valid Instagram post URL."
            )
            return

        await message.reply_text("Downloading the Instagram video... Please wait.")

        # Extract shortcode from URL
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if not post.is_video:
            await message.reply_text("The provided URL does not contain a video.")
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
            await message.reply_text("Failed to locate the downloaded video.")
            return

        # Send the video to the user
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file,
            caption="Here is your downloaded Instagram video!",
        )

        # Clean up the downloads folder
        shutil.rmtree(target_folder)

    except Exception as e:
        await message.reply_text(
            f"An error occurred while processing your request: {e}"
        )
        print(f"Error: {e}")
