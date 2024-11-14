from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from AlinaMusic.misc import SUDOERS
from AlinaMusic import app
# Path to your cookies file
COOKIES_FILE = "cookies/cookies.txt"

# Check if cookies file is valid function
def check_cookies():
    ytdl_opts = {
        "cookiefile": COOKIES_FILE,
        "quiet": True,
    }
    
    try:
        with YoutubeDL(ytdl_opts) as ydl:
            # Attempt to access a video with the cookies
            ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
        return True  # If successful, cookies are valid
    except Exception as e:
        print("Cookies file check failed:", e)
        return False  # If there's an error, cookies are likely invalid or expired

# Command to check cookies in your bot
@app.on_message(filters.command("check_cookies") & )
async def check_cookies_command(client, message):
    if check_cookies():
        await message.reply_text("✅ The cookies file is valid and working!")
    else:
        await message.reply_text("❌ The cookies file is invalid or expired. Switching to OAuth2 is recommended.")
