import telegram
from telegram import Update, BotCommand, MenuButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .data import *
from multiprocessing import Pool

from panel.misc import get_token as get_rocket_token
import panel.user.misc.user as rocket_user

COMMAND_I = 0

def gci():
    global COMMAND_I

    COMMAND_I += 1
    return COMMAND_I

def error_msg(log):
    msg = f'*An error occured:* `{log}`'
    return msg

steps = {
    'AUTH': {
        'AUTH': gci(),
        'PASSCODE': gci(),
        'COMPLETE': gci()
    },
    'PANEL': {
        'ENTRY': gci(),
        'USER': gci(),
        'HASHTAG': gci(),
        'LOCATION': gci(),
        'COMPARE': gci(),
        'SELECTION': gci()
    },
    'USER': {
        'GET_USER': gci(),
        'INFO': gci(),
        'FOLLOWERS': gci(),
        'FOLLOWERS_GET': gci(),
        'FOLLOWERS_CONTINUE': gci(),
        'FOLLOWING': gci(),
        'FOLLOWING_GET': gci(),
        'FOLLOWING_CONTINUE': gci(),
        'MEDIA': gci(),
        'MEDIA_GET': gci(),
        'MEDIA_CONTINUE': gci(),
        'USERS_SEND': gci(),
        'USERS_INFO_PROC': gci(),
        'USERS_INFO_SEND': gci(),
        'SELECTION': gci()
    },
    'MEDIA': {
        'ENTRY': gci(),
        'SHOW': gci(),
        'SHOW_SELECT': gci(),
        'SELECT': gci(),
        'SELECT_MENU': gci(),
        'POST': gci(),
        'LIKES': gci(),
        'LIKES_CONTINUE': gci(),
        'COMMENTS': gci(),
        'COMMENTS_CONTINUE': gci(),
    },
    'HASHTAG': {
        'GET_HASHTAG': gci(),
        'SELECTION': gci(),
        'MEDIA': gci(),
        'MEDIA_GET': gci(),
        'MEDIA_CONTINUE': gci(),
        'INFO': gci()
    },
    'LOCATION': {
        'GET_LOCATION': gci(),
        'SELECTION': gci(),
        'MEDIA': gci(),
        'MEDIA_GET': gci(),
        'MEDIA_CONTINUE': gci(),
        'INFO': gci()
    },
    'COMPARE': {
        'GET_FILES': gci(),
        'SELECTION': gci(),
        'MATCH': gci(),
        'DIFF': gci(),
    }
}

async def users_send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    btn_1 = InlineKeyboardButton('👥 Only usernames', callback_data=steps['USER']['USERS_SEND'])
    btn_2 = InlineKeyboardButton('📃 Each user data', callback_data=steps['USER']['USERS_INFO_SEND'])
    btn_3 = InlineKeyboardButton(context.user_data['back_txt'], callback_data=context.user_data['back_data'])

    keyboard = InlineKeyboardMarkup([[btn_1, btn_2], [btn_3]])

    await context.bot.send_message(chat_id, f'👥 {len(context.user_data["data"])} users retrieved from {context.user_data["profile_info"]["username"]}', reply_markup=keyboard)

    return steps['USER']['USERS_SEND']

async def users_send_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    users = context.user_data['data']
    users = [f['username'] for f in users]
    users = '\n'.join(users)

    fw = open('data/tmp', 'w')
    fw.write(users)
    fw.close()

    btn_1 = InlineKeyboardButton(context.user_data['back_txt'], callback_data=context.user_data['back_data'])
    btn_2 = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])
    keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

    await context.bot.send_document(chat_id, open('data/tmp'), reply_markup=keyboard, filename=f'{context.user_data["profile_info"]["username"]}.users.txt')

    return steps['USER']['USERS_SEND']

async def users_info_send_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    users = context.user_data['data']
    users_id = [f[context.user_data['iid']] for f in users]

    token = get_rocket_token()
    user_info = []

    msg = await context.bot.send_message(chat_id, f'👥 Getting users info\.\.\.', parse_mode=ParseMode.MARKDOWN_V2)

    with Pool(processes=8) as pool:
        for u in users_id:
            pool.apply_async(rocket_user.get_user_info_noexcept_w, (u, token), callback=lambda d: (user_info.append(d)))
        pool.close()
        pool.join()

    msg = await msg.edit_text(f'👥 Getting users info complete ✅', parse_mode=ParseMode.MARKDOWN_V2)

    if len(user_info) == 0:
        return steps['USER']['USERS_SEND']

    data = ', '.join(user_info[0].keys()) + '\n'

    for d in user_info:
        data += f'{", ".join(d.values())}\n'

    fw = open('data/tmp', 'w', encoding='utf-8')
    fw.write(data)
    fw.close()

    btn_1 = InlineKeyboardButton(context.user_data['back_txt'], callback_data=context.user_data['back_data'])
    btn_2 = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])
    keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

    await context.bot.send_document(chat_id, open('data/tmp', encoding='utf-8'), reply_markup=keyboard, filename=f'{context.user_data["profile_info"]["username"]}.users.csv')

    return steps['USER']['USERS_SEND']
