from user import user_actions
from hashtag import hashtag_actions
from misc import get_token, mkdir_output
from rocketapi import InstagramAPI

def main():
    mkdir_output()
    api = InstagramAPI(token=get_token())
    
    print('[Rocket Panel]')
    print('''
        user (@) - get user info
        hastag (#) - get hastag info
        exit - close gui
        ''')


    while True:
        c = input('> ').strip().lower()

        if c == 'user' or c == '@':
            user_actions(api)
        elif c == 'hashtag' or c == '#':
            hashtag_actions(api)
        elif c == 'location':
            pass
        elif c == 'help':
            print('''Commands:
    user (@) - get user info
    hashtag (#) - get hastag info
    exit - close gui''')
        elif c == 'exit':
            return
        else:
            print('Invalid command, try "help"')
        print('')

if __name__ == "__main__":
    main()