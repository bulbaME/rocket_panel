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


from rocketapi import InstagramAPI
from panel.misc import get_token as get_rocket_token
from panel.misc import check_response
import panel.hashtag.media as rocket_hashtag

async def hashtag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_auth(user_name, context):
        return
    
    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api

    await context.bot.send_message(chat_id, 'Enter hashtag')

    return steps['HASHTAG']['GET_HASHTAG']

async def get_hashtag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    hashtag = update.message.text.strip().lower()
    context.user_data['hashtag'] = hashtag
    data = {}

    try:
        data = context.user_data['api'].get_hashtag_info(hashtag)
        check_response(data)
        data = data['data']
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['PANEL']['HASHTAG'])
        btn_2 = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)
        return steps['PANEL']['SELECTION']
    
    context.user_data['hashtag_data'] = data

    return await menu_command(update, context)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    hashtag_data = context.user_data['hashtag_data']
    context.user_data['profile_info'] = { 'username': hashtag_data['name'] }

    res = requests.get(hashtag_data['profile_pic_url'])
    fw = open('data/tmp.png', 'wb')
    fw.write(res.content)
    fw.close()

    btn_media = InlineKeyboardButton('👥 Users', callback_data=steps['HASHTAG']['MEDIA'])
    btn_menu = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])
    keyboard = InlineKeyboardMarkup([[btn_media], [btn_menu]])

    await context.bot.send_photo(chat_id, open('data/tmp.png', 'rb'), caption=f'#{hashtag_data["name"]}', reply_markup=keyboard)

    return steps['HASHTAG']['SELECTION']

async def media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    hashtag = context.user_data['hashtag']
    hashtag_data = context.user_data['hashtag_data']

    await context.bot.send_message(chat_id, f'#️⃣ #{hashtag} has {hashtag_data["media_count"]} posts \nHow many posts to parse?')

    return steps['HASHTAG']['MEDIA_GET']
    
async def media_get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    hashtag = context.user_data['hashtag']
    hashtag_data = context.user_data['hashtag_data']
    count = update.message.text

    try:
        count = int(count)
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['HASHTAG']['MEDIA'])
        btn_2 = InlineKeyboardButton('#️⃣ Hashtag menu', callback_data=steps['PANEL']['HASHTAG'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, f'{count} is invalid count', reply_markup=keyboard)
        return steps['HASHTAG']['SELECTION']
    
    count = min(count, int(hashtag_data['media_count']))

    msg = await context.bot.send_message(chat_id, f'\#️⃣ Getting posts `[0/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    
    data = []
    usernames_in = set()

    rocket_token = get_rocket_token()

    max_id = (None, None)

    while len(data) < count:
        (d, max_id, e) = rocket_hashtag.get_media_noexcept_w(hashtag, rocket_token, max_id)
        d_e = []
        for u in d:
            if not u['username'] in usernames_in:
                d_e.append(u)
                usernames_in.add(u['username'])

        data.extend(d_e)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['HASHTAG']['MEDIA_CONTINUE'])
            btn_2 = InlineKeyboardButton('#️⃣ Hashtag menu', callback_data=steps['PANEL']['HASHTAG'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id
            context.user_data['usernames_in'] = usernames_in

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['HASHTAG']['MEDIA_CONTINUE']

        if len(d) != 0:
            msg = await msg.edit_text(f'\#️⃣ Getting posts `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'
    context.user_data['back_txt'] = '#️⃣ Hashtag menu'
    context.user_data['back_data'] = steps['HASHTAG']['SELECTION']

    return await users_send_command(update, context)

async def media_continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    hashtag = context.user_data['hashtag']
    hashtag_data = context.user_data['hashtag_data']
    data = context.user_data['data']
    count = context.user_data['count']
    max_id = context.user_data['max_id']

    usernames_in = context.user_data['usernames_in']

    msg = await context.bot.send_message(chat_id, f'\#️⃣ Getting posts `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    rocket_token = get_rocket_token()

    while len(data) < count:
        (d, max_id, e) = rocket_hashtag.get_media_noexcept_w(hashtag, rocket_token, max_id)
        d_e = []
        for u in d:
            if not u['username'] in usernames_in:
                d_e.append(u)
                usernames_in.add(u['username'])

        data.extend(d_e)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['HASHTAG']['MEDIA_CONTINUE'])
            btn_2 = InlineKeyboardButton('#️⃣ Hashtag menu', callback_data=steps['PANEL']['HASHTAG'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id
            context.user_data['usernames_in'] = usernames_in

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['HASHTAG']['MEDIA_CONTINUE']

        if len(d) != 0:
            msg = await msg.edit_text(f'\#️⃣ Getting posts `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'
    context.user_data['back_txt'] = '#️⃣ Hashtag menu'
    context.user_data['back_data'] = steps['HASHTAG']['SELECTION']

    return await users_send_command(update, context)