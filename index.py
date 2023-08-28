from user import user_actions
from misc import get_token
from rocketapi import InstagramAPI

def main():
    api = InstagramAPI(token=get_token())

    while True:
        user_actions(api)
        print('\n \n')

if __name__ == "__main__":
    main()