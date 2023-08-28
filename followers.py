from misc.followers import get_followers
from misc.user import get_users_info

def action_followers(api, user_data):
    count = 100

    try:
        t = input('Followers count (100): ')
        count = int(t)
    except BaseException:
        pass

    count = min(count, int(user_data['follower_count']))

    response = get_followers(int(user_data['pk']), count)
    print(f'{len(response)} followers retrieved')
    
    while True:
        c = input(f'(1) Retrive each users\' info into {user_data["username"]}.followers.csv\n(2) Retrtieve user handles into {user_data["username"]}.followers.txt\n: ')
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

