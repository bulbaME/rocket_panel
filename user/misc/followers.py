from rocketapi import InstagramAPI
from misc import check_response
from . import remove_duplicates
from misc import get_token
from progress.bar import Bar
from multiprocessing import Pool

def get_followers_pagintation_type(id, api):
    data = {}
    
    while True:
        try:
            print('\nRetrieving pagination type...')
            data = api.get_user_followers(id)
            check_response(data)
            break
        except BaseException as e:
            print(e)
            if input('Repeat? (y/n): ').lower().strip() != 'y':
                return -1
            
    try:
        int(data['next_max_id'])
        print("Pagination type decimal\n")
        return 1
    except BaseException:
        print("Pagination type base64\n")
        return 2

def get_followers_noexcept_w_1(id, token, max_id):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_user_followers(id, count=100, max_id=max_id)
            check_response(r)
            data = r['users']
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return ([], e)
        
    return (data, None)

def get_followers_1(id, count):
    data = []
    req_count = (count - 1) // 100 + 1
    token = get_token()
    err = []

    with Bar('Retrieving users', max=req_count, suffix='%(percent)d%%') as bar:

        with Pool(processes=8) as pool:
            for i in range(req_count):
                pool.apply_async(get_followers_noexcept_w_1, (int(id), token, str(i * 100)), callback=lambda v: (data.extend(v[0]), bar.next(), err.append((v[1], str(i * 100)))))
            pool.close()
            pool.join()
    
    err = list(filter(lambda v: v[0] != None, err))

    while len(err) > 0:
        print(f'\n{len(err)} / {req_count} requests failed:')
        for (e, _) in err:
            print(e)
        
        c = input('\nDo you want to repeat? (y/n): ').strip().lower()
        if c != 'y':
            break
        
        _err = []
        with Bar('Retrieving users', max=len(err), suffix='%(percent)d%%') as bar:
            with Pool(processes=8) as pool:
                for i in range(len(err)):
                    pool.apply_async(get_followers_noexcept_w_1, (int(id), token, str(i * 100)), callback=lambda v: (data.extend(v[0]), bar.next(), _err.append((v[1], str(i * 100)))))
        
        err = list(filter(lambda v: v[0] != None, _err))
    
    return remove_duplicates(data)

def get_followers_noexcept_w_2(id, token, max_id):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_user_followers(id, max_id=max_id)
            check_response(r)
            data = r
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return ([], max_id, e)
        
    return (data["users"], data["next_max_id"], None)

def get_followers_2(id, count):
    data = []
    token = get_token()
    err = {}

    with Bar('Retrieving users', max=count, suffix='%(percent)d%%') as bar:
        max_id = None

        with Pool(processes=8) as pool:
            while count > len(data):
                (d, _max_id, e) = pool.apply(get_followers_noexcept_w_2, (id, token, max_id))
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
            print(f'\Followers request failed:')
            print(err['e'])
            
            c = input('\nRepeat? (y/n): ').strip().lower()
            if c != 'y':
                break
            
            _err = {}
            with Bar('Retrieving followers', max=err['left'], suffix='%(percent)d%%') as bar:
                max_id = err['max_id']

                with Pool(processes=8) as pool:
                    while count > len(data):
                        (d, _max_id, e) = pool.apply(get_followers_noexcept_w_2, (id, token, max_id))
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