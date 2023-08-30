from .misc.user import get_user_info_by_id, get_user_info, parse_user_data
from .followers import action_followers
from .followings import action_following
from .media import action_media

def user_actions(api):
    user_name = input('Instagram handle - @')
    user_data = {}
    user_id_data = {}

    while True:
        try:
            print('\nRetrieving info...')
            user_data = get_user_info(api, user_name)
            user_id_data = get_user_info_by_id(api, int(user_data['id']))
            break
        except BaseException as e:
            print(e)
            if input('Repeat? (y/n): ').lower().strip() != 'y':
                return
            
    print('Info retrieved')

    while True:
        print(f'\n@{user_name}')
        c = input('> ').strip()

        if c == 'help':
            print(f'''Commands:
    following - retrieve user followings
    followers - retrieve user followers
    media - retrieve user media
    info - retrive user information
    exit - close handle interface''')
        elif c == 'exit':
            return
        elif c == 'followers':
            action_followers(api, user_id_data)
        elif c == 'following':
            action_following(api, user_id_data)
        elif c == 'media':
            action_media(api, user_id_data)
        elif c == 'info':
            info = parse_user_data(user_id_data)
            for (k, v) in info.items():
                print(f'{k}: {v}')
        else:
            print('Incorrect command, try "help"')