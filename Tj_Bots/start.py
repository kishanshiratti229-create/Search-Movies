
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import UPDATE_CHANNEL, REQUEST_GROUP, PHOTO_URL, ADMINS, LOG_CHANNEL, AUTH_CHANNEL_FORCE
from database import db
from .utils import get_readable_size

async def send_file_with_fallback(client, chat_id, file_data, reply_to_id=None):
    try:
        await client.copy_message(
            chat_id=chat_id,
            from_chat_id=file_data['chat_id'],
            message_id=file_data['message_id'],
            caption=None,
            reply_to_message_id=reply_to_id
        )
        return True
    except:
        file_id = file_data.get('file_id')
        if not file_id:
            return False
            
        file_name = file_data.get('file_name', '')
        file_size = get_readable_size(file_data.get('file_size', 0))
        fallback_caption = f"**{file_name}**\n\n**💾 Size: {file_size}**"
        
        try:
            await client.send_video(
                chat_id=chat_id,
                video=file_id,
                caption=fallback_caption,
                reply_to_message_id=reply_to_id
            )
            return True
        except:
            try:
                await client.send_document(
                    chat_id=chat_id,
                    document=file_id,
                    caption=fallback_caption,
                    reply_to_message_id=reply_to_id
                )
                return True
            except:
                return False

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.from_user.id
        
        if len(message.command) > 1:
            file_db_id = message.command[1]
            
            should_check = AUTH_CHANNEL_FORCE
            is_subbed = True
            
            if should_check:
                try:
                    await client.get_chat_member(UPDATE_CHANNEL, user_id)
                except:
                    is_subbed = False

            if not is_subbed:
                btn = [[InlineKeyboardButton('📣 Subscribe to the channel', url=f'https://t.me/{UPDATE_CHANNEL}')],
                       [InlineKeyboardButton('↻ Try again', callback_data=f"checksub_{file_db_id}")]]
                
                return await message.reply_text(
                    "**To use this bot you must be subscribed to its feed!🫰**",
                    reply_markup=InlineKeyboardMarkup(btn),
                    quote=True
                )

            file_data = await db.get_file(file_db_id)
            if file_data:
                success = await send_file_with_fallback(client, message.chat.id, file_data, message.id)
                if not success:
                    await message.reply("❌ The file was deleted from the source or I don't have access to it.", quote=True)
            return

        bot_name = client.me.first_name
        bot_username = client.me.username
        bot_mention = f"[{bot_name}](https://t.me/{bot_username})"

        anim_msg = await message.reply_text(
             f"<blockquote>**__Hi <tg-emoji emoji-id='5195448447062251797'>👋</tg-emoji>__**\n**__Welcome to {bot_mention} <tg-emoji emoji-id='5325559344513691205'>😎</tg-emoji>__**</blockquote>",
             quote=True
        )        
        await asyncio.sleep(1.0)
        
        await anim_msg.edit_text("<tg-emoji emoji-id='5456140674028019486'>⚡️</tg-emoji>")
        await asyncio.sleep(0.8)

        await anim_msg.edit_text("**__Boot starts...__** <tg-emoji emoji-id='5929303842205207391'>😈</tg-emoji>")
        await asyncio.sleep(0.7)
        
        await send_home_message(client, message)
        await anim_msg.delete()

    elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply("Hey! I'm ready to search for movies 🎬", quote=True)

@Client.on_message(filters.new_chat_members)
async def added_to_group(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            await message.reply("Thanks for adding me! 🎬\nSend the name of the movie/series you want to search for.", quote=True)

async def send_home_message(client, message, user=None, is_edit=False):
    if not user:
        user = message.from_user
    
    user_mention = user.mention
    bot_name = client.me.first_name
    bot_username = client.me.username
    bot_mention = f"[{bot_name}](https://t.me/{bot_username})"
    
    buttons = [
        [InlineKeyboardButton("🔍 Inline Search 🔎", switch_inline_query_current_chat="", style=enums.ButtonStyle.PRIMARY)],
        [InlineKeyboardButton('✇ Request Group ✇', url=REQUEST_GROUP, style=enums.ButtonStyle.SUCCESS),
         InlineKeyboardButton('✇ Update Channel ✇', url=f'https://t.me/{UPDATE_CHANNEL}', style=enums.ButtonStyle.SUCCESS)],
        [InlineKeyboardButton('〄 Help 〄', callback_data='help', style=enums.ButtonStyle.PRIMARY), 
         InlineKeyboardButton('⍟ About ⍟', callback_data='about', style=enums.ButtonStyle.PRIMARY)],
        [InlineKeyboardButton('⇋ Add to group ⇋', url=f"http://t.me/{client.me.username}?startgroup&admin=delete_messages", style=enums.ButtonStyle.SUCCESS)]
    ]
    
    txt = (f"**היי {user_mention} <tg-emoji emoji-id='5195448447062251797'>👋</tg-emoji>**\n"
            f"**Welcome to {bot_mention}** <tg-emoji emoji-id='5325559344513691205'>😎</tg-emoji>\n\n"
           "**I am an innovative movie and series search engine,**"
           "\n<b>My job is to look for movies in groups,"
           "\nAdd me to your group and I'll continue from here.</b><tg-emoji emoji-id='5224607267797606837'>☄️</tg-emoji>\n\n"
           "<blockquote>**👨🏼‍💻Lead Programmer: @BOSS1480**</blockquote>")
    
    if is_edit:
        await message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_photo(PHOTO_URL, caption=txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    if data.startswith("checksub_"):
        file_db_id = data.split("_")[1]
        
        should_check = AUTH_CHANNEL_FORCE
        is_subbed = True
        
        if should_check:
            try:
                await client.get_chat_member(UPDATE_CHANNEL, user_id)
            except:
                is_subbed = False

        if not is_subbed:
            return await query.answer("❌ You are not yet subscribed to the channel! You must subscribe to receive the file.", show_alert=True)
        
        file_data = await db.get_file(file_db_id)
        if file_data:
            reply_to = query.message.reply_to_message.id if query.message.reply_to_message else None
            success = await send_file_with_fallback(client, query.message.chat.id, file_data, reply_to)
            if success:
                await query.message.delete()
            else:
                await query.answer("❌ The file has been deleted from the source or I don't have access to it.", show_alert=True)
        else:
            await query.answer("❌ The file is not in the database.", show_alert=True)
        return

    if data == "help_admin" and user_id not in ADMINS:
        return await query.answer("⛔ For administrators only.", show_alert=True)
    
    if data not in ["closea", "noop", "help_stats"]:
        try:
            await query.message.edit_media(
                InputMediaPhoto(PHOTO_URL, caption=""),
                reply_markup=None 
            )
            await asyncio.sleep(0.1)
        except:
            pass
    
    if data == "home":
        await send_home_message(client, query.message, user=query.from_user, is_edit=True)
    
    elif data == "help":
        user_mention = query.from_user.mention
        
        buttons = [
            [InlineKeyboardButton('Group Settings', callback_data='help_settings', style=enums.ButtonStyle.PRIMARY), InlineKeyboardButton('Copyright', callback_data='help_copyright', style=enums.ButtonStyle.PRIMARY)],
            [InlineKeyboardButton('Extra', callback_data='help_extra', style=enums.ButtonStyle.PRIMARY), InlineKeyboardButton('User Guide', callback_data='help_guide', style=enums.ButtonStyle.PRIMARY)],
            [InlineKeyboardButton('Download from TikTok', callback_data='help_d', style=enums.ButtonStyle.PRIMARY), InlineKeyboardButton('Statistics', callback_data='help_stats', style=enums.ButtonStyle.PRIMARY)],
            [InlineKeyboardButton('🆕 Upload Image', callback_data='help_telegraph', style=enums.ButtonStyle.PRIMARY), InlineKeyboardButton('🆕 Video Tools', callback_data='help_exthumb', style=enums.ButtonStyle.PRIMARY)],
            [InlineKeyboardButton('🏠 בית 🏠', callback_data='home', style=enums.ButtonStyle.DANGER)],          
        ]
        
        if user_id in ADMINS:
             btns.insert(0, [InlineKeyboardButton('👮‍♂️ Admin Commands 👮‍♂️', callback_data='help_admin', style=enums.ButtonStyle.DANGER)])

        await query.message.edit_media(
            InputMediaPhoto(PHOTO_URL, caption=f"<b>Hey {user_mention},\nHere you can get help for all my commands.</b>"),
            reply_markup=InlineKeyboardMarkup(btns)
        )

    elif data == "help_extra":
        txt = (
            "<b><u>Extra Tools:</u></b>\n\n"
            "<b>◉ Text font:</b>\n"
            "<blockquote>• <code>/font</code> [text] - Converts English text to special fonts.</blockquote>\n\n"
            "<b>◉ Text Sharing:</b>\n"
            "<blockquote>• <code>/share</code> [text] - Creates a quick share link to the text you wrote.</blockquote>\n\n"
            "<b>◉ Text-to-speech (TTS):</b>\n"
            "<blockquote>• <code>/tts</code> - Reply to a text message, and the bot will send it to you as a voice message.</blockquote>\n\n"
            "<b>◉ Upload text (Paste):</b>\n"
            "<blockquote>• <code>/paste</code> - Comment on text or a file to upload it to Pastebin and get a link.</blockquote>\n\n"
            "<b>◉ User details:</b>\n"
            "<blockquote>• <code>/id</code> - User ID/Chat ID.</blockquote>\n"
            "<blockquote>• <code>/info</code> - Information about a user's account, profile, name, username, etc...</blockquote>\n\n"
            "<b>◉ Sticker ID</b>\n"
            "<blockquote>• <code>/stickerid</code> - Gets the id of the sticker that was commented on.</blockquote>\n\n"
            "<b>◉ System Tools:</b>\n"
            "<blockquote>• <code>/json</code> - Get the technical information (JSON) of the message.</blockquote>\n"
            "<blockquote>• <code>/written</code> [filename] - Converts the text to a text file.</blockquote>"
        )
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]))

    elif data == "help_admin":
        txt = (
            "<b><u>Administrator Control Panel:</u></b>\n\n"
            "<b>◉ Content Management:</b>\n"
            "<blockquote>• <code>/index</code> [link] - [start] - Adding files from a channel (by range).\n"
            "• <code>/newindex</code> [ID] - Track new content in the channel.\n"
            "• <code>/channels</code> - Manage monitored channels.</blockquote>\n\n"
            "<b>◉ Users and Groups:</b>\n"
            "<blockquote>• <code>/ban</code> [ID] - Block user.\n"
            "• <code>/unban</code> [ID] - Unban a user.\n"
            "• <code>/ban_chat</code> [ID] - Block group.\n"
            "• <code>/unban_chat</code> [ID] - Unban a group.\n"
            "• <code>/leave</code> [ID] - Leave group (without blocking).</blockquote>\n\n"
            "<b>◉ System:</b>\n"
            "<blockquote>• <code>/clean</code> - Data Cleanup Wizard.\n"
            "• <code>/broadcast</code> [-f] - Broadcast to subscribers.\n"
            "• <code>/broadcast_groups</code> - Broadcast to groups.\n"
            "• <code>/restart</code> - Restart.</blockquote>"
        )
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]))

    elif data == "help_guide":
        txt = (
            "<blockquote>"
            "⚙️ <b><u> Guide to searching in the search robot</u></b> 💡\n\n"
            "To request a movie or series, you must pay attention to the way you request. It is important to write the exact name of the movie or series you want to find.\n\n"
            "<b><i><u>Examples of correct search </u></i></b>✔️\n"
            "My fault\n"
            "Fast and Furious\n\n"
            "<b><i><u>Incorrect examples</u></i></b>❌\n"
            "Is there Harry Potter?"
            "Maybe Harry Potter\n"
            "Is there a Harry Potter movie?\n\n"
            "<b>Got it? Great!</b>\n"
            "<b>Try it now in a group!</b>\n\n"
            "<b>You didn't understand</b> <b>⁉️</b>\n"
            "<b>Don't worry</b> ‼️\n"
            "We're here to help! Our great team is always available to answer requests ⚡️\n"
            "It's just another smart way to respond faster."
            "</blockquote>"
)

        btn = [[InlineKeyboardButton('Go to group 💬', url=REQUEST_GROUP, style=enums.ButtonStyle.SUCCESS)], [InlineKeyboardButton('Return ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup(btn))

    elif data == "help_copyright":
        txt = "<b>© Copyright</b>\n\nThe files in the bot are collected from Telegram automatically. We do not upload content ourselves."
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]))
    
    elif data == "help_settings":
        txt = "<b>⚙️ Group Settings</b>\n\nSend <code>/settings</code> in the group to set:\n• Display mode (buttons/text)\n• Search trigger (!)\n• Number of results"
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]))

    elif data == "help_stats":
        try:
            await query.message.edit_caption("⏳ **Computer data...**")
        except:
            pass

        def get_size(bytes, suffix="B"):
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor

        MAX_DB_SIZE = 536870912

        users = await db.users.count_documents({})
        files = await db.files.count_documents({})
        groups = await db.groups.count_documents({})

        try:
            db_stats = await db.users.database.command("dbstats")
            used_bytes = db_stats['storageSize']
            used_size = get_size(used_bytes)
            max_size = get_size(MAX_DB_SIZE)
            
            percentage = (used_bytes / MAX_DB_SIZE) * 100
            
            bar_len = 10
            filled_len = int(bar_len * percentage / 100)
            bar = '▓' * filled_len + '░' * (bar_len - filled_len)
            
            db_info = (
                f"🗄 <u>**Database storage:**</u>\n"
                f"<blockquote>**★ Used:** `{used_size}`\n"
                f"**★ from:** `{max_size}`\n"
                f"★ **Status:** [{bar}] `{percentage:.2f}%`</blockquote>"
            )
        except Exception as e:
            db_info = f"❌ Technical data cannot be retrieved.\n`{e}`"

        txt = (
            f"📊 <u>**Bot Statistics:**</u>\n\n"
            f"🤖 <u>**Bot Status:**</u>\n"
            f"<blockquote>★ **Files:** `{files}`\n"
            f"★ **Users:** `{users}`\n"
            f"★ **Groups:** `{groups}`</blockquote>\n\n"
            f"{db_info}"
        )
        
        await query.message.edit_media(
            InputMediaPhoto(PHOTO_URL, caption=txt), 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY),
                 InlineKeyboardButton('↻ רענן', callback_data='help_stats', style=enums.ButtonStyle.SUCCESS)]
            ])
        )

    elif data == "about":
        bot_name = client.me.first_name
        bot_username = client.me.username
        bot_mention = f"[{bot_name}](https://t.me/{bot_username})"
        txt = (
            "<blockquote><b>╔════❰ 𝗔𝗯𝗼𝘂𝘁 𝗧𝗵𝗲 𝗕𝗼𝘁 ❱═❍⊱❁۪۪</b>\n"
            "<b>║╭━━━━━━━━━━━━━━━➣</b>\n"
            f"<b>║┣⪼ 🤖 ʙᴏᴛ : {bot_mention}</b>\n"
            "<b>║┣⪼ 👦 ᴄʀᴇᴀᴛᴏʀ : @KishanMS</b>\n"
            f"<b>║┣⪼ 🤖 ᴜᴘᴅᴀᴛᴇ : <a href='https://t.me/{UPDATE_CHANNEL}'>Update Channel</a></b>\n"
            "<b>║┣⪼ 🗣️ ʟᴀɴɢᴜᴀɢᴇ : [Python](https://www.python.org/)</b>\n"
            "<b>║┣⪼ 📚 Lɪʙʀᴀʀʏ : [Pyrogram](https://docs.pyrogram.org/)</b>\n"
            "<b>║┣⪼ &lt;/&gt; Movie Website: : [Movie website](https://Cinhub4u.gt.tc)</b>\n"
            "<b>║╰━━━━━━━━━━━━━━━➣</b>\n"
            "<b>╚══════════════════❍⊱❁۪۪</b></blockquote>"
        )
        btn = [
            [InlineKeyboardButton('🐙 Movie.Website 🐙', url='https://cinhub4u.gt.tc', style=enums.ButtonStyle.SUCCESS)], 
            [InlineKeyboardButton('חזרה ⋟', callback_data='home', style=enums.ButtonStyle.PRIMARY), InlineKeyboardButton('✘ סגור', callback_data='closea', style=enums.ButtonStyle.DANGER)]
        ]
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup(btn))

    elif data == "help_d":
        txt = (
            "<b><tg-emoji emoji-id='5443127283898405358'>📥</tg-emoji></b><b> </b><b><u>Download from TikTok:</u></b>\n\n\n<b>◉ </b><b><u>Command:</u></b>\n<blockquote>/d</blockquote>\n\n<b>◉ </b><b><u>How to use</u>?</b>\n<blockquote>Send the command along with a link. You can also respond to the link with the command.</blockquote>"
        )
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]))


    elif data == "help_telegraph":
        txt = (
            "<tg-emoji emoji-id='5445355530111437729'>📤</tg-emoji> <b><u>Uploading photos to: i.ibb.co</u></b> 🖼️\n\n\n<b>◉ </b><b><u>Command:</u></b>\n<blockquote>/telegraph</blockquote>\n\n<b>◉ </b><b><u>How to use?</u></b>\n<blockquote>Simply comment on a photo with the command.</blockquote>"
        )
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]))


    elif data == "help_exthumb":
        txt = (
            "<tg-emoji emoji-id='5823268688874179761'>🔧</tg-emoji> <b><i>Video Tools:</i>\n\n\n</b><b><tg-emoji emoji-id='5332679880599418983'>ℹ️</tg-emoji></b><b> </b><b><u>Video Information:</u></b>\n<b>◉ Command:</b>\n<blockquote>/mediainfo</blockquote>\n\n<b>🖼️ </b><b><u>Extract Thumbnail:</u></b>\n<b>◉ Command:</b>\n<blockquote>/extract_thumbnail</blockquote>\n\n\n<b><u>How to use?</u></b>\n<blockquote>Comment on a video/file with the command ")
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help', style=enums.ButtonStyle.PRIMARY)]]))


    elif data == "closea":
        try:
            await query.message.delete()
  
