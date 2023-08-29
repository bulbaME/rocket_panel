from rocketapi import InstagramAPI
from .response import check_response
from . import get_token, remove_duplicates
from progress.bar import Bar
from multiprocessing import Pool

def get_media_noexcept_w(id, token, max_id):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_user_media(id, count=50, max_id=max_id)
            check_response(r)
            data = r['items']
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return []
        
    return data

def get_media(id, count):
    data = []

    token = get_token()
    with Bar('Retrieving media', max=(count - 1) // 33 + 1) as bar:
        max_id = ''

        with Pool(processes=8) as pool:
            for i in range((count - 1) // 33 + 1):
                data.extend(pool.apply(get_media_noexcept_w, (int(id), token, max_id)))
                bar.next()
                max_id = data[-1]['id'] if len(data) > 0 else max_id

            pool.close()
            pool.join()
    
    return data

def get_likes_noexcept_w(code, token, max_id):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_media_likes(code, count=50, max_id=max_id)
            check_response(r)
            data = r['data']['shortcode_media']['edge_liked_by']
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return ([], max_id)
        
    return (data['edges'], data['page_info']['end_cursor'])

def get_likes(code, count):
    data = []

    token = get_token()
    with Bar('Retrieving likes', max=(count - 1) // 50 + 1) as bar:
        max_id = ''

        with Pool(processes=8) as pool:
            for i in range((count - 1) // 50 + 1):
                (d, max_id) = pool.apply(get_likes_noexcept_w, (code, token, max_id))
                bar.next()
                data.extend(d)

            pool.close()
            pool.join()
    
    data = [v['node'] for v in data]
    return data

def get_comments_noexcept_w(id, token, max_id):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_media_comments(id, min_id=max_id)
            check_response(r)
            data = r
            break
        except BaseException as e:
            print(e)
            i -= 1
            if i == 0:
                return ([], max_id)
        
    return (data['comments'], data['next_min_id'])

def get_comments(id, count):
    data = []

    token = get_token()
    with Bar('Retrieving comments', max=(count - 1) // 15 + 1) as bar:
        max_id = ''

        with Pool(processes=8) as pool:
            for i in range((count - 1) // 15 + 1):
                (d, max_id) = pool.apply(get_comments_noexcept_w, (id, token, max_id))
                bar.next()
                data.extend(d)

            pool.close()
            pool.join()
    
    return remove_duplicates(data)
