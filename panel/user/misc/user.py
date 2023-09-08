from rocketapi import InstagramAPI
from misc import check_response
from misc import get_token
from progress.bar import Bar
from multiprocessing import Pool

def get_user_info_noexcept_w(id, token):
    data = {}
    api = InstagramAPI(token=token)

    i = 5

    while True:
        try:
            data = get_user_info_by_id(api, id)
            break
        except BaseException as e:
            i -= 1
            if i == 0:
                return {}
        
    return parse_user_data(data)

def get_users_info(users, id_f='pk'):
    data = []

    token = get_token()
    with Bar('Retrieving users info', max=len(users)) as bar:

        with Pool(processes=8) as pool:
            for u in users:
                pool.apply_async(get_user_info_noexcept_w, (int(u[id_f]), token), callback=lambda d: (data.append(d), bar.next()))
            pool.close()
            pool.join()
    
    return data

def get_str_val(data, k):
    try:
        return data[k]
    except BaseException:
        return ''

def parse_user_data(data):
    return {
        'username': get_str_val(data, 'username'),
        'id': get_str_val(data, 'pk'),
        'full_name': get_str_val(data, 'full_name'),
        'followers': get_str_val(data, 'follower_count'),
        'followings': get_str_val(data, 'following_count'),
        'adress': get_str_val(data, 'address_street'),
        'city': get_str_val(data, 'city_name'),
        'phone_contact': get_str_val(data, 'contact_phone_number'),
        'email': get_str_val(data, 'public_email'),
        'phone_public': get_str_val(data, 'public_phone_number'),
        'zip': get_str_val(data, 'zip')
    }

def get_user_info(api, user_name):
    r = api.get_user_info(user_name)
    response = check_response(r)
    return response['data']['user']

def get_user_info_by_id(api, id):
    r = api.get_user_info_by_id(id)
    response = check_response(r)
    return response['user']
