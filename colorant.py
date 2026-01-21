import cv2
import numpy as np
import threading
import time
import win32api
import pyautogui

from capture import Capture
from mouse import ArduinoMouse
from fov_window import show_detection_window, toggle_window

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

class Colorant:
    LOWER_COLOR = np.array([140, 120, 180])
    UPPER_COLOR = np.array([160, 200, 255])

    def __init__(self, x, y, xfov, yfov, FLICKSPEED, MOVESPEED):
        readconfig()
        self.arduinomouse = ArduinoMouse()
        self.grabber = Capture(x, y, xfov, yfov)
        self.flickspeed = FLICKSPEED
        self.movespeed = MOVESPEED
        threading.Thread(target=self.listen, daemon=True).start()
        self.toggled = False
        self.window_toggled = False
        
    def toggle(self):
        self.toggled = not self.toggled
        time.sleep(0.2)

    def listen(self):
        while True:
            if win32api.GetAsyncKeyState(0x71) < 0:
                toggle_window(self)
                time.sleep(0.2)
            if win32api.GetAsyncKeyState(TOGGLE_KEY_MOUSE) < 0 and self.toggled:
                self.process("move")
            elif win32api.GetAsyncKeyState(0x12) < 0 and self.toggled:
                self.process("click")
            elif win32api.GetAsyncKeyState(0x11) < 0 and self.toggled:
                self.process("flick")

    def process(self, action):
        screen = self.grabber.get_screen()
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.LOWER_COLOR, self.UPPER_COLOR)
        dilated = cv2.dilate(mask, None, iterations=5)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return

        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        center = (x + w // 2, y + h // 2)
        y_offset = int(h * 0.3)

        if action == "move":
            cX = center[0]
            cY = y + y_offset
            x_diff = cX - self.grabber.xfov // 2
            y_diff = cY - self.grabber.yfov // 2
            self.arduinomouse.move(x_diff * self.movespeed, y_diff * self.movespeed)

        elif action == "click" and abs(center[0] - self.grabber.xfov // 2) <= 4 and abs(center[1] - self.grabber.yfov // 2) <= 10:
            self.arduinomouse.click()

        elif action == "flick":
            cX = center[0] + 2
            cY = y + y_offset
            x_diff = cX - self.grabber.xfov // 2
            y_diff = cY - self.grabber.yfov // 2
            flickx = x_diff * self.flickspeed
            flicky = y_diff * self.flickspeed
            self.arduinomouse.flick(flickx, flicky)
            self.arduinomouse.click()
            self.arduinomouse.flick(-(flickx), -(flicky))
