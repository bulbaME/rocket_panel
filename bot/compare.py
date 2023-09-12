import telegram
from telegram import Update, BotCommand, MenuButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .data import *
from .misc import *
from . import media
import requests
import asyncio
from progress.bar import Bar
from multiprocessing import Pool

async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_auth(user_name, context):
        return

    btn = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])
    keyboard = InlineKeyboardMarkup([[btn]])

    await context.bot.send_message(chat_id, '📂 Send two files to compare', reply_markup=keyboard)
    context.user_data['files'] = []

    return steps['COMPARE']['GET_FILES']

async def get_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    d = update.effective_message.document.file_id
    context.user_data['files'].append(d)

    if len(context.user_data['files']) != 2:
        return steps['COMPARE']['GET_FILES']

    f1 = None
    f2 = None

    try:
        f1 = await context.bot.get_file(context.user_data['files'][0])
        f2 = await context.bot.get_file(context.user_data['files'][1])
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['PANEL']['COMPARE'])
        btn_2 = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, f'📂 Invalid attachments', reply_markup=keyboard)
        return steps['PANEL']['SELECTION']
    
    await f1.download_to_drive('data/tmp')
    f1 = open('data/tmp', encoding='utf-8')
    s1 = f1.read()
    f1.close()

    await f2.download_to_drive('data/tmp')
    f2 = open('data/tmp', encoding='utf-8')
    s2 = f2.read()
    f2.close()

    context.user_data['files'] = [s1, s2]

    btn_1 = InlineKeyboardButton('🟡 Matches', callback_data=steps['COMPARE']['MATCH'])
    btn_2 = InlineKeyboardButton('🟣 Differences', callback_data=steps['COMPARE']['DIFF'])
    btn_3 = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

    keyboard = InlineKeyboardMarkup([[btn_1], [btn_2], [btn_3]])

    await context.bot.send_message(chat_id, f'📂 Choose an operation to perform', reply_markup=keyboard)

    return steps['COMPARE']['SELECTION']


async def compare_diff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    s1 = context.user_data['files'][0].split('\n')
    s2 = context.user_data['files'][1].split('\n')

    r = []
    for u in s1:
        if not u in s2:
            r.append(u)
    
    for u in s2:
        if not u in s1:
            r.append(u)
            
    s = '\n'.join(r) + '\n'

    f = open('data/tmp', 'w', encoding='utf-8')
    f.write(s)
    f.close()

    btn = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

    keyboard = InlineKeyboardMarkup([[btn]])
    await context.bot.send_document(chat_id, open('data/tmp', encoding='utf-8'), reply_markup=keyboard, filename='matches.txt')

    return steps['PANEL']['SELECTION']

async def compare_match_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    s1 = context.user_data['files'][0].split('\n')
    s2 = context.user_data['files'][1].split('\n')

    r = []
    for u in s1:
        if u in s2:
            r.append(u)
            
    s = '\n'.join(r) + '\n'

    f = open('data/tmp', 'w', encoding='utf-8')
    f.write(s)
    f.close()

    btn = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

    keyboard = InlineKeyboardMarkup([[btn]])
    await context.bot.send_document(chat_id, open('data/tmp', encoding='utf-8'), reply_markup=keyboard, filename='differences.txt')

    return steps['PANEL']['SELECTION']