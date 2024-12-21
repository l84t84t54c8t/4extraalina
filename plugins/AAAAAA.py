from ahmed import Ahmed
from pyrogram import Client, types, filters, enums, raw
import pyromod
import ahmed
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, SessionPasswordNeeded, PasswordHashInvalid, PhoneCodeExpired
)
import asyncio


# start Pyrogram App 
app = Client(
    name="rad", 
    bot_token=Ahmed.TETO, 
    api_hash=Ahmed.API_HASH, 
    api_id=Ahmed.API_ID
)



@app.on_message(filters.private & filters.regex('^/start$'))
async def ON_START_BOT(app: Client, message: types.Message):
    await app.send_message(
        chat_id=message.chat.id ,text="-🙋‍♂ أهلا بك\n-📮 في بوت حذف حسابات التيليكرام.\n\n▫️ من خلاله يمكنك حذف حسابك بسهوله،\n▫️ عبر اتباعك للخطوات،\n▫️ لكن احذر: لن تستطيع استرجاع حسابك أبداً.", 
        reply_markup=types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(text='حذف حسابي ⛔...', callback_data="DELETACCOUNT")
            ],
            [
                types.InlineKeyboardButton(text='استخراج الايبيهات', callback_data="GETAPI")
            ]
        ])
    )

SESSSIONS = None
PASSWORD = None

@app.on_callback_query(filters.regex('^DELETACCOUNT$'))
async def DELET_ACCOUNT(app: Client, query: types.CallbackQuery):
    global SESSSIONS
    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=query.message.id , 
        text='- ارسل رقم هاتفك 👤\nمثال : +20123456789', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('BACK', 'BACK')]])
    )

    # On Listen Phone Number 
    data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

    # Check PHone and start Client 
    PhoneNumber = data.text
    message_data = await app.send_message(
        chat_id=query.message.chat.id, 
        text='↢ جاري التحقق من البيانات'
    )
    
    session_client = Client(
        name=":memory:",
        api_hash=Ahmed.API_HASH, api_id=Ahmed.API_ID, in_memory=True
    )
    try:
        await session_client.connect()
        phon_code_data = await session_client.send_code(
            phone_number=PhoneNumber
        )

    except PhoneNumberInvalid as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text="↢ رقم هاتفك غير صحيح حاول مره اخري", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('• ارجع •', 'BACK')]])
        )
        await session_client.disconnect()
        return  
      
    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=message_data.id, 
        text='↢ ارسل الان كود التحقق', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('• ارجع •', 'BACK')]])
    )

    # On Listen Ver Code 
    data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

    
    message_data = await app.send_message(
        chat_id=query.message.chat.id, 
        text='↢ جاري التحقق من البيانات'
    )

    # Check COde
    try: 
        VerCode = int(data.text)
    except:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text='↢ رقم هاتفك غير صحيح حاول مره اخري', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('• ارجع •', 'BACK')]])
        )
        return

    # Start Logins Session
    try:
        await session_client.sign_in(
            phone_code=str(VerCode), 
            phone_code_hash=phon_code_data.phone_code_hash, 
            phone_number=PhoneNumber
        )

    except (PhoneCodeInvalid ,PhoneCodeExpired) as Err:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text='↢ رقم هاتفك غير صحيح حاول مره اخري' ,reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('• ارجع •', 'BACK')]])
        )
        return
    
    
    except SessionPasswordNeeded as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text='↢ الان حان اخر خطوه قم بارسال كود المستلم من التليجرام', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('• ارجع •', 'BACK')]])
        )
        
        # On Listen Password 
        data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

        
        Password = data.text
        PASSWORD = Password
        message_data = await app.send_message(
            chat_id=query.message.chat.id, 
            text='↢ جاري التحقق من البيانات'
            )

        # CHcek Password 
        try: 
            await session_client.check_password(Password)
         
        except PasswordHashInvalid as Err:
            await app.edit_message_text(
                    chat_id=query.message.chat.id, message_id=message_data.id, 
                    text='↢ كود التحقق خطا حاول مره اخري', reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton('• ارجع •', 'BACK')]])
            )
            await session_client.disconnect()
            return
        
    #  ADD Session Data 
    session_String = await session_client.export_session_string()
    SESSSIONS = session_String
    await session_client.disconnect()


    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=message_data.id, 
        text="↢ عزيزي هل انت متأكد من انك تريد حذف حسابك ؟", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text="أجل ، اريد ذلك", callback_data='OnDelete')]])
    )



@app.on_callback_query(filters.regex('^OnDelete$'))
async def DELET_ACCOUNT(app: Client, query: types.CallbackQuery):
    async with Client(':memory:', api_hash="", api_id="",  session_string=SESSSIONS) as session_client:
        await session_client.invoke(raw.functions.account.DeleteAccount(
            reason="not"))

    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=query.message.id, 
        text="↢ باي ي عزيزي , تم حذف هذا الحساب"
    )




asyncio.run(app.run())

@app.on_callback_query(filters.regex('^GETAPI$'))
async def GET_API(app: Client, query: types.CallbackQuery):
    global API_HASH, API_ID
    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=query.message.id, 
        text= "ارسل رقم هاتفك 👤\nمثال : +20123456789", 
        reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("BACK", "BACK")]])
    )

    # On Listen Phone Number 
    data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

    # Check PHone and start Client 
    PhoneNumber = data.text
    message_data = await app.send_message(
        chat_id=query.message.chat.id, 
        text= "جاري التحقق من البيانات"
    )
    
    session_client = Client(
        name=":memory:",
        in_memory=True
    )
    try:
        await session_client.connect()
        phon_code_data = await session_client.send_code(
            phone_number=PhoneNumber
        )

    except PhoneNumberInvalid as Err:
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text="رقم هاتفك غير صحيح حاول مره اخري", 
            reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("• ارجع •", "BACK")]])
        )
        await session_client.disconnect()
        return  
      
    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=message_data.id, 
        text= "ارسل الان كود التحقق", 
        reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("• ارجع •", "BACK")]])
    )

    # On Listen Ver Code 
    data = await app.listen(chat_id=query.from_user.id, filters=filters.text & filters.private)

    # Check COde
    try: 
        VerCode = int(data.text)
    except:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text="رقم هاتفك غير صحيح حاول مره اخري", 
            reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("• ارجع •", "BACK")]])
        )
        return

    # Start Logins Session
    try:
        await session_client.sign_in(
            phone_code=str(VerCode), 
            phone_code_hash=phon_code_data.phone_code_hash, 
            phone_number=PhoneNumber
        )

    except (PhoneCodeInvalid,PhoneCodeExpired) as Err:
        await session_client.disconnect()
        await app.edit_message_text(
            chat_id=query.message.chat.id, message_id=message_data.id, 
            text="رقم هاتفك غير صحيح حاول مره اخري", 
            reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("• ارجع •", "BACK")]])
        )
        return
    
    # Get API Hash and ID
    api_hash = await session_client.invoke(raw.functions.help.GetConfig())
    API_HASH = api_hash.api_hash
    API_ID = api_hash.api_id

    await app.edit_message_text(
        chat_id=query.message.chat.id, message_id=message_data.id, 
        text=f"API Hash: {API_HASH}\nAPI ID: {API_ID}", 
        reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("BACK", "BACK")]])
    )

    await session_client.disconnect()
