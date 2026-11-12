from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMINS
from database import db
import random

CAPTCHA_CHANNELS = {}

@Client.on_message(filters.command("channels") & filters.user(ADMINS))
async def list_channels(client, message):
    channels = await db.get_watched_channels()
    
    if not channels:
        return await message.reply("No channels in the watchlist.", quote=True)
    
    keyboard = []
    for chat_id in channels:
        keyboard.append([
            InlineKeyboardButton(f"Channel: {chat_id}", callback_data="noop"),
            InlineKeyboardButton("🗑️ הסר", callback_data=f"ask_rem_ch_{chat_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("❌ סגור", callback_data="clean_cancel")])
    
    await message.reply(
        f"📋 **List of channels being followed ({len(channels)})**\nClick 'Remove' to stop following.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        quote=True
    )

@Client.on_callback_query(filters.regex(r"^ask_rem_ch_"))
async def ask_remove_channel(client, query):
    try: chat_id = int(query.data.split("_")[-1])
    except: return
    user_id = query.from_user.id
    
    num1 = random.randint(1, 9)
    num2 = random.random(1, 9)
    correct = num1 + num2
    
    CAPTCHA_CHANNELS[(user_id, chat_id)] = correct
    
    answers = [correct, correct + random.randint(1, 3), correct - random.randint(1, 3)]
    random.shuffle(answers)
    
    buttons = []
    for ans in answers:
        btns.append(InlineKeyboardButton(str(ans), callback_data=f"sol_rem_ch_{chat_id}_{ans}"))
    
    markup = InlineKeyboardMarkup([btns, [InlineKeyboardButton("❌ ביטול", callback_data="clean_cancel")]])
    
    await query.message.edit_text(
        f"⚠️ **Deletion Verification**\nRemove channel `{chat_id}` from tracking?\n\nSolution: **{num1} + {num2} = ?**",
        reply_markup=markup
    )

@Client.on_callback_query(filters.regex(r"^sol_rem_ch_"))
async def solve_remove_channel(client, query):
    parts = query.data.split("_")
    chat_id = int(parts[-2])
    ans = int(parts[-1])
    user_id = query.from_user.id
    key = (user_id, chat_id)
    
    if key not in CAPTCHA_CHANNELS:
        return await query.answer("Expired.", show_alert=True)
    
    correct = CAPTCHA_CHANNELS[key]
    del CAPTCHA_CHANNELS[key]
    
    if ans != correct:
        await query.message.delete()
        return await query.answer("Error! Not deleted.", show_alert=True)
    
    await db.remove_watched_channel(chat_id)
    await query.message.edit_text(f"✅ Channel `{chat_id}` has been removed from the watchlist.")

@Client.on_callback_query(filters.regex("clean_cancel"))
async def cancel_action(client, query):
    await query.message.delete()
