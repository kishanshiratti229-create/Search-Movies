from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import db
from .utils import is_admin

@Client.on_message(filters.command("settings") & filters.group)
async def settings_cmd(client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("⛔ This command is available to administrators only.", quote=True)
    
    await send_settings_panel(message.chat.id, message)

async def send_settings_panel(chat_id, message, is_edit=False):
    settings = await db.get_settings(chat_id)
    
    res_val = settings.get('results_per_page', 10)
    disp_val = settings.get('display_mode', 'inline')
    trig_val = settings.get('search_trigger', 'all')

    text = "<b>⚙️ Bot Settings ⚙️</b>\n\nClick on the value to change.\n"
    
    res_btn = str(res_val)
    disp_btn = 'buttons' if disp_val == 'inline' else 'text'
    trig_btn = 'Every message' if trig_val == 'all' else 'Only with !'

    buttons = [
        [InlineKeyboardButton(res_btn, callback_data="set_res"), InlineKeyboardButton('Number of results:', callback_data="noop")],
        [InlineKeyboardButton(disp_btn, callback_data="set_disp"), InlineKeyboardButton('Display mode:', callback_data="noop")],
        [InlineKeyboardButton(trig_btn, callback_data="set_trig"), InlineKeyboardButton('Search trigger:', callback_data="noop")],
        [InlineKeyboardButton('✘ Close Menu ✘', callback_data="close_settings")]
    ]
    
    markup = InlineKeyboardMarkup(buttons)

    if is_edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.reply(text, reply_markup=markup, quote=True)

@Client.on_callback_query(filters.regex(r"^(set_|close_settings)"))
async def settings_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    
    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("⛔ For administrators only!", show_alert=True)
    
    data = query.data

    if data == "close_settings":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            pass 
        return

    settings = await db.get_settings(chat_id)
    
    if data == "set_res":
        new_val = 5 if settings.get('results_per_page', 10) == 10 else 10
        await db.update_settings(chat_id, 'results_per_page', new_val)
        
    elif data == "set_disp":
        curr = settings.get('display_mode', 'inline')
        new_val = 'text' if curr == 'inline' else 'inline'
        await db.update_settings(chat_id, 'display_mode', new_val)
        
    elif data == "set_trig":
        curr = settings.get('search_trigger', 'all')
        new_val = 'bang' if curr == 'all' else 'all'
        await db.update_settings(chat_id, 'search_trigger', new_val)
        
    await query.answer("The definition has been updated ✅")
    await send_settings_panel(chat_id, query.message, is_edit=True)
