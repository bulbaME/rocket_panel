from .misc.following import get_following
from .misc.user import get_users_info
from panel.misc import print_g, print_e

def action_following(api, user_data):
    count = 100

    print(f'\n@{user_data["username"]} has {user_data["following_count"]} followings')

    try:
        t = input('Following count (100): ')
        count = int(t)
    except BaseException:
        pass

    count = min(count, int(user_data['following_count']))

    response = get_following(int(user_data['pk']), count)
    print_g(f'{len(response)} followings retrieved')
    
    while True:
        c = input(f'(1) Retrive each users\' info into {user_data["username"]}.following.csv\n(2) Retrtieve user handles into {user_data["username"]}.following.txt\n(3) Close\n: ')
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

            fw = open(f'output/{user_data["username"]}.following.csv', 'w', encoding='utf-8')
            fw.write(s)
            fw.close()

            break
        elif c == 2:
            fw = open(f'output/{user_data["username"]}.following.txt', 'w')
            for u in response:
                fw.write(f'@{u["username"]}\n')
            fw.close()

            break
        elif c == 3:
            break

