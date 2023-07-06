import json
import os

def screen_clear():
   # for mac and linux(here, os.name is 'posix')
   if os.name == 'posix':
      _ = os.system('clear')
   else:
      # for windows platfrom
      _ = os.system('cls')

def main(): 
    conv = open('conversations-all.json')

    response = 'y'
    line_num = 0

    while response == 'y' or response == 'Y':
        screen_clear()
        line = conv.readline()
        data = json.loads(line)
        for e in data['events']:
            print(e['event'])
            print('|')
            if e['event'] == 'action':
                print('----'+e['name'])
            if e['event'] == 'user':
                print('----'+e['text'])
            if e['event'] == 'bot':
                print(e['text'])
            print('|')
        print(f"DIALOGUE: {line_num}")
        response = input('Continue?[y/n]')
        if response == '':
            response = 'y'
        line_num += 1
            
if __name__ == "__main__":
    main()