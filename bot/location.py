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
import panel.location.media as rocket_location

async def location_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_auth(user_name, context):
        return
    
    api = InstagramAPI(get_rocket_token())
    context.user_data['api'] = api

    await context.bot.send_message(chat_id, 'Enter location id')

    return steps['LOCATION']['GET_LOCATION']

async def get_location_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    location = update.message.text.strip().lower()
    context.user_data['location'] = location
    data = {}

    try:
        data = context.user_data['api'].get_location_info(location)
        check_response(data)
        data = data['native_location_data']['location_info']
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['PANEL']['LOCATION'])
        btn_2 = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)
        return steps['PANEL']['SELECTION']
    
    context.user_data['location_data'] = data

    return await menu_command(update, context)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    location_data = context.user_data['location_data']
    context.user_data['profile_info'] = { 'username': location_data['name'] }

    btn_media = InlineKeyboardButton('👥 Users', callback_data=steps['LOCATION']['MEDIA'])
    btn_menu = InlineKeyboardButton('🕹 Main menu', callback_data=steps['PANEL']['ENTRY'])
    keyboard = InlineKeyboardMarkup([[btn_media], [btn_menu]])

    try:
        await context.bot.send_location(chat_id, latitude=float(location_data['lat']), longtitude=float(location_data['lng']), reply_markup=keyboard)
    except BaseException:
        await context.bot.send_message(chat_id, f'📍 {location_data["name"]}', reply_markup=keyboard)

    return steps['LOCATION']['SELECTION']

async def media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    location_data = context.user_data['location_data']

    await context.bot.send_message(chat_id, f'📍 {location_data["name"]} \nHow many posts to parse?')

    return steps['LOCATION']['MEDIA_GET']
    
async def media_get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    location_data = context.user_data['location_data']
    count = update.message.text

    try:
        count = int(count)
    except BaseException as e:
        btn_1 = InlineKeyboardButton('🔄 Retry', callback_data=steps['LOCATION']['MEDIA'])
        btn_2 = InlineKeyboardButton('📍 Location menu', callback_data=steps['PANEL']['LOCATION'])

        keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

        await context.bot.send_message(chat_id, f'{count} is invalid count', reply_markup=keyboard)
        return steps['LOCATION']['SELECTION']

    msg = await context.bot.send_message(chat_id, f'📍 Getting posts `[0/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    
    data = []
    usernames_in = set()

    rocket_token = get_rocket_token()

    max_id = (None, None)

    while len(data) < count:
        (d, max_id, e) = rocket_location.get_media_noexcept_w(location_data['location_id'], rocket_token, max_id)
        d_e = []
        for u in d:
            if not u['username'] in usernames_in:
                d_e.append(u)
                usernames_in.add(u['username'])

        data.extend(d_e)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['LOCATION']['MEDIA_CONTINUE'])
            btn_2 = InlineKeyboardButton('📍 Location menu', callback_data=steps['PANEL']['LOCATION'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id
            context.user_data['usernames_in'] = usernames_in

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['LOCATION']['MEDIA_CONTINUE']

        msg = await msg.edit_text(f'📍 Location menu `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'
    context.user_data['back_txt'] = '📍 Location menu'
    context.user_data['back_data'] = steps['LOCATION']['SELECTION']

    return await users_send_command(update, context)

async def media_continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    location_data = context.user_data['location_data']
    data = context.user_data['data']
    count = context.user_data['count']
    max_id = context.user_data['max_id']

    usernames_in = context.user_data['usernames_in']

    msg = await context.bot.send_message(chat_id, f'📍 Location menu `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)
    rocket_token = get_rocket_token()

    while len(data) < count:
        (d, max_id, e) = rocket_location.get_media_noexcept_w(location_data['location_id'], rocket_token, max_id)
        d_e = []
        for u in d:
            if not u['username'] in usernames_in:
                d_e.append(u)
                usernames_in.add(u['username'])

        data.extend(d_e)

        if e != None:
            btn_1 = InlineKeyboardButton('▶ Continue', callback_data=steps['LOCATION']['MEDIA_CONTINUE'])
            btn_2 = InlineKeyboardButton('📍 Location menu', callback_data=steps['PANEL']['LOCATION'])

            keyboard = InlineKeyboardMarkup([[btn_1], [btn_2]])

            context.user_data['data'] = data
            context.user_data['count'] = count
            context.user_data['max_id'] = max_id
            context.user_data['usernames_in'] = usernames_in

            await context.bot.send_message(chat_id, error_msg(e), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard)

            return steps['LOCATION']['MEDIA_CONTINUE']

        msg = await msg.edit_text(f'📍 Getting posts `[{len(data)}/{count}]`', parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data['data'] = data
    context.user_data['count'] = len(data)
    context.user_data['max_id'] = max_id
    context.user_data['iid'] = 'pk'
    context.user_data['back_txt'] = '📍 Location menu'
    context.user_data['back_data'] = steps['LOCATION']['SELECTION']

    return await users_send_command(update, context)