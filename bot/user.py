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
import panel.user.misc.user as rocket_user
import panel.user.misc.followers as rocket_followers
import panel.user.misc.following as rocket_following
import panel.user.misc.media as rocket_media

async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_auth(user_name, context):
        return
    
    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api

    await context.bot.send_message(chat_id, 'Enter username')

    return steps['USER']['GET_USER']

async def get_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile = update.message.text.strip().lower()
    context.user_data['profile'] = profile
    profile_data = {}
    profile_info = {}

    try:
        profile_data = rocket_user.get_user_info(context.user_data['api'], profile)
        profile_info = rocket_user.get_user_info_by_id(context.user_data['api'], profile_data['id'])
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['PANEL']['USER'])
        btn_2 = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)
        return steps['PANEL']['SELECTION']
    
    context.user_data['profile_data'] = profile_data
    context.user_data['profile_info'] = profile_info

    return await menu_command(update, context)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    context.user_data['data'] = None
    context.user_data['count'] = None
    context.user_data['max_id'] = None
    context.user_data['media'] = None

    profile_data = context.user_data['profile_data']
    res = requests.get(profile_data['profile_pic_url_hd'])
    fw = open('data/tmp.png', 'wb')
    fw.write(res.content)
    fw.close()

    btn_followers = InlineKeyboardButton('👥 Followers', callback_data=steps['USER']['FOLLOWERS'])
    btn_following = InlineKeyboardButton('👥 Following', callback_data=steps['USER']['FOLLOWING'])
    btn_media = InlineKeyboardButton('🎞 Media', callback_data=steps['USER']['MEDIA'])
    btn_info = InlineKeyboardButton('ℹ Info', callback_data=steps['USER']['INFO'])
    btn_main_menu = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

    keyboard = InlineKeyboardMarkup([[btn_followers, btn_following], [btn_media, btn_info], [btn_main_menu]])

    await context.bot.send_photo(chat_id, open('data/tmp.png', 'rb'), caption=f'@{profile_data["username"]}', reply_markup=keyboard)

    return steps['USER']['SELECTION']

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile_info = rocket_user.parse_user_data(context.user_data['profile_info'])
    msg = ''

    for (k, v) in profile_info.items():
        msg += f'{k}: {v}\n'

    btn = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])
    keyboard = InlineKeyboardMarkup([[btn]])

    await context.bot.send_message(chat_id, msg, reply_markup=keyboard)

    return steps['USER']['SELECTION']


async def followers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile_info = context.user_data['profile_info']

    await context.bot.send_message(chat_id, f'👥 @{profile_info["username"]} has {profile_info["follower_count"]} followers \nHow many followers to parse?')

    return steps['USER']['FOLLOWERS_GET']
    
async def followers_get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile_info = context.user_data['profile_info']
    count = update.message.text

    try:
        count = int(count)
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['USER']['FOLLOWERS'])
        btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, f'{count} is invalid count', reply_markup=keyboard)
        return steps['USER']['SELECTION']
    
    count = min(count, int(profile_info['follower_count']))

    msg = await context.bot.send_message(chat_id, f'👥 Getting followers `[0/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    
    data = []

    rocket_token = get_rocket_token()

    max_id = None

    while len(data) < count:
        (d, max_id, e) = rocket_followers.get_followers_noexcept_w_2(profile_info['pk'], rocket_token, max_id)
        data.extend(d)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['USER']['FOLLOWERS_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['USER']['FOLLOWERS_CONTINUE']

        msg = await msg.edit_text(f'👥 Getting followers `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'

    return await users_send_command(update, context)

async def followers_continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']

    count = context.user_data['count']
    data = context.user_data['data']
    max_id = context.user_data['max_id']

    msg = await context.bot.send_message(chat_id, f'👥 Getting followers `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    rocket_token = get_rocket_token()

    while len(data) < count:
        (d, max_id, e) = rocket_followers.get_followers_noexcept_w_2(profile_info['pk'], rocket_token, max_id)
        data.extend(d)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['USER']['FOLLOWERS_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['USER']['FOLLOWERS_CONTINUE']

        msg = await msg.edit_text(f'👥 Getting followers `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'

    return await users_send_command(update, context)


async def following_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile_info = context.user_data['profile_info']

    await context.bot.send_message(chat_id, f'👥 @{profile_info["username"]} has {profile_info["following_count"]} followings \nHow many followers to parse?')

    return steps['USER']['FOLLOWING_GET']

async def following_get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile_info = context.user_data['profile_info']
    count = update.message.text

    try:
        count = int(count)
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['USER']['FOLLOWING'])
        btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, f'{count} is invalid count', reply_markup=keyboard)
        return steps['USER']['SELECTION']
    
    count = min(count, int(profile_info['following_count']))

    msg = await context.bot.send_message(chat_id, f'👥 Getting following\.\.\.', parse_mode=ParseMode.MARKDOWN_V2)
    data = []
    rocket_token = get_rocket_token()
    req_count = (count - 1) // 100 + 1

    with Pool(processes=8) as pool:
        for i in range(req_count):
            pool.apply_async(rocket_following.get_followings_noexcept_w, (profile_info['pk'], rocket_token, str(i * 100)), callback=lambda d: (data.append(d)))
        pool.close()
        pool.join()

    e_count = 0
    failed = []
    for (d, e) in data:
        if e != None:
            e_count += 1
            failed.append(d)
    
    d = []
    data = list(filter(lambda v: v[1] == None, data))
    [d.extend(v[0]) for v in data]

    if e_count != 0:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['USER']['FOLLOWING_CONTINUE'])
        btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        context.user_data['data'] = d
        context.user_data['failed'] = failed
        context.user_data['count'] = count

        await context.bot.send_message(chat_id, f'*{e_count}* requests failed', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

        return steps['USER']['FOLLOWING_CONTINUE']

    msg = await msg.edit_text(f'👥 Getting following complete ✅', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = d
    context.user_data['count'] = len(data)
    context.user_data['iid'] = 'pk'

    return await users_send_command(update, context)

async def following_continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']

    count = context.user_data['count']
    data = context.user_data['data']
    failed = context.user_data['failed']

    msg = await context.bot.send_message(chat_id, f'👥 Getting following\.\.\.', parse_mode=ParseMode.MARKDOWN_V2)
    rocket_token = get_rocket_token()
    e_count = 0

    with Pool(processes=8) as pool:
        for i in failed:
            pool.apply_async(rocket_following.get_followings_noexcept_w, (profile_info['pk'], rocket_token, i), callback=lambda d: (data.append(d)))
        pool.close()
        pool.join()

    failed = []
    for (d, e) in data:
        if e != None:
            e_count += 1
            failed.append(d)

    d = []
    data = list(filter(lambda v: v[1] == None, data))
    [d.extend(v[0]) for v in data]

    if e_count != 0:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['USER']['FOLLOWING_CONTINUE'])
        btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        context.user_data['data'] = d
        context.user_data['failed'] = failed
        context.user_data['count'] = count

        await context.bot.send_message(chat_id, f'*{e_count}* requests failed, do you want to retry them?', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

        return steps['USER']['FOLLOWING_CONTINUE']

    msg = await msg.edit_text(f'👥 Getting following complete ✅', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = d
    context.user_data['count'] = len(data)
    context.user_data['iid'] = 'pk'

    return await users_send_command(update, context)


async def media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile_info = context.user_data['profile_info']

    await context.bot.send_message(chat_id, f'🎞 @{profile_info["username"]} has {profile_info["media_count"]} posts \nHow many posts to parse?')

    return steps['USER']['MEDIA_GET']

async def media_get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    profile_info = context.user_data['profile_info']
    count = update.message.text

    try:
        count = int(count)
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['USER']['MEDIA'])
        btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, f'{count} is invalid count', reply_markup=keyboard)
        return steps['USER']['SELECTION']
    
    count = min(count, int(profile_info['media_count']))

    msg = await context.bot.send_message(chat_id, f'🎞 Getting media `[0/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    
    data = []

    rocket_token = get_rocket_token()

    max_id = None

    while len(data) < count:
        (d, max_id, e) = rocket_media.get_media_noexcept_w(int(profile_info['pk']), rocket_token, max_id)
        data.extend(d)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['USER']['MEDIA_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['media'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['USER']['MEDIA_CONTINUE']

        msg = await msg.edit_text(f'🎞 Getting media `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['media'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'

    return await media.menu_command(update, context)

async def media_continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id
    profile_info = context.user_data['profile_info']

    count = context.user_data['count']
    data = context.user_data['media']
    max_id = context.user_data['max_id']

    msg = await context.bot.send_message(chat_id, f'🎞 Getting media `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    rocket_token = get_rocket_token()

    while len(data) < count:
        (d, max_id, e) = rocket_media.get_media_noexcept_w(int(profile_info['pk']), rocket_token, max_id)
        data.extend(d)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['USER']['MEDIA_CONTINUE'])
            btn_2 = InlineKeyboardButton('👤 User menu', callback_data=steps['PANEL']['USER'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['media'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['USER']['MEDIA_CONTINUE']

        msg = await msg.edit_text(f'🎞 Getting media `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['media'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'

    return await media.menu_command(update, context)

