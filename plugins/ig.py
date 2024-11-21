import requests
from AlinaMusic import app
from pyrogram import filters
from pyrogram import Client, filters
import instaloader
import os

# Create an Instaloader instance
loader = instaloader.Instaloader()

# Command handler to download Instagram video
@app.on_message(filters.command(["download_instagram"]))
async def download_instagram(client, message):
    try:
        # Check if a URL was provided
        if len(message.command) < 2:
            await message.reply_text("Please provide an Instagram post URL.\nUsage: `/download_instagram <url>`")
            return

        # Extract URL
        url = message.command[1]
        
        # Download the video
        await message.reply_text("Downloading the Instagram video... Please wait.")
        post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
        
        if not post.is_video:
            await message.reply_text("This URL does not contain a video.")
            return
        
        # Save the video
        video_file = f"{post.shortcode}.mp4"
        loader.download_post(post, target="downloads")
        video_path = os.path.join("downloads", video_file)

        # Send the video to the user
        await client.send_video(chat_id=message.chat.id, video=video_path)
        await message.reply_text("Here is your downloaded Instagram video!")
        
        # Clean up
        os.remove(video_path)
    except Exception as e:
        await message.reply_text(f"Failed to download video: {e}")
        print(e)
