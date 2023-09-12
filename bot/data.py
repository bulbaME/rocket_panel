import json
import os
from telegram.ext import ContextTypes

def user_auth(user_name, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if 'auth' in list(context.user_data.keys()):
        return context.user_data['auth']

    users = data_users_get()
    if user_name in users.keys() and users[user_name]['auth']:
        context.user_data['auth'] = True

        return True
    
    return False


def data_dir():
    if not os.path.isdir('data'):
        os.mkdir('data')

    if not os.path.isfile('data/users.json'):
        f = open('data/users.json', 'w')
        f.write('{}')
        f.close()
        
def data_users_get() -> dict:
    return json.load(open('data/users.json'))

def data_users_set(k, v):
    d = data_users_get()
    d[k] = v
    f = open('data/users.json', 'w')
    f.write(json.dumps(d))
    f.close()
