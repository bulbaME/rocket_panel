import os

def get_token():
    fr = open('TOKEN')
    token = fr.readline().strip()
    fr.close()
    return token

def mkdir_output():
    if not os.path.exists('output'):
        os.mkdir('output')

def check_response(res):
    if res['status'] != 'ok':
        raise Exception('An error occured: ' + res['message'])
    
    return res