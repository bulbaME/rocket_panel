from rocketapi import InstagramAPI
from misc import check_response
from . import remove_duplicates
from misc import get_token
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
                return ([], max_id, e)
        
    return (data, data[-1]['id'], None)

def get_media(id, count):
    data = []
    req_count = (count - 1) // 33 + 1
    token = get_token()
    err = {}

    with Bar('Retrieving media', max=req_count, suffix='%(percent)d%%') as bar:
        max_id = ''

        with Pool(processes=8) as pool:
            for i in range(req_count):
                (d, _max_id, e) = pool.apply(get_media_noexcept_w, (id, token, max_id))
                bar.next()
                data.extend(d)
                if (e != None):
                    err['e'] = e
                    err['max_id'] = max_id
                    err['left'] = req_count - i
                    bar.finish()
                    break
                max_id = _max_id

            pool.close()
            pool.join()

        while len(err.keys()) > 0:
            print(f'\nMedia request failed:')
            print(err['e'])
            
            c = input('\nRepeat? (y/n): ').strip().lower()
            if c != 'y':
                break
            
            _err = {}
            with Bar('Retrieving media', max=err['left'], suffix='%(percent)d%%') as bar:
                max_id = err['max_id']

                with Pool(processes=8) as pool:
                    for i in range(err['left']):
                        (d, _max_id, e) = pool.apply(get_media_noexcept_w, (id, token, max_id))
                        bar.next()
                        data.extend(d)
                        if (e != None):
                            _err['e'] = e
                            _err['max_id'] = max_id
                            _err['left'] = req_count - i
                            bar.finish()
                            break
                        max_id = _max_id
            
            err = _err
    
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
                return ([], max_id, e)
        
    return (data['edges'], data['page_info']['end_cursor'], None)

def get_likes(code, count):
    data = []
    req_count = (count - 1) // 50 + 1
    token = get_token()
    err = {}

    with Bar('Retrieving likes', max=req_count, suffix='%(percent)d%%') as bar:
        max_id = ''

        with Pool(processes=8) as pool:
            for i in range(req_count):
                (d, _max_id, e) = pool.apply(get_likes_noexcept_w, (code, token, max_id))
                bar.next()
                data.extend(d)
                if (e != None):
                    err['e'] = e
                    err['max_id'] = max_id
                    err['left'] = req_count - i
                    bar.finish()
                    break
                max_id = _max_id

            pool.close()
            pool.join()

        while len(err.keys()) > 0:
            print(f'\nLikes request failed:')
            print(err['e'])
            
            c = input('\nRepeat? (y/n): ').strip().lower()
            if c != 'y':
                break
            
            _err = {}
            with Bar('Retrieving likes', max=err['left'], suffix='%(percent)d%%') as bar:
                max_id = err['max_id']

                with Pool(processes=8) as pool:
                    for i in range(err['left']):
                        (d, _max_id, e) = pool.apply(get_likes_noexcept_w, (id, token, max_id))
                        bar.next()
                        data.extend(d)
                        if (e != None):
                            _err['e'] = e
                            _err['max_id'] = max_id
                            _err['left'] = req_count - i
                            bar.finish()
                            break
                        max_id = _max_id
            
            err = _err
    
    data = [v['node'] for v in data]
    return remove_duplicates(data, dp_f='id')

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
            i -= 1
            if i == 0:
                return ([], max_id, e)
        
    return (data['comments'], data['next_min_id'], None)

def get_comments(id, count):
    data = []
    err = {}
    token = get_token()
    req_count = (count - 1) // 15 + 1

    with Bar('Retrieving comments', max=req_count, suffix='%(percent)d%%') as bar:
        max_id = None

        with Pool(processes=8) as pool:
            for i in range(req_count):
                (d, _max_id, e) = pool.apply(get_comments_noexcept_w, (id, token, max_id))
                bar.next()
                data.extend(d)
                if (e != None):
                    err['e'] = e
                    err['max_id'] = max_id
                    err['left'] = req_count - i
                    bar.finish()
                    break
                max_id = _max_id

            pool.close()
            pool.join()

        while len(err.keys()) > 0:
            print(f'\nComments request failed:')
            print(err['e'])
            
            c = input('\nRepeat? (y/n): ').strip().lower()
            if c != 'y':
                break
            
            _err = {}
            with Bar('Retrieving comments', max=err['left'], suffix='%(percent)d%%') as bar:
                max_id = err['max_id']

                with Pool(processes=8) as pool:
                    for i in range(err['left']):
                        (d, _max_id, e) = pool.apply(get_comments_noexcept_w, (id, token, max_id))
                        bar.next()
                        data.extend(d)
                        if (e != None):
                            _err['e'] = e
                            _err['max_id'] = max_id
                            _err['left'] = req_count - i
                            bar.finish()
                            break
                        max_id = _max_id
            
            err = _err

    return remove_duplicates(data)
