from rocketapi import InstagramAPI
from panel.misc import check_response
from . import remove_duplicates
from panel.misc import get_token, print_g, print_e
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
    token = get_token()
    err = {}

    with Bar('Retrieving media', max=count, suffix='%(percent)d%%') as bar:
        max_id = ''

        with Pool(processes=8) as pool:
            while count > len(data):
                (d, _max_id, e) = pool.apply(get_media_noexcept_w, (id, token, max_id))
                bar.next(len(d))
                data.extend(d)
                if (e != None):
                    err['e'] = e
                    err['max_id'] = max_id
                    err['left'] = count - len(data)
                    bar.finish()
                    break
                max_id = _max_id

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
                max_id = err['max_id']

                with Pool(processes=8) as pool:
                    while count > len(data):
                        (d, _max_id, e) = pool.apply(get_media_noexcept_w, (id, token, max_id))
                        bar.next(len(d))
                        data.extend(d)
                        if (e != None):
                            _err['e'] = e
                            _err['max_id'] = max_id
                            _err['left'] = count - len(data)
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
            r = api.get_media_likes(code)
            check_response(r)
            data = r
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return ([], max_id, e)
        
    users = data["users"]

    return users

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
            print_e(f'\nLikes request failed:')
            print_e(err['e'])
            
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
    
    try:
        max_id = data['next_max_id']
    except BaseException:
        pass

    return (data['comments'], max_id, None)

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
            print_e(f'\nComments request failed:')
            print_e(err['e'])
            
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
