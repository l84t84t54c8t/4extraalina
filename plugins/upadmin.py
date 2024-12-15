import asyncio
import json

from AlinaMusic import app
from pyrogram import Client, enums, filters, types
from pyrogram.errors import ChatAdminRequired

# Constants
ON_TYPES = {True: "✅", False: "❌"}
DEFAULT_PRIVILEGES = {
    "edit_info": False,
    "delete_message": False,
    "restrict_members": False,
    "invite_users": False,
    "pin_message": False,
    "Manage_video": False,
    "promote_members": False,
}
Temp = {}


# Check if user is an admin or owner
def is_admin():
    async def func(_, app: Client, message: types.Message) -> bool:
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            member = await app.get_chat_member(chat_id, user_id)
            return member.status in [
                enums.ChatMemberStatus.OWNER,
                enums.ChatMemberStatus.ADMINISTRATOR,
            ]
        except AttributeError:
            return False

    return filters.create(func)


# Filter for specific callback queries
def is_on_call(data: str):
    async def func(flt, _, query: types.CallbackQuery) -> bool:
        return query.data.split("|")[0] == flt.data

    return filters.create(func, data=data)


# Generate the admin privileges keyboard
def generate_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    ON_TYPES[False not in Temp[user_id].values()],
                    f"up_all_prom|{json.dumps({'user_id': user_id})}",
                ),
                types.InlineKeyboardButton("هەموو ڕۆڵەکان", callback_data="none"),
            ],
            *[
                [
                    types.InlineKeyboardButton(
                        ON_TYPES[Temp[user_id][key]],
                        f"up_prom|{json.dumps({'user_id': user_id, 'promote': key})}",
                    ),
                    types.InlineKeyboardButton(description, callback_data="none"),
                ]
                for key, description in {
                    "edit_info": "گۆرینی زانیاری",
                    "delete_message": "سڕینەوەی چات",
                    "restrict_members": "باند و میوت",
                    "pin_message": "بانگهێشت کردن",
                    "Manage_video": "کۆنتڕۆلکردنی تێل",
                    "promote_members": "زیادکردنی ئەدمین",
                }.items()
            ],
            [
                types.InlineKeyboardButton(
                    "ئێستا ئەندام بکە ئەدمین",
                    f"save|{json.dumps({'user_id': user_id})}",
                )
            ],
            [types.InlineKeyboardButton("داخستن", callback_data="close")],
        ]
    )


# Command to initiate admin privilege updates
@app.on_message(
    filters.regex("^/upadmin$") & filters.group & filters.reply & is_admin()
)
async def on_reply(app: Client, message: types.Message):
    chat_id = message.chat.id
    member_up_id = message.reply_to_message.from_user.id

    # Initialize user privileges
    Temp[member_up_id] = DEFAULT_PRIVILEGES.copy()

    await app.send_message(
        chat_id,
        text="**ڕۆڵەکانی ئەدمینی نوێ دیاریبکە دواتر بیکە بە ئەدمین👾🖤•**",
        reply_markup=generate_keyboard(member_up_id),
    )


# Callback for toggling individual privileges
@app.on_callback_query(is_on_call("up_prom") & is_admin())
async def toggle_privilege(app: Client, query: types.CallbackQuery):
    data = json.loads(query.data.split("|")[1])
    user_id = data["user_id"]
    privilege = data["promote"]

    # Toggle privilege
    Temp[user_id][privilege] = not Temp[user_id][privilege]

    await query.message.edit_text(
        text="**ڕۆڵەکانی ئەدمینی نوێ دیاریبکە دواتر بیکە بە ئەدمین👾🖤•**",
        reply_markup=generate_keyboard(user_id),
    )


# Callback for enabling all privileges
@app.on_callback_query(is_on_call("up_all_prom") & is_admin())
async def enable_all_privileges(app: Client, query: types.CallbackQuery):
    data = json.loads(query.data.split("|")[1])
    user_id = data["user_id"]

    # Enable all privileges
    for key in Temp[user_id]:
        Temp[user_id][key] = True

    await query.message.edit_text(
        text="**ڕۆڵەکانی ئەدمینی نوێ دیاریبکە دواتر بیکە بە ئەدمین👾🖤•**",
        reply_markup=generate_keyboard(user_id),
    )


# Callback for saving and promoting the user
@app.on_callback_query(is_on_call("save"))
async def save_and_promote(app: Client, query: types.CallbackQuery):
    data = json.loads(query.data.split("|")[1])
    user_id = data["user_id"]
    chat_id = query.message.chat.id

    try:
        # Promote the user with selected privileges
        await app.promote_chat_member(
            chat_id,
            user_id,
            types.ChatPrivileges(**Temp[user_id]),
        )
        await query.message.edit_text("**✧¦ بە سەرکەوتوویی کرا بە ئەدمین♥️•**")
    except ChatAdminRequired:
        await query.message.edit_text(
            "**✧¦ پێویستە بۆت ئەدمین بێت و ڕۆڵی زیادکردنی ئەدمینی هەبێت♥️•**"
        )
    finally:
        await asyncio.sleep(60)
        await app.delete_messages(chat_id, query.message.id)
