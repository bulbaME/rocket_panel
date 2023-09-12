import telegram
from telegram import Update, BotCommand, MenuButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .data import *
from .misc import steps

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_auth(user_name, context):
        return
    
    user_btn = InlineKeyboardButton('👤 Profile', callback_data=steps['PANEL']['USER'])
    hashtag_btn = InlineKeyboardButton('#️⃣ Hashtag', callback_data=steps['PANEL']['HASHTAG'])
    location_btn = InlineKeyboardButton('📍 Location', callback_data=steps['PANEL']['LOCATION'])
    compare_btn = InlineKeyboardButton('🖥 Compare', callback_data=steps['PANEL']['COMPARE'])

    keyboard = InlineKeyboardMarkup([[user_btn], [hashtag_btn], [location_btn], [compare_btn]])

    await context.bot.send_message(chat_id, f'`🚀 Rocket Panel 🚀`\n\n*Profile* \- instagram profile menu\n*Hashtag* \- instagram hashtag\n*Location* \- instagram location\n*Compare* \- compare two data files', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

    return steps['PANEL']['SELECTION']