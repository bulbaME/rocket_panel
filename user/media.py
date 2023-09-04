from .misc.media import get_media, get_likes, get_comments
from .misc.user import get_users_info
from datetime import datetime

def action_media(api, user_data):
    print(f'@{user_data["username"]} has {user_data["media_count"]} media')

    count = 50

    try:
        t = input('Media count (50): ')
        count = int(t)
    except BaseException:
        pass

    count = min(count, int(user_data['media_count']))

    data = get_media(int(user_data['pk']), count)
    print(f'{len(data)} posts retrieved')
    count = len(data)

    while True:
        print(f'\n@{user_data["username"]} - {count} media')
        c = input('media> ').strip()

        if c == 'help':
            print(f'''Commands:
    show - list all retrieved posts
    select - select a post by its index
    exit - close media interface''')
        elif c == 'exit':
            return
        elif c == 'show':
            for i in range(count):
                print(f'({i+1}) {"no caption text" if data[i]["caption"] == None else data[i]["caption"]["text"]} [{datetime.fromtimestamp(int(data[i]["taken_at"]))}]')
        elif c =='select':
            action_post(api, user_data, data)
        else:
            print('Incorrect command, try "help"')

def action_post(api, user_data, media):
    post = {}
    post_i = 0

    try:
        post_i = input('Select post: ')
        post_i = int(post_i)
        post = media[post_i - 1]
    except BaseException:
        print('Invalid selection number')
        return
    
    print('Selected post')
    print(f'{"no caption text" if post["caption"] == None else post["caption"]["text"]} [{datetime.fromtimestamp(int(post["taken_at"]))}]')
    print(f'{post["comment_count"]} comments, {post["like_count"]} likes')

    while True:
        print(f'\n@{user_data["username"]} - post {post_i}')
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

def action_likes(api, post):
    like_data = get_likes(post['code'], int(post['like_count']))
    print(f'{len(like_data)} likes retrieved')

    while True:
        c = input(f'(1) Retrive each users\' info into {post["code"]}.post.likes.csv\n(2) Retrtieve user handles into {post["code"]}.post.likes.txt\n(3) Close\n: ')
        c = int(c)
        if c == 1:
            data = get_users_info(like_data, id_f='id')
            s = ''
            
            for k in data[0].keys():
                s += k + ', '
            s += '\n'

            for d in data:
                for v in d.values():
                    s += str(v) + ', '
                s += '\n'

            fw = open(f'output/{post["code"]}.post.likes.csv', 'w', encoding='utf-8')
            fw.write(s)
            fw.close()

            break
        elif c == 2:
            fw = open(f'output/{post["code"]}.post.likes.txt', 'w')
            for u in like_data:
                fw.write(f'@{u["username"]}\n')
            fw.close()

            break
        elif c == 3:
            break

def action_comments(api, post):
    comment_data = get_comments(post['pk'], int(post['comment_count']))
    print(f'{len(comment_data)} comments retrieved')

    while True:
        c = input(f'(1) Retrive each users\' info into {post["code"]}.post.comments.csv\n(2) Retrtieve user handles into {post["code"]}.post.comments.txt\n(3) Show comments\n(4) Close\n: ')
        c = int(c)
        if c == 1:
            data = get_users_info(comment_data, id_f='user_id')
            s = ''
            
            for k in data[0].keys():
                s += k + ', '
            s += '\n'

            for d in data:
                for v in d.values():
                    s += str(v) + ', '
                s += '\n'

            fw = open(f'output/{post["code"]}.post.comments.csv', 'w', encoding='utf-8')
            fw.write(s)
            fw.close()

            break
        elif c == 2:
            fw = open(f'output/{post["code"]}.post.comments.txt', 'w')
            for u in comment_data:
                fw.write(f'@{u["user"]["username"]}\n')
            fw.close()

            break
        elif c == 3:
            print('Comments:')
            for i in range(len(comment_data)):
                v = comment_data[i]
                print(f'({i+1}) @{v["user"]["username"]}: {v["text"]}')
            print()
        elif c == 4:
            break
        
