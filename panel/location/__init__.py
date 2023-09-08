from misc import check_response
from .media import action_media
from misc import print_g, print_e, RB, RS

def location_actions(api):
    id = input('Instagram location id - !').strip()

    try: 
        id = int(id)
    except BaseException:
        print_e('Invalid location id')
        return

    data = {}

    while True:
        try:
            print_g('\nRetrieving info...')
            data = api.get_location_info(id)
            check_response(data)
            data = data['native_location_data']['location_info']
            break
        except BaseException as e:
            print_e(e)
            if input('Repeat? (y/n): ').lower().strip() != 'y':
                return
            
    print('Info retrieved')

    while True:
        print(f'\n! {data["name"]}')
        c = input(f'!> ').strip().lower()

        if c == 'info':
            print(data['name'])
            print(f'Website: {data["website"]}')
            print(f'Phone: {data["phone"]}')
            print(f'Adress: {data["location_address"]}')
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
