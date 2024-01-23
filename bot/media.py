import telegram
from telegram import Update, BotCommand, MenuButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from .data import *
from .misc import *
import requests
import asyncio
from progress.bar import Bar
from multiprocessing import Pool
from datetime import datetime

from rocketapi import InstagramAPI
from panel.misc import get_token as get_rocket_token
import panel.user.misc.media as rocket_media
import panel.user.misc.user as rocket_user

LIKE_FETCH_LIMIT_RATE = 0.1

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']

    if not user_auth(user_name, context):
        return
    
    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api

    # btn_show = InlineKeyboardButton('🖼 Show', callback_data=steps['MEDIA']['SHOW'])
    btn_select = InlineKeyboardButton('📃 Select', callback_data=steps['MEDIA']['SELECT'])
    btn_menu = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])
    keyboard = InlineKeyboardMarkup([[btn_select], [btn_menu]])

    await context.bot.send_message(chat_id, f'🎞 @{profile_info["username"]} media', reply_markup=keyboard)

    return steps['MEDIA']['ENTRY']

async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']
    
    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api
    media = context.user_data['media']

    buttons = []
    for i in range(len(media)):
        time = datetime.fromtimestamp(int(media[i]["taken_at"]))
        btn = InlineKeyboardButton(f'🖼 {time}', callback_data=str(i + 1000))
        buttons.append([btn])

    btn_menu = InlineKeyboardButton('🎞 Media menu', callback_data=steps['MEDIA']['ENTRY'])
    buttons.append([btn_menu])

    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(chat_id, f'🎞 {len(media)} posts from @{profile_info["username"]}', reply_markup=keyboard)

    return steps['MEDIA']['SHOW']

async def show_select_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']
    media_i = update.callback_query.data

    try:
        media_i = int(media_i) - 1000
    except BaseException:
        return steps['MEDIA']['SHOW']
    
    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api
    post = context.user_data['media'][media_i]
    time = datetime.fromtimestamp(int(post["taken_at"]))

    res = requests.get(post['carousel_media'][0]['image_versions2']['candidates'][0]['url'])
    fw = open('data/tmp.png', 'wb')
    fw.write(res.content)
    fw.close()

    caption = '<i>(no caption text)</i>'
    try: 
        caption = f'<b>{post["caption"]["text"]}</b>'
    except BaseException:
        pass
 
    await context.bot.send_photo(chat_id, open('data/tmp.png', 'rb'), caption=f'{caption}\n📅 {time}', parse_mode=ParseMode.HTML)

    return steps['MEDIA']['SHOW']

async def select_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']
    
    context.user_data['back_txt'] = '🎞 Media menu'
    context.user_data['back_data'] = steps['MEDIA']['ENTRY']

    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api
    media = context.user_data['media']

    buttons = []
    for i in range(len(media)):
        time = datetime.fromtimestamp(int(media[i]["taken_at"]))
        btn = InlineKeyboardButton(f'🖼 {time}', callback_data=str(i + 1000))
        buttons.append([btn])

    btn_menu = InlineKeyboardButton('🎞 Media menu', callback_data=steps['MEDIA']['ENTRY'])
    buttons.append([btn_menu])

    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(chat_id, f'🎞 {len(media)} posts from @{profile_info["username"]}', reply_markup=keyboard)

    return steps['MEDIA']['SELECT']

async def select_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']
    media_i = update.callback_query.data

    try:
        media_i = int(media_i) - 1000
    except BaseException:
        return steps['MEDIA']['SHOW']
    
    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api
    post = context.user_data['media'][media_i]
    time = datetime.fromtimestamp(int(post["taken_at"]))
    context.user_data['post'] = post
    url = ''

    try:
        url = post['carousel_media'][0]['image_versions2']['candidates'][0]['url']
    except BaseException:
        url = post['image_versions2']['candidates'][0]['url']

    res = requests.get(url)
    fw = open('data/tmp.png', 'wb')
    fw.write(res.content)
    fw.close()

    caption = '<i>(no caption text)</i>'
    try: 
        caption = f'<b>{post["caption"]["text"]}</b>'
    except BaseException:
        pass

    btn_likes = InlineKeyboardButton(f'👍 Likes', callback_data=steps['MEDIA']['LIKES'])
    btn_comments = InlineKeyboardButton(f'📃 Comments', callback_data=steps['MEDIA']['COMMENTS'])
    btn_menu = InlineKeyboardButton(f'🎞 Media menu', callback_data=steps['MEDIA']['ENTRY'])
    keyboard = InlineKeyboardMarkup([[btn_likes], [btn_comments], [btn_menu]])

    await context.bot.send_photo(chat_id, open('data/tmp.png', 'rb'), caption=f'{caption}\n📅 {time}', parse_mode=ParseMode.HTML, reply_markup=keyboard)

    return steps['MEDIA']['POST']

async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    post = context.user_data['post']
    count = int(post['like_count'])
    if count > 1000:
        count *= 0.85
        count = int(count)

    msg = await context.bot.send_message(chat_id, f'👍 Getting likes `[0/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    
    data = {}
    
    last_c = 0
    limit = count * LIKE_FETCH_LIMIT_RATE

    rocket_token = get_rocket_token()

    while len(data) < count and limit > 0:
        limit -= 1
        (p, e) = rocket_media.get_likes_noexcept_w(post['code'], rocket_token)
        for u in p: 
            data[u['pk']] = p

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['MEDIA']['LIKES_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['MEDIA']['LIKES_CONTINUE']

        if len(data) != last_c:
            msg = await msg.edit_text(f'👍 Getting likes `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

        last_c = len(data)

    data = [v for v in data.values()]

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['iid'] = 'pk'

    return await users_send_command(update, context)

async def likes_continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    post = context.user_data['post']

    count = context.user_data['count']
    data = context.user_data['data']

    msg = await context.bot.send_message(chat_id, f'👍 Getting likes `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    rocket_token = get_rocket_token()

    last_c = 0
    limit = count * LIKE_FETCH_LIMIT_RATE

    while len(data) < count and limit > 0:
        limit -= 1
        (p, e) = rocket_media.get_likes_noexcept_w(post['code'], rocket_token)
        for u in p:
            data[u['pk']] = u

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['MEDIA']['LIKES_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['MEDIA']['LIKES_CONTINUE']

        if len(data) != last_c:
            msg = await msg.edit_text(f'👍 Getting likes `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

        last_c = len(data)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['iid'] = 'pk'

    return await users_send_command(update, context)

async def comments_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    post = context.user_data['post']
    count = int(post['comment_count'])

    msg = await context.bot.send_message(chat_id, f'📃 Getting comments `[0/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    
    data = []

    rocket_token = get_rocket_token()

    max_id = None

    while len(data) < count:
        (d, max_id, e) = rocket_media.get_comments_noexcept_w(post['id'], rocket_token, max_id)
        data.extend(d)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['MEDIA']['COMMENTS_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['MEDIA']['COMMENTS_CONTINUE']

        if len(d) != 0:
            msg = await msg.edit_text(f'📃 Getting comments `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'username'

    return await users_send_command(update, context)

async def comments_continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    post = context.user_data['post']

    count = context.user_data['count']
    data = context.user_data['data']
    max_id = context.user_data['max_id']

    msg = await context.bot.send_message(chat_id, f'📃 Getting comments `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    rocket_token = get_rocket_token()

    while len(data) < count:
        (d, max_id, e) = rocket_media.get_comments_noexcept_w(post['id'], rocket_token, max_id)
        data.extend(d)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['MEDIA']['COMMENTS_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['MEDIA']['COMMENTS_CONTINUE']

        if len(d) != 0:
            msg = await msg.edit_text(f'📃 Getting comments `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'username'

    return await users_send_command(update, context)
