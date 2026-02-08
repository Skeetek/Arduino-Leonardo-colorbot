from keyauth import api

import sys
import os
import hashlib
import time
import random
import keyboard
import pyautogui
from termcolor import colored
from colorant import Colorant
from datetime import datetime

APP_NAME = "ColorVant"
APP_VERSION  = "1.0.9"

#Settings
TOGGLE_KEY = 'F1'  # Toggle on/off colorant key
XFOV = 50  # X-Axis FOV
YFOV = 50  # Y-Axis FOV
INGAME_SENSITIVITY = 0.4 # Replace this with the your in-game sensitivity value
FLICKSPEED = 1.07437623 * (INGAME_SENSITIVITY ** -0.9936827126)  # Calculate flick speed
MOVESPEED = 1 / (5 * INGAME_SENSITIVITY) # Calculate move speed
SERIAL_PORT_SEARCH = "Auto"
FORCE_COM_PORT = ""
TOGGLE_KEY_MOUSE = '0x02'

def readconfig():
    global TOGGLE_KEY 
    global XFOV 
    global YFOV 
    global FLICKSPEED
    global MOVESPEED
    global SERIAL_PORT_SEARCH
    global FORCE_COM_PORT
    global TOGGLE_KEY_MOUSE
    try:
        file1 = open("config.txt", "r")
    except:
        print('Config file not found. Continue with default settings. ')
        return
    filelines = file1.readlines()
    for line in filelines:
        if line[0]=="#" or line == "\n"or line == "":
            continue
        splitedline = line.split("=") 
        splitedline[0] = splitedline[0].strip().replace("\n","")
        splitedline[1] = splitedline[1].strip().replace("\n","")
        if splitedline[0] == 'TOGGLE_KEY':
            TOGGLE_KEY = splitedline[1]
        elif splitedline[0] == 'XFOV':
            XFOV = int(splitedline[1])
        elif splitedline[0] == 'YFOV':
            YFOV = int(splitedline[1])
        elif splitedline[0] == 'INGAME_SENSITIVITY':
            INGAME_SENSITIVITY = float(splitedline[1])
            FLICKSPEED = 1.07437623 * (INGAME_SENSITIVITY ** -0.9936827126)
            MOVESPEED = 1 / (5 * INGAME_SENSITIVITY)
        elif splitedline[0] == 'SERIAL_PORT_SEARCH':
            SERIAL_PORT_SEARCH = splitedline[1]
        elif splitedline[0] == 'FORCE_COM_PORT':
            FORCE_COM_PORT = splitedline[1]
        elif splitedline[0] == 'TOGGLE_KEY_MOUSE':
            TOGGLE_KEY_MOUSE = int(splitedline[1], 0)


monitor = pyautogui.size()
CENTER_X, CENTER_Y = monitor.width // 2, monitor.height // 2
colors = ['red', 'yellow', 'green', 'blue', 'magenta', 'cyan']
selected_color = random.choice(colors)

def set_title(str):
    os.system('title ' + str)

def clear_console():
    os.system('cls')
    #rn its for windows only but the game isnt supported for linux so who cares

def print_logo():
    print(colored('''
 _____         _               _   _                _   
/  __ \       | |             | | | |              | |  
| /  \/  ___  | |  ___   _ __ | | | |  __ _  _ __  | |_ 
| |     / _ \ | | / _ \ | '__|| | | | / _` || '_ \ | __|
| \__/\| (_) || || (_) || |   \ \_/ /| (_| || | | || |_ 
 \____/ \___/ |_| \___/ |_|    \___/  \__,_||_| |_| \__|
 v''' + APP_VERSION + "\n", selected_color))

def main():
    readconfig()
    set_title(APP_NAME + " " + APP_VERSION)

    print_logo()

    # license authentication
    def getchecksum():
        md5_hash = hashlib.md5()
        file = open(''.join(sys.argv), "rb")
        md5_hash.update(file.read())
        digest = md5_hash.hexdigest()
        return digest

    if False:
        print(colored('[Status]', 'green'), "Loading license authenticator. (Internet connection required.)")
        keyauthapp = None
        try:
            keyauthapp = api(
                name = "ColorVant",
                ownerid = "PTCLv3Qp0x",
                secret = "f5b846a054f471471de5da09e5c360f747ca254d3173a08ef7bcf2a980563055",
                version = "1.0",
                hash_to_check = getchecksum()
            )

        except Exception as e:
            print(colored('[Error]', 'red'), "Looks like license verification service is down or no internet connection. Try again later.")
            os._exit(1)

        try:
            key = input('Enter your license key: ')
            keyauthapp.license(key)
        except KeyboardInterrupt:
            os._exit(1)
        
        if not keyauthapp.check():
            print(colored('[License]', 'red'), "License check returned denial. (expired or banned)")
            os._exit(1)
        # license completed, if license is expired or incorrect keyauthapp.license had to exit the program by now

        clear_console()
        print_logo()
        print(colored('[Info]', 'green'), "License expires at: " + datetime.utcfromtimestamp(int(keyauthapp.user_data.expires)).strftime('%Y-%m-%d %H:%M:%S'))
    else:
        clear_console()
        print_logo()


    # initiate the program
    colorant = Colorant(CENTER_X - XFOV // 2, CENTER_Y - YFOV // 2, XFOV, YFOV, FLICKSPEED, MOVESPEED)
    print(colored('[Status]', 'green'), APP_NAME + " has initialized and is running!")
    
    print(colored("Authentication success! Enjoy!", 'green'))
    print()
    print(colored('[!Important!]', 'red'), colored('Set enemies to', 'white'), colored('Purple', 'magenta'))
    print(colored('[Info]', 'green'), colored(f'Press {colored(TOGGLE_KEY, "red")} to toggle ON/OFF Color Aimbot', 'white'))
    print(colored('[Info]', 'green'), colored(f'Press', 'white'), colored('F2', 'red'), colored('to toggle ON/OFF Detection Window', 'white'))
    print(colored('[Info]', 'green'), colored('RightMB', 'red'), colored('= Aimbot', 'white'))
    print(colored('[Info]', 'green'), colored('LeftAlt', 'red'), colored('= Triggerbot', 'white'))
    print(colored('[Info]', 'green'), colored('LeftCtrl', 'red'), colored('= Silentaim', 'white'))
    print(colored('[Info]', 'green'), colored('Made By', 'white'), colored('Discord:', 'red'), colored('senpaicik & rhb4652', 'white'))
    status = 'Disabled'
    
    try:
        while True:
            if keyboard.is_pressed(TOGGLE_KEY):
                colorant.toggle()
                status = 'Enabled ' if colorant.toggled else 'Disabled'
            print(f'\r{colored("[Status]", "green")} {colored(status, "white")}', end='')
            time.sleep(0.01)
    except (KeyboardInterrupt, SystemExit):
        print(colored('\n[Info]', 'green'), colored('Exiting...', 'white') + '\n')
    finally:
        colorant.close()  # NOW WORKS ✓

if __name__ == '__main__':
    main()
