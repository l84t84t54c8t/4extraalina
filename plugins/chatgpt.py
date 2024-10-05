import openai
from AlinaMusic import app
from config import BANNED_USERS
from pyrogram import Client, filters
from pyrogram.types import Message

# Set your OpenAI API Key
openai.api_key = "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"  # Replace with your OpenAI API key


# Function to generate AI responses using OpenAI Chat API
def get_ai_chat_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
        )
        return response["choices"][0]["message"][
            "content"
        ].strip()  # Get the chat response
    except Exception as e:
        return f"Error: {e}"


# AI-powered chat feature: Respond to /gpt command followed by a user question
@app.on_message(filters.command(["chatgpt", "ai", "ask", "gpt"]) & ~BANNED_USERS)
async def gpt_command(client: Client, message: Message):
    user_message = message.text[len("/gpt ") :]  # Extract the message after "/gpt "

    if not user_message.strip():
        await message.reply_text(
            "**نموونە :**\n\n`/ai write simple website code using html css, js?`"
        )
        return

    ai_response = get_ai_chat_response(
        user_message
    )  # Get AI-generated response from GPT
    await message.reply_text(ai_response)  # Send the AI response to the user


__MODULE__ = "CʜᴀᴛGᴘᴛ"
__HELP__ = """
/advice - ɢᴇᴛ ʀᴀɴᴅᴏᴍ ᴀᴅᴠɪᴄᴇ ʙʏ ʙᴏᴛ
/ai [ǫᴜᴇʀʏ] - ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ᴄʜᴀᴛɢᴘᴛ's ᴀɪ
/gemini [ǫᴜᴇʀʏ] - ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ɢᴏᴏɢʟᴇ's ɢᴇᴍɪɴɪ ᴀɪ
/bard [ǫᴜᴇʀʏ] -ᴀsᴋ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ ᴡɪᴛʜ ɢᴏᴏɢʟᴇ's ʙᴀʀᴅ ᴀɪ"""
