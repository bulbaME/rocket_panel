import os
import colorama
import yaml
colorama.init()

RB = colorama.Fore.RED + colorama.Style.BRIGHT
GB = colorama.Fore.GREEN + colorama.Style.BRIGHT
RS = colorama.Style.RESET_ALL

def get_token():
    t = yaml.safe_load(open('credentials.yaml'))['rocket_api']['token']
    return t

def mkdir_output():
    if not os.path.exists('output'):
        os.mkdir('output')

def check_response(res):
    if res['status'] != 'ok':
        raise Exception('An error occured: ' + res['message'])
    
    return res


def print_t(s):
    print(colorama.Fore.RED + colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL)

def print_g(s):
    print(colorama.Fore.GREEN + colorama.Style.DIM + s + colorama.Style.RESET_ALL)

def print_e(s):
    print(colorama.Fore.RED + colorama.Style.DIM + s + colorama.Style.RESET_ALL)

