import asyncio

from AlinaMusic import app
from AlinaMusic.core.mongo import mongodb
from pyrogram import Client, enums, filters, types

upadmindb = mongodb.upadmin

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

# Helper functions for MongoDB


async def get_user_privileges(user_id: int):
    privileges = await upadmindb.find_one({"user_id": user_id})
    if privileges is None:
        # Insert default privileges if user is not found
        privileges = {"user_id": user_id, "privileges": DEFAULT_PRIVILEGES}
        await upadmindb.insert_one(privileges)
    return privileges["privileges"]


async def update_user_privileges(user_id: int, updated_privileges: dict):
    await upadmindb.update_one(
        {"user_id": user_id}, {"$set": {"privileges": updated_privileges}}, upsert=True
    )


# Pyrogram filters
def is_admin():
    async def func(_, app, message):
        user_id = message.from_user.id
        try:
            chat_id = message.chat.id
        except AttributeError:
            chat_id = message.message.chat.id
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        ]

    return filters.create(func)


def is_onCall(data):
    async def func(flt, _, query):
        return query.data.split("|")[0] == flt.data

    return filters.create(func, data=data)


# Keyboard generator
async def keyboard(user_id: int):
    privileges = await get_user_privileges(user_id)
    return types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(
                    ON_TYPES[all(privileges.values())],
                    f"up_all_prom|{user_id}",
                ),
                types.InlineKeyboardButton("هەموو ڕۆڵەکان", callback_data="None"),
            ],
            *[
                [
                    types.InlineKeyboardButton(
                        ON_TYPES[privileges[key]],
                        f"up_prom|{user_id}|{key}",
                    ),
                    types.InlineKeyboardButton(description, callback_data="None"),
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
            [types.InlineKeyboardButton("ئێستا ئەندام بکە ئەدمین", f"save|{user_id}")],
            [types.InlineKeyboardButton("داخستن", callback_data="close")],
        ]
    )


# Command to initialize admin privilege management
@app.on_message(
    filters.regex("^/upadmin$") & filters.group & filters.reply & is_admin()
)
async def ON_RPLY(app: Client, message: types.Message):
    user_id = message.reply_to_message.from_user.id
    # Ensure the user exists in the database
    await get_user_privileges(user_id)
    await app.send_message(
        message.chat.id,
        text="**ڕۆڵەکانی ئەدمینی نوێ دیاریبکە دواتر بیکە بە ئەدمین👾🖤•**",
        reply_markup=await keyboard(user_id),
    )


@app.on_callback_query(is_onCall("up_prom") & is_admin())
async def toggle_privilege(app: Client, query: types.CallbackQuery):
    _, user_id, privilege = query.data.split("|")
    user_id = int(user_id)

    # Toggle privilege in MongoDB
    privileges = await get_user_privileges(user_id)
    privileges[privilege] = not privileges[privilege]
    await update_user_privileges(user_id, privileges)

    await query.message.edit_text(
        text="**ڕۆڵەکانی ئەدمینی نوێ دیاریبکە دواتر بیکە بە ئەدمین👾🖤•**",
        reply_markup=await keyboard(user_id),
    )


@app.on_callback_query(is_onCall("up_all_prom") & is_admin())
async def enable_all_privileges(app: Client, query: types.CallbackQuery):
    _, user_id = query.data.split("|")
    user_id = int(user_id)

    # Enable all privileges in MongoDB
    privileges = {key: True for key in DEFAULT_PRIVILEGES}
    await update_user_privileges(user_id, privileges)

    await query.message.edit_text(
        text="**ڕۆڵەکانی ئەدمینی نوێ دیاریبکە دواتر بیکە بە ئەدمین👾🖤•**",
        reply_markup=await keyboard(user_id),
    )


@app.on_callback_query(is_onCall("save"))
async def save_and_promote(app: Client, query: types.CallbackQuery):
    _, user_id = query.data.split("|")
    user_id = int(user_id)

    privileges = await get_user_privileges(user_id)
    chat_id = query.message.chat.id

    try:
        # Promote user with selected privileges
        await app.promote_chat_member(
            chat_id,
            user_id,
            types.ChatPrivileges(**privileges),
        )
        await query.message.edit_text(text="**✧¦ بە سەرکەوتوویی کرا بە ئەدمین♥️•**")
    except Exception as e:
        await query.message.edit_text(text=f"**✧¦ هەڵە ڕوویدا: {str(e)}**")
    await asyncio.sleep(60)
    await query.message.delete()
