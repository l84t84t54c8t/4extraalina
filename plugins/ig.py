import requests
from pyrogram import Client, filters
from AlinaMusic import app

@app.on_message(filters.command(["ig", "instagram", "reel"]) & filters.text)
async def download_instagram_video(client, message):
    text = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else None

    if text and "instagram.com" in text:
        # Sending a loading message
        loading_message = await message.reply_text("**← دادەبەزێت کەمێک چاوەڕێ بکە ...!**")
        
        # Prepare data for the API
        json_data = {"url": text}
        api_url = "https://insta.savetube.me/downloadPostVideo"

        try:
            # Making the API request
            response = requests.post(api_url, json=json_data)
            response_data = response.json()
            
            # Check if the API returned a valid URL
            if "url" in response_data and response_data["url"]:
                video_url = response_data["url"]
                
                # Sending the video
                await client.send_video(
                    chat_id=message.chat.id,
                    video=video_url,
                    caption="- @IQMCBOT .",
                )
            else:
                await message.reply_text("**هیچ شتێک نەدۆزراوە**")
        except Exception as e:
            await message.reply_text(f"**هەڵە: {e}**")
        finally:
            # Deleting the loading message
            await loading_message.delete()
    else:
        await message.reply_text("**تکایە بەستەری ئینستاگرام بە دروستی بنێرە**")
