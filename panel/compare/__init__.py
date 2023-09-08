import os
from misc import print_g, print_e, GB, RS

def compare_actions():
    while True:
        c = input('\n/> ')

        if c == 'help':
            print(f'''Commands:
    show - retrieve user followings
    select - retrieve user followers
    exit - close handle interface''')
        elif c == 'show':
            show_action(True)
        elif c == 'select':
            select_action()
        elif c == 'exit':
            break
        else:
            print('Incorrect command, try "help"')

def show_action(to_print) -> list:
    files = os.listdir('output')
    files = list(filter(lambda x: x.endswith('.txt'), files))

    d = {
        'likes': [],
        'comments': [],
        'followers': [],
        'following': [],
        'hashtag': [],
        'location': [],
        'other': []
    }

    for f in files:
        if f.find('likes') != -1:
            d['likes'].append(f)
        elif f.find('comments') != -1:
            d['comments'].append(f)
        elif f.find('followers') != -1:
            d['followers'].append(f)
        elif f.find('following') != -1:
            d['following'].append(f)
        elif f.find('#') != -1:
            d['hashtag'].append(f)
        elif f.find('!') != -1:
            d['location'].append(f) 
        else:
            d['other'].append(f)

    c = 1
    l = []
    for (k, v) in d.items():
        if len(v) == 0:
            continue
        
        l.extend(v)
        
        if not to_print:
            continue

        print(f'[{GB}{k.upper()}{RS}]')
        for f in v:
            print(f'({c})    {f}')
            c += 1
        print()

    return l

def select_action():
    l = show_action(True)

    f1 = ''
    f2 = ''

    f1 = input('First file: ')
    f2 = input('Second file: ')

    try:
        f1 = int(f1)
        if f1 < 1 or f1 > len(l):
            raise BaseException
        
    except BaseException:
        print_e(f'Invalid index {f1} for first file')
        return

    try:
        f2 = int(f2)
        if f2 < 1 or f2 > len(l):
            raise BaseException
        
    except BaseException:
        print_e(f'Invalid index {f2} for second file')
        return
    
    f1 -= 1
    f2 -= 1

    fn1 = l[f1]
    fn2 = l[f2]

    s1 = open(f'output/{fn1}').read().split('\n')
    s2 = open(f'output/{fn2}').read().split('\n')

    fn1 = '.'.join(fn1.split('.')[:-1])
    fn2 = '.'.join(fn2.split('.')[:-1])

    print(f'{GB}{fn1}{RS} and {GB}{fn2}{RS}')

    while True:
        op = input('Choose comparation type\nmatch (=) - get matching users\ndiffer (^) - get users that differ\n: ')
        op = op.lower().strip()

        if op == 'differ' or op == '^':
            r = []
            for u in s1:
                if not u in s2:
                    r.append(u)
            
            for u in s2:
                if not u in s1:
                    r.append(u)
                    
            s = '\n'.join(r) + '\n'
            print(f'Result was saved to !differ.{fn1}.{fn2}.txt')
            f = open(f'output/!differ.{fn1}.{fn2}.txt', 'w')
            f.write(s)
            f.close()

            break

        elif op == 'match' or op == '=':
            r = []
            for u in s1:
                if u in s2:
                    r.append(u)
                    
            s = '\n'.join(r) + '\n'
            print(f'Result was saved to !match.{fn1}.{fn2}.txt')
            f = open(f'output/!match.{fn1}.{fn2}.txt', 'w')
            f.write(s)
            f.close()

            break
        else:
            print("Invalid operation, try again\n")