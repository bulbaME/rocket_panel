from .misc.followers import get_followers_1, get_followers_2, get_followers_pagintation_type
from .misc.user import get_users_info
from misc import print_g, print_e

def action_followers(api, user_data):
    count = 100

    print(f'\n@{user_data["username"]} has {user_data["follower_count"]} followers')

    try:
        t = input('Followers count (100): ')
        count = int(t)
    except BaseException:
        pass

    count = min(count, int(user_data['follower_count']))
    p = get_followers_pagintation_type(int(user_data['pk']), api)
    response = {}

    if p == 1:
        response = get_followers_1(int(user_data['pk']), count)
    elif p == 2:
        response = get_followers_2(int(user_data['pk']), count)
    else:
        return

    print_g(f'{len(response)} followers retrieved')
    
    while True:
        c = input(f'(1) Retrive each users\' info into {user_data["username"]}.followers.csv\n(2) Retrtieve user handles into {user_data["username"]}.followers.txt\n(3) Close\n: ')
        c = int(c)
        if c == 1:
            data = get_users_info(response)
            s = ''
            
            for k in data[0].keys():
                s += k + ', '
            s += '\n'

            for d in data:
                for v in d.values():
                    s += str(v) + ', '
                s += '\n'

            fw = open(f'output/{user_data["username"]}.followers.csv', 'w', encoding='utf-8')
            fw.write(s)
            fw.close()

            break
        elif c == 2:
            fw = open(f'output/{user_data["username"]}.followers.txt', 'w')
            for u in response:
                fw.write(f'@{u["username"]}\n')
            fw.close()

            break
        elif c == 3:
            break
