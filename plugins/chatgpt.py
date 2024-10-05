import openai
from AlinaMusic import app
from config import BANNED_USERS
from pyrogram import Client, filters
from pyrogram.types import Message

# Set your OpenAI API Key
openai.api_key = "sk-svcacct-Iqac6w1z7uS8YvcGBQ0pAAOYXfPM4zUVNS1wgy74mTpHTLJb2v-U_zQtfDmkCaT3BlbkFJlbH6qgPs5XQsrL30rbAkvC2Ko7nd-eiWUb6YysPsNgEbiER56Q3SdA744Sbl4A"  # Replace with your OpenAI API key


# Function to generate AI responses using OpenAI Chat API
def get_ai_chat_response(user_message):
    try:
        # Updated API usage
        response = openai.chat_completions.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" if you prefer
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
