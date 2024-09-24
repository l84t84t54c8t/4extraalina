import time
from asyncio import sleep

from AlinaMusic import app
from pyrogram import enums, filters
from pyrogram.types import Message
from strings.filters import command


@app.on_message(
    ~filters.private & command(["/gdata", "داتای گرووپ", "gdata", "پشکنینی گرووپ"]),
    group=2,
)
async def instatus(app, message):
    start_time = time.perf_counter()
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    count = await app.get_chat_members_count(message.chat.id)
    if user.status in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        sent_message = await message.reply_text("**هێنانی داتایی گرووپ . .**")
        deleted_acc = 0
        premium_acc = 0
        banned = 0
        bot = 0
        uncached = 0
        async for ban in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.BANNED
        ):
            banned += 1
        async for member in app.get_chat_members(message.chat.id):
            user = member.user
            if user.is_deleted:
                deleted_acc += 1
            elif user.is_bot:
                bot += 1
            elif user.is_premium:
                premium_acc += 1
            else:
                uncached += 1
        end_time = time.perf_counter()
        timelog = "{:.2f}".format(end_time - start_time)
        await sent_message.edit(
            f"""
**➖➖➖➖➖➖➖
➲ ناو : {message.chat.title} ✅
➲ ئەندام : [ {count} ]🫂
➖➖➖➖➖➖➖
➲ بۆتەکان : {bot}💡
➲ ئەکاونتی سووتاو : {deleted_acc}🧟
➲ باندکراوەکان : {banned}🚫
➲ بەکارهێنەری پریمیوم : {premium_acc}🎁
➖➖➖➖➖➖➖
کاتی خایەنراو : {timelog} S**"""
        )
    else:
        sent_message = await message.reply_text("**تەنیا ئەدمینەکان دەتوانن!**")
        await sleep(5)
        await sent_message.delete()


@app.on_message(command(["groupinfo", "زانیاری"]))
async def get_group_status(_, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "**فەرمان بنووسە لەگەڵ یوزەری گرووپ یان کەناڵ\nنموونە:**\n`/ginfo , زانیاری @username`"
        )
        return

    group_username = message.command[1]

    try:
        group = await app.get_chat(group_username)
    except Exception as e:
        await message.reply(f"**➲ هەڵە: {e}**")
        return

    total_members = await app.get_chat_members_count(group.id)
    group_description = group.description
    premium_acc = banned = deleted_acc = bot = (
        0  # You should replace these variables with actual counts.
    )

    response_text = (
        f"**➖➖➖➖➖➖➖\n**"
        f"**➲ ناو : {group.title} ✅\n\n**"
        f"**➲ ئایدی :** `{group.id}`\n"
        f"**➲ ئەندام : {total_members}\n**"
        f"**➲ بایۆ : {group_description or 'N/A'}\n\n**"
        f"**➲ یوزەر : @{group_username}\n**"
        f"➖➖➖➖➖➖➖"
    )

    await message.reply(response_text)
