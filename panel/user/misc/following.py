from rocketapi import InstagramAPI
from panel.misc import check_response
from . import remove_duplicates
from panel.misc import get_token, print_g, print_e
from progress.bar import Bar
from multiprocessing import Pool

def get_followings_noexcept_w(id, token, max_id):
    data = []
    api = InstagramAPI(token=token)

    i = 8

    while True:
        try:
            r = api.get_user_following(id, count=100, max_id=max_id)
            check_response(r)
            data = r['users']
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return (max_id, e) 
            
    return (data, None)

def get_following(id, count):
    data = []
    req_count = (count - 1) // 100 + 1
    token = get_token()
    err = []

    with Bar('Retrieving users', max=req_count, suffix='%(percent)d%%') as bar:

        with Pool(processes=8) as pool:
            for i in range(req_count):
                pool.apply_async(get_followings_noexcept_w, (int(id), token, str(i * 100)), callback=lambda v: (data.extend(v[0]), bar.next(), err.append((v[1], str(i * 100)))))
            pool.close()
            pool.join()
    
    err = list(filter(lambda v: v[0] != None, err))

    while len(err) > 0:
        print_e(f'\n{len(err)} / {req_count} requests failed:')
        for (e, _) in err:
            print_e(e)
        
        c = input('\nDo you want to repeat? (y/n): ').strip().lower()
        if c != 'y':
            break
        
        _err = []
        with Bar('Retrieving users', max=len(err), suffix='%(percent)d%%') as bar:
            with Pool(processes=8) as pool:
                for i in range(len(err)):
                    pool.apply_async(get_followings_noexcept_w, (int(id), token, str(i * 100)), callback=lambda v: (data.extend(v[0]), bar.next(), _err.append((v[1], str(i * 100)))))
        
        err = list(filter(lambda v: v[0] != None, _err))
    
    return remove_duplicates(data)
