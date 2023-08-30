from misc import check_response
from .media import action_media

def hashtag_actions(api):
    name = input('Instagram hashtag - #').strip()
    data = {}

    while True:
        try:
            print('\nRetrieving info...')
            data = api.get_hashtag_info(name)
            check_response(data)
            data = data['data']
            break
        except BaseException as e:
            print(e)
            if input('Repeat? (y/n): ').lower().strip() != 'y':
                return
            
    print('Info retrieved')

    while True:
        print(f'\n#{name}')
        c = input('> ').strip().lower()

        if c == 'info':
            print(data['subtitle'])
            print(f'Posts: {data["media_count"]}')
        elif c == 'media':
            action_media(api, data)
        elif c == 'help':
            print(f'''Commands:
    media - retrieve hashtag media
    info - retrive hashtag information
    exit - close hashtag interface''')
        elif c == 'exit':
            break
        else:
            print('Invalid command, try "help"')
