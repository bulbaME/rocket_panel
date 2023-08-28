from rocketapi import InstagramAPI
from .response import check_response
from . import get_token, remove_duplicates
from progress.bar import Bar
from multiprocessing import Pool

def get_followers_noexcept_w(id, token, max_id):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_user_followers(id, count=100, max_id=str(max_id))
            check_response(r)
            data = r['users']
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return []
        
    return data

def get_followers(id, count):
    data = []

    token = get_token()
    with Bar('Retrieving users', max=(count - 1) // 100 + 1) as bar:

        with Pool(processes=8) as pool:
            for i in range((count - 1) // 100 + 1):
                pool.apply_async(get_followers_noexcept_w, (int(id), token, i * 100), callback=lambda d: (data.extend(d), bar.next()))
            pool.close()
            pool.join()
    
    return remove_duplicates(data)
