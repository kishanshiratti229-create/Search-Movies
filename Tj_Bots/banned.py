from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import ADMINS, REQUEST_GROUP

SUPPORT_LINK = REQUEST_GROUP

@Client.on_message(group=-10)
async def ban_enforcer(client, message):
    if not message.from_user: return
    
    if message.from_user.id not in ADMINS:
        ban_info = await db.get_ban_status(message.from_user.id)
        if ban_info:
            if message.chat.type == enums.ChatType.PRIVATE:
                await message.reply(
                    f"🚫 **You are blocked from using the bot.**\nReason: `{ban_info.get('reason')}`\n\nFor inquiries, contact support.",
                    quote=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠️Support ", url=SUPPORT_LINK)]])
                )
            message.stop_propagation()
            return

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        chat_ban_info = await db.get_chat_ban_status(message.chat.id)
        if chat_ban_info:
            try:
                await message.reply(
                    f"🚫 **This group has been blocked for use.**\nReason: `{chat_ban_info.get('reason')}`\n\nThe bot is leaving the group now.",
                    quote=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠️ Support", url=SUPPORT_LINK)]])
                )
                await client.leave_chat(message.chat.id)
            except: pass
            message.stop_propagation()

@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/ban [ID] [reason]`", quote=True)
    
    try:
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) or "rule violation"
        
        await db.ban_user(user_id, reason)
        await message.reply(f"🚫 User `{user_id}` has been blocked.\nReason: `{reason}`", quote=True)
    except Exception as e:
        await message.reply(f"Error: {e}", quote=True)

@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_user_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/unban [ID]`", quote=True)
    
    try:
        user_id = int(message.command[1])
        await db.unban_user(user_id)
        await message.reply(f"✅ User `{user_id}` has been unblocked.", quote=True)
    except:
        await message.reply("Error executing command.", quote=True)

@Client.on_message(filters.command("ban_chat") & filters.user(ADMINS))
async def ban_chat_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/ban_chat [ID] [reason]`", quote=True)
    
    try:
        chat_id = int(message.command[1])
        reason = " ".join(message.command[2:]) or "rule violation"
        
        await db.ban_chat(chat_id, reason)
        await message.reply(f"🚫 Group `{chat_id}` has been blocked.\nReason: `{reason}`", quote=True)
        
        try:
            await client.send_message(chat_id, f"🚫 **This group has been blocked.**\nReason: {reason}\nBye!")
            await client.leave_chat(chat_id)
        except: pass
        
    except Exception as e:
        await message.reply(f"Error: {e}", quote=True)

@Client.on_message(filters.command("unban_chat") & filters.user(ADMINS))
async def unban_chat_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("שימוש: `/unban_chat [ID]`", quote=True)
    
    try:
        chat_id = int(message.command[1])
        await db.unban_chat(chat_id)
        await message.reply(f"✅ The group `{chat_id}` has been unblocked.", quote=True)
    except:
        await message.reply("Error.", quote=True)

@Client.on_message(filters.command("leave") & filters.user(ADMINS))
async def leave_chat_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("Use: `/leave [ID]`", quote=True)
    
    try:
        chat_id = int(message.command[1])
        await client.send_message(chat_id, "👋 **The bot administrator ordered me to leave the group. Goodbye!**")
        await client.leave_chat(chat_id)
        await message.reply(f"✅ I left the group `{chat_id}`.", quote=True)
    except Exception as e:
        await message.reply(f"Error: {e}", quote=True)
