import logging
import telegram
from telegram import Update, MenuButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
import yaml

from .data import *
from . import auth
from . import panel
from . import user
from . import media
from . import hashtag
from . import location
from . import compare
from .misc import steps

TOKEN = yaml.safe_load(open('credentials.yaml'))['tg']['token']

logging.basicConfig(
    filename='logs.log',
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = data_users_get()
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if not user_name in users.keys() or not users[user_name]['auth']:
        btn = InlineKeyboardButton('Authenticate', callback_data=auth.steps['AUTH']['AUTH'])
        keyboard = InlineKeyboardMarkup([[btn]])
        await context.bot.send_message(chat_id, "🚀 Hello, you should complete authorization to continue", reply_markup=keyboard)

        d = {
            'auth': False,
            'chat_id': update.effective_chat.id
        }

        data_users_set(user_name, d)

        return steps['AUTH']['AUTH']
    else:
        await context.bot.send_message(chat_id, "🟢 You are authorized [/menu]")

        return steps['AUTH']['COMPLETE']

async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username

    if not user_auth(user_name, context):
        return
    
    users = data_users_get()
    user = users[user_name]
    user['auth'] = False

    data_users_set(user_name, user)
    context.user_data['auth'] = False

    await context.bot.delete_my_commands(scope=telegram.BotCommandScopeChat(chat_id))

    await context.bot.set_chat_menu_button(chat_id=chat_id, menu_button=MenuButton(MenuButton.DEFAULT))
    await context.bot.send_message(chat_id, '🔴 Loged out successfully [/start]')

def main():
    data_dir()
    application = ApplicationBuilder().token(TOKEN).build()

    # command handlers

    start_handler = CommandHandler('start', start_command)
    logout_handler = CommandHandler('logout', logout_command)
    menu_handler = CommandHandler('menu', panel.menu_command)

    # conversation handlers

    auth_conversation = ConversationHandler(
        [start_handler],
        {
            steps['AUTH']['AUTH']: [CallbackQueryHandler(auth.auth_command, pattern=f'^{steps["AUTH"]["AUTH"]}$')],
            steps['AUTH']['PASSCODE']: [MessageHandler(filters.TEXT, auth.passcode_command)],
            steps['AUTH']['COMPLETE']: [start_handler]
        },
        [start_handler]
    )

    menu_conversation = ConversationHandler(
        [menu_handler],
        {
            steps['PANEL']['SELECTION']: [
                CallbackQueryHandler(user.user_command, pattern=f'^{steps["PANEL"]["USER"]}$'), 
                CallbackQueryHandler(location.location_command, pattern=f'^{steps["PANEL"]["LOCATION"]}$'), 
                CallbackQueryHandler(hashtag.hashtag_command, pattern=f'^{steps["PANEL"]["HASHTAG"]}$'),
                CallbackQueryHandler(compare.compare_command, pattern=f'^{steps["PANEL"]["COMPARE"]}$'),
                CallbackQueryHandler(panel.menu_command, pattern=f'^{steps["PANEL"]["ENTRY"]}$'),
                menu_handler
            ],
            steps['USER']['GET_USER']: [MessageHandler(filters.TEXT, user.get_user_command)],
            steps['USER']['SELECTION']: [
                CallbackQueryHandler(user.info_command, pattern=f'^{steps["USER"]["INFO"]}$'), 
                CallbackQueryHandler(user.followers_command, pattern=f'^{steps["USER"]["FOLLOWERS"]}$'), 
                CallbackQueryHandler(user.following_command, pattern=f'^{steps["USER"]["FOLLOWING"]}$'),
                CallbackQueryHandler(user.media_command, pattern=f'^{steps["USER"]["MEDIA"]}$'),
                CallbackQueryHandler(user.menu_command, pattern=f'^{steps["PANEL"]["USER"]}$'),
                CallbackQueryHandler(panel.menu_command, pattern=f'^{steps["PANEL"]["ENTRY"]}$')
            ],
            steps['USER']['FOLLOWERS_GET']: [MessageHandler(filters.TEXT, user.followers_get_command)],
            steps['USER']['FOLLOWERS_CONTINUE']: [
                CallbackQueryHandler(user.followers_continue_command, pattern=f'^{steps["USER"]["FOLLOWERS_CONTINUE"]}$'),
                CallbackQueryHandler(user.menu_command, pattern=f'^{steps["PANEL"]["USER"]}$')
            ],
            steps['USER']['FOLLOWING_GET']: [MessageHandler(filters.TEXT, user.following_get_command)],
            steps['USER']['FOLLOWING_CONTINUE']: [
                CallbackQueryHandler(user.following_continue_command, pattern=f'^{steps["USER"]["FOLLOWING_CONTINUE"]}$'),
                CallbackQueryHandler(user.menu_command, pattern=f'^{steps["PANEL"]["USER"]}$')
            ],
            steps['USER']['MEDIA_GET']: [MessageHandler(filters.TEXT, user.media_get_command)],
            steps['USER']['MEDIA_CONTINUE']: [
                CallbackQueryHandler(user.media_continue_command, pattern=f'^{steps["USER"]["MEDIA_CONTINUE"]}$'),
                CallbackQueryHandler(user.menu_command, pattern=f'^{steps["PANEL"]["USER"]}$')
            ],
            steps['MEDIA']['ENTRY']: [
                CallbackQueryHandler(media.show_command, pattern=f'^{steps["MEDIA"]["SHOW"]}$'),
                CallbackQueryHandler(media.select_command, pattern=f'^{steps["MEDIA"]["SELECT"]}$'),
                CallbackQueryHandler(user.menu_command, pattern=f'^{steps["PANEL"]["USER"]}$'),
            ],
            steps['MEDIA']['SHOW']: [
                CallbackQueryHandler(media.show_select_command, pattern=f'^(?:100[0-9]|10[1-9][0-9]|1[1-4][0-9]{{2}})$'),
                CallbackQueryHandler(media.menu_command, pattern=f'^{steps["MEDIA"]["ENTRY"]}$'),
            ],
            steps['MEDIA']['SELECT']: [
                CallbackQueryHandler(media.select_menu_command, pattern=f'^(?:100[0-9]|10[1-9][0-9]|1[1-4][0-9]{{2}})$'),
                CallbackQueryHandler(media.menu_command, pattern=f'^{steps["MEDIA"]["ENTRY"]}$'),
            ],
            steps['MEDIA']['SELECT_MENU']: [
                CallbackQueryHandler(media.select_menu_command, pattern=f'^(?:100[0-9]|10[1-9][0-9]|1[1-4][0-9]{{2}})$'),
                CallbackQueryHandler(media.menu_command, pattern=f'^{steps["MEDIA"]["ENTRY"]}$'),
            ],
            steps['MEDIA']['POST']: [
                CallbackQueryHandler(media.likes_command, pattern=f'^{steps["MEDIA"]["LIKES"]}$'),
                CallbackQueryHandler(media.comments_command, pattern=f'^{steps["MEDIA"]["COMMENTS"]}$'),
                CallbackQueryHandler(media.menu_command, pattern=f'^{steps["MEDIA"]["ENTRY"]}$'),
            ],
            steps['MEDIA']['LIKES_CONTINUE']: [
                CallbackQueryHandler(media.comments_continue_command, pattern=f'^{steps["MEDIA"]["LIKES_CONTINUE"]}$'),
                CallbackQueryHandler(media.menu_command, pattern=f'^{steps["MEDIA"]["ENTRY"]}$')
            ],
            steps['MEDIA']['COMMENTS_CONTINUE']: [
                CallbackQueryHandler(media.likes_continue_command, pattern=f'^{steps["MEDIA"]["COMMENTS_CONTINUE"]}$'),
                CallbackQueryHandler(media.menu_command, pattern=f'^{steps["MEDIA"]["ENTRY"]}$')
            ],
            steps['USER']['USERS_SEND']: [
                CallbackQueryHandler(user.users_send_file_command, pattern=f'^{steps["USER"]["USERS_SEND"]}$', block=False),
                CallbackQueryHandler(user.users_info_send_file_command, pattern=f'^{steps["USER"]["USERS_INFO_SEND"]}$', block=False),
                CallbackQueryHandler(user.menu_command, pattern=f'^{steps["PANEL"]["USER"]}$'),
                CallbackQueryHandler(hashtag.menu_command, pattern=f'^{steps["HASHTAG"]["SELECTION"]}$'),
                CallbackQueryHandler(location.menu_command, pattern=f'^{steps["LOCATION"]["SELECTION"]}$'),
                CallbackQueryHandler(media.menu_command, pattern=f'^{steps["MEDIA"]["ENTRY"]}$'),
                CallbackQueryHandler(panel.menu_command, pattern=f'^{steps["PANEL"]["ENTRY"]}$'),
            ],
            steps['HASHTAG']['GET_HASHTAG']: [MessageHandler(filters.TEXT, hashtag.get_hashtag_command)],
            steps['HASHTAG']['SELECTION']: [
                CallbackQueryHandler(hashtag.menu_command, pattern=f'^{steps["PANEL"]["HASHTAG"]}$'),
                CallbackQueryHandler(hashtag.media_command, pattern=f'^{steps["HASHTAG"]["MEDIA"]}$'),
                CallbackQueryHandler(panel.menu_command, pattern=f'^{steps["PANEL"]["ENTRY"]}$'),
            ],
            steps['HASHTAG']['MEDIA_GET']: [MessageHandler(filters.TEXT, hashtag.media_get_command)],
            steps['HASHTAG']['MEDIA_CONTINUE']: [
                CallbackQueryHandler(hashtag.media_continue_command, pattern=f'^{steps["HASHTAG"]["MEDIA_CONTINUE"]}$'),
                CallbackQueryHandler(hashtag.menu_command, pattern=f'^{steps["HASHTAG"]["SELECTION"]}$')
            ],
            steps['LOCATION']['GET_LOCATION']: [MessageHandler(filters.TEXT, location.get_location_command)],
            steps['LOCATION']['SELECTION']: [
                CallbackQueryHandler(location.menu_command, pattern=f'^{steps["PANEL"]["LOCATION"]}$'),
                CallbackQueryHandler(location.media_command, pattern=f'^{steps["LOCATION"]["MEDIA"]}$'),
                CallbackQueryHandler(panel.menu_command, pattern=f'^{steps["PANEL"]["ENTRY"]}$'),
            ],
            steps['LOCATION']['MEDIA_GET']: [MessageHandler(filters.TEXT, location.media_get_command)],
            steps['LOCATION']['MEDIA_CONTINUE']: [
                CallbackQueryHandler(location.media_continue_command, pattern=f'^{steps["LOCATION"]["MEDIA_CONTINUE"]}$'),
                CallbackQueryHandler(location.menu_command, pattern=f'^{steps["LOCATION"]["SELECTION"]}$')
            ],
            steps['COMPARE']['GET_FILES']: [
                MessageHandler(filters.Document.TXT, compare.get_files_command),
                CallbackQueryHandler(panel.menu_command, pattern=f'^{steps["PANEL"]["ENTRY"]}$')
            ],
            steps['COMPARE']['SELECTION']: [
                CallbackQueryHandler(compare.compare_match_command, pattern=f'^{steps["COMPARE"]["MATCH"]}$'),
                CallbackQueryHandler(compare.compare_diff_command, pattern=f'^{steps["COMPARE"]["DIFF"]}$'),
                CallbackQueryHandler(panel.menu_command, pattern=f'^{steps["PANEL"]["ENTRY"]}$')
            ],
        },
        [],
        allow_reentry=True
    )

    # add handlers

    application.add_handler(auth_conversation)
    application.add_handler(menu_conversation)

    application.add_handler(logout_handler)

    application.run_polling()
    