from user.media import action_likes, action_comments
from rocketapi import InstagramAPI
from misc import get_token, check_response
from datetime import datetime
from progress.bar import Bar
from multiprocessing import Pool
from user.misc.user import get_users_info
from user.misc import remove_duplicates
from misc import print_g, print_e

def get_media_noexcept_w(name, token, t):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_hashtag_media(name, max_id=t[0], page=t[1])
            check_response(r)
            data = r
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return ([], t, e)
    
    max_id = data['next_max_id']
    page = data['next_page']

    posts = []
    for v in data['sections']:
        for m in v['layout_content']['medias']:
            posts.append(m['media'])

    return (posts, (max_id, page), None)

def get_media(name, count):
    data = []
    token = get_token()
    err = {}

    with Bar('Retrieving media', max=count, suffix='%(percent)d%%') as bar:
        t = (None, None)

        with Pool(processes=8) as pool:
            while True:
                (d, _t, e) = pool.apply(get_media_noexcept_w, (name, token, t))
                bar.next(n=len(d))
                data.extend(d)
                if len(data) >= count:
                    break
                if (e != None):
                    err['e'] = e
                    err['t'] = t
                    err['left'] = count - len(data)
                    bar.finish()
                    break
                t = _t

            pool.close()
            pool.join()

        while len(err.keys()) > 0:
            print_e(f'\nMedia request failed:')
            print_e(err['e'])
            
            c = input('\nRepeat? (y/n): ').strip().lower()
            if c != 'y':
                break
            
            _err = {}
            with Bar('Retrieving media', max=err['left'], suffix='%(percent)d%%') as bar:
                t = err['t']
                c = 0

                with Pool(processes=8) as pool:
                    while True:
                        (d, _t, e) = pool.apply(get_media_noexcept_w, (name, token, t))
                        bar.next(n=len(d))
                        c += len(d)
                        data.extend(d)
                        if (e != None):
                            _err['e'] = e
                            _err['t'] = t
                            _err['left'] = err['left'] - c
                            bar.finish()
                            break
                        t = _t
            
            err = _err
    
    return data

def action_media(api, hashtag_data):
    print_g(f'#{hashtag_data["name"]} has {hashtag_data["media_count"]} media')

    count = 50

    try:
        t = input('Media count (50): ')
        count = int(t)
    except BaseException:
        pass

    count = min(count, int(hashtag_data['media_count']))

    data = get_media(hashtag_data['name'], count)
    print_g(f'{len(data)} posts retrieved')
    count = len(data)

    while True:
        print(f'\n#{hashtag_data["name"]} - {count} media')
        c = input('media> ').strip()

        if c == 'help':
            print(f'''Commands:
    show - list all retrieved posts
    users - get users who posted
    select - select a post by its index
    exit - close media interface''')
        elif c == 'exit':
            return
        elif c == 'users':
            users = [p['user'] for p in data]
            users = remove_duplicates(users)
            print_g(f'Retrieved {len(users)} unique users')
            
            while True:
                c = input(f'(1) Retrive each users\' info into {hashtag_data["name"]}#.users.csv\n(2) Retrtieve user handles into {hashtag_data["name"]}#.users.txt\n(3) Close\n: ')
                c = int(c)
                if c == 1:
                    data = get_users_info(users)
                    s = ''
                    
                    for k in data[0].keys():
                        s += k + ', '
                    s += '\n'

                    for d in data:
                        for v in d.values():
                            s += str(v) + ', '
                        s += '\n'

                    fw = open(f'output/{hashtag_data["name"]}#.users.csv', 'w', encoding='utf-8')
                    fw.write(s)
                    fw.close()

                    break
                elif c == 2:
                    fw = open(f'output/{hashtag_data["name"]}#.users.txt', 'w')
                    for u in users:
                        fw.write(f'@{u["username"]}\n')
                    fw.close()

                    break
                elif c == 3:
                    break

        elif c == 'show':
            for i in range(count):
                print(f'({i+1}) {"no caption text" if data[i]["caption"] == None else data[i]["caption"]["text"]} [{datetime.fromtimestamp(int(data[i]["taken_at"]))}]')
        elif c =='select':
            action_post(api, hashtag_data, data)
        else:
            print('Incorrect command, try "help"')

def action_post(api, hashtag_data, media):
    post = {}
    post_i = 0

    try:
        post_i = input('Select post: ')
        post_i = int(post_i)
        post = media[post_i - 1]
    except BaseException:
        print_e('Invalid selection number')
        return
    
    print('Selected post')
    print(f'{"no caption text" if post["caption"] == None else post["caption"]["text"]} [{datetime.fromtimestamp(int(post["taken_at"]))}]')
    print(f'{post["comment_count"]} comments, {post["like_count"]} likes')

    while True:
        print(f'\n#{hashtag_data["name"]} - post {post_i}')
        c = input('post> ').strip()

        if c == 'help':
            print(f'''Commands:
    likes - get all users who liked
    comments - get all users who commented
    exit - close media interface''')
        elif c == 'exit':
            return
        elif c == 'likes':
            action_likes(api, post)
        elif c == 'comments':
            action_comments(api, post)
        else:
            print('Incorrect command, try "help"')