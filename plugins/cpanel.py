from AlinaMusic import app
from AlinaMusic.misc import SUDOERS
from config import OWNER_ID
from pyrogram import filters

from utils import set_channel, set_group, set_must


@app.on_message(filters.command(["• گۆڕینی کەناڵی بۆت •", "گۆڕینی کەناڵی بۆت"], ""))
async def set_botch(client: Client, message):
    bot_username = app.username
    if message.chat.id == OWNER_ID or message.chat.id in SUDOERS:
        NAME = await client.ask(
            message.chat.id, "**لینکی کەناڵی نوێ بنێرە**", filters=filters.text
        )
        channel = NAME.text
        await set_channel(app.username, channel)
        await message.reply_text("**بە سەرکەوتوویی کەناڵی بۆت گۆڕا -🖱️**")
        return


@app.on_message(filters.command(["• گۆڕینی گرووپی بۆت •", "گۆڕینی گرووپی بۆت"], ""))
async def set_botgr(client: Client, message):
    bot_username = app.username
    if message.chat.id == OWNER_ID or message.chat.id in SUDOERS:
        NAME = await client.ask(
            message.chat.id, "**لینکی گرووپی نوێ بنێرە**", filters=filters.text
        )
        group = NAME.text
        await set_group(bot_username, group)
        await message.reply_text("**بە سەرکەوتوویی گرووپی بۆت گۆڕا -🖱️**")
        return


@app.on_message(
    filters.command(
        ["• ناچالاککردنی جۆینی ناچاری •", "• چالاککردنی جۆینی ناچاری •"], ""
    )
)
async def set_join_must(client: Client, message):
    bot_username = app.username
    if message.chat.id == OWNER_ID or message.chat.id in SUDOERS:
        bot_username = app.username
        m = message.command[0]
        await set_must(bot_username, m)
        if message.command[0] == "• ناچالاککردنی جۆینی ناچاری •":
            await message.reply_text("**بە سەرکەوتوویی جۆینی ناچاری ناچالاککرا -🖱️**")
        else:
            await message.reply_text("**بە سەرکەوتوویی جۆینی ناچاری چالاککرا -🖱️**")
        return
