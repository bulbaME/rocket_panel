from user import user_actions
from hashtag import hashtag_actions
from location import location_actions
from compare import compare_actions
from .misc import get_token, mkdir_output, print_t, RB, GB, RS
from rocketapi import InstagramAPI

def main():
    mkdir_output()
    api = InstagramAPI(token=get_token())
    
    help_s = f'''    <=== {RB}Rocket Panel{RS} ===>\n
    [extraction]
        user ({RB}@{RS}) - get user info
        hashtag ({RB}#{RS}) - get hastag info
        location ({RB}!{RS}) - get location info
          
    [tools]
        compare ({GB}/{RS}) - compare two data files
        
    exit - close gui\n'''
    print(help_s)

    while True:
        c = input('> ').strip().lower()

        if c == 'user' or c == '@':
            user_actions(api)
        elif c == 'hashtag' or c == '#':
            hashtag_actions(api)
        elif c == 'location' or c == '!':
            location_actions(api)
        elif c == 'compare' or c == '/':
            compare_actions()
        elif c == 'help':
            print(help_s)
        elif c == 'exit':
            return
        else:
            print('Invalid command, try "help"')
        print('')

if __name__ == "__main__":
    main()