import telegram
from telegram import Update, BotCommand, MenuButton
from telegram.ext import ContextTypes
from .data import *
from .misc import steps
import yaml

PASSCODE = yaml.safe_load(open('credentials.yaml'))['tg']['passcode']

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = data_users_get()
    user_name = update.effective_user.username
    chat_id = update.effective_chat.id

    if user_name in users.keys() and not users[user_name]['auth']:
        await context.bot.send_message(chat_id, 'Send the passcode')

    return steps['AUTH']['PASSCODE']

async def passcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = data_users_get()
    user_name = update.effective_user.username

    if update.message.text.strip() == PASSCODE:
        await context.bot.send_message(chat_id, '✅ Authorization complete [/menu]')
        user = users[user_name]
        user['auth'] = True
        context.user_data['auth'] = True
        data_users_set(user_name, user)

        menu_command = BotCommand('menu', 'Display menu 🚀')
        logout_command = BotCommand('logout', 'Logout 🔴')

        await context.bot.set_my_commands([menu_command, logout_command], scope=telegram.BotCommandScopeChat(chat_id))
        await context.bot.set_chat_menu_button(chat_id=chat_id, menu_button=MenuButton(MenuButton.COMMANDS))

        return steps['AUTH']['COMPLETE']
    else:
        await context.bot.send_message(chat_id, '❌ Incorrect passcode, try again')
        return steps['AUTH']['PASSCODE']