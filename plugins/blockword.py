from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.core.mongo import mongodb
from pyrogram import Client, filters

abuse_words_db = mongodb.abuse_words

abuse_cache = []


async def load_abuse_cache():
    global abuse_cache
    abuse_cache = [
        entry["word"] for entry in await abuse_words_db.find().to_list(length=None)
    ]


async def add_abuse_word(word: str):
    global abuse_cache
    if word not in abuse_cache:
        await abuse_words_db.insert_one({"word": word})
        abuse_cache.append(word)


async def is_abuse_present(text: str):
    global abuse_cache
    if not abuse_cache:
        await load_abuse_cache()
    return any(word in text.lower() for word in abuse_cache)


@app.on_message(filters.command("blockword") & SUDOERS)
async def block_word(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:** `/block <word>`\nAdd a word to the abuse list."
            )
            return
        new_word = message.command[1].lower()
        await add_abuse_word(new_word)
        await message.reply_text(f"**Word '{new_word}' added to abuse list!**")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("unblockword") & SUDOERS)
async def unblock_word(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:** `/unblock <word>`\nRemove a word from the abuse list."
            )
            return
        word_to_remove = message.command[1].lower()
        global abuse_cache
        if word_to_remove in abuse_cache:
            await abuse_words_db.delete_one({"word": word_to_remove})
            abuse_cache.remove(word_to_remove)
            await message.reply_text(
                f"**Word '{word_to_remove}' removed from abuse list!**"
            )
        else:
            await message.reply_text(
                f"**Word '{word_to_remove}' is not in the abuse list.**"
            )
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("blockedw") & SUDOERS)
async def list_blocked_words(client: Client, message: Message):
    try:
        global abuse_cache
        if not abuse_cache:
            await load_abuse_cache()
        if abuse_cache:
            blocked_words = ", ".join(abuse_cache)
            await message.reply_text(f"**Blocked Words:**\n{blocked_words}")
        else:
            await message.reply_text("**No blocked words found.**")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
