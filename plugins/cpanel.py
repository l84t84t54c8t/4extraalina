from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from AlinaMusic.utils.database import set_channel, set_group, set_must
from pyrogram import Client, filters


@app.on_message(
    filters.command(["• گۆڕینی کەناڵی بۆت •", "گۆڕینی کەناڵی بۆت"], "") & SUDOERS
)
async def set_botch(client: Client, message):
    bot_username = app.username
    await message.reply_text("**لینکی کەناڵی نوێ بنێرە**")
    
    # Wait for the user's next message in the same chat
    response = await app.listen(message.chat.id, filters=filters.text)
    channel = response.text
    
    await set_channel(bot_username, channel)
    await message.reply_text("**بە سەرکەوتوویی کەناڵی بۆت گۆڕا -🖱️**")
    return


@app.on_message(
    filters.command(["• گۆڕینی گرووپی بۆت •", "گۆڕینی گرووپی بۆت"], "") & SUDOERS
)
async def set_botgr(client: Client, message):
    bot_username = app.username
    await message.reply_text("**لینکی گرووپی نوێ بنێرە**")
    
    # Wait for the user's next message in the same chat
    response = await app.listen(message.chat.id, filters=filters.text)
    group = response.text
    
    await set_group(bot_username, group)
    await message.reply_text("**بە سەرکەوتوویی گرووپی بۆت گۆڕا -🖱️**")
    return


@app.on_message(
    filters.command(
        ["• ناچالاککردنی جۆینی ناچاری •", "• چالاککردنی جۆینی ناچاری •"], ""
    )
    & SUDOERS
)
async def set_join_must(client: Client, message):
    bot_username = app.username
    m = message.command[0]
    await set_must(bot_username, m)
    
    if message.command[0] == "• ناچالاککردنی جۆینی ناچاری •":
        await message.reply_text("**بە سەرکەوتوویی جۆینی ناچاری ناچالاککرا -🖱️**")
    else:
        await message.reply_text("**بە سەرکەوتوویی جۆینی ناچاری چالاککرا -🖱️**")
    return
