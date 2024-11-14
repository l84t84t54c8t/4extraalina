from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from pyrogram import filters
from yt_dlp import YoutubeDL

# Path to your cookies file
COOKIES_FILE = "cookies/cookies.txt"

# Function to load cookies from the cookies file
def load_cookies(file_path):
    cookies = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("#") or not line.strip():  # Ignore comments and empty lines
                continue
            cookies.append(line.strip())
    return cookies

# Function to check if a specific cookie is valid
def check_cookie_validity(cookie):
    try:
        ydl_opts = {
            "quiet": True,
            "cookiejar": cookie  # Set this to the specific cookie to test
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Test with a sample video URL
            video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            info = ydl.extract_info(video_url, download=False)
            if info:
                return True  # Cookie is valid
    except Exception as e:
        print(f"Error with cookie {cookie}: {e}")
    
    return False  # Cookie is invalid or expired

# Function to check all cookies in the file
def check_all_cookies():
    cookies = load_cookies(COOKIES_FILE)
    valid_cookies = []

    # Test each cookie
    for idx, cookie in enumerate(cookies):
        print(f"Checking cookie {idx + 1}...")
        if check_cookie_validity(cookie):
            valid_cookies.append(cookie)

    return valid_cookies

# Pyrogram bot command to check cookies validity
@app.on_message(filters.command("check_cookies") & SUDOERS)
async def check_cookies_command(client, message):
    valid_cookies = check_all_cookies()
    
    if valid_cookies:
        await message.reply_text(f"✅ The following cookies are valid:\n{', '.join(valid_cookies)}")
    else:
        await message.reply_text("❌ No valid cookies found. Switching to OAuth2 is recommended.")

