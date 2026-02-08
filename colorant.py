import cv2
import numpy as np
import threading
import time
import win32api
import pyautogui
import traceback 

from capture import Capture
from mouse import ArduinoMouse
from fov_window import show_detection_window, toggle_window

#Settings
TOGGLE_KEY = 'F1'
XFOV = 50
YFOV = 50
INGAME_SENSITIVITY = 0.4
FLICKSPEED = 1.07437623 * (INGAME_SENSITIVITY ** -0.9936827126)
# ULTRA STRONG MODE: Changed divisor from 5 to 2.5 for 2x Speed
MOVESPEED = 1 / (2.5 * INGAME_SENSITIVITY)
SERIAL_PORT_SEARCH = "Auto"
FORCE_COM_PORT = ""
# CRITICAL FIX: Default must be an integer (number), not a string.
TOGGLE_KEY_MOUSE = 0x02 

def readconfig():
    global TOGGLE_KEY, XFOV, YFOV, FLICKSPEED, MOVESPEED, SERIAL_PORT_SEARCH, FORCE_COM_PORT, TOGGLE_KEY_MOUSE
    try:
        with open("config.txt", "r") as f:
            for line in f:
                # Handle comments and empty lines
                if line.strip().startswith("#") or line.strip() == "":
                    continue
                
                # Split key and value
                parts = line.split("=", 1)
                if len(parts) != 2: continue
                
                key = parts[0].strip()
                # Remove inline comments from value
                value = parts[1].split("#")[0].strip()

                if key == 'TOGGLE_KEY':
                    TOGGLE_KEY = value
                elif key == 'XFOV':
                    XFOV = int(value)
                elif key == 'YFOV':
                    YFOV = int(value)
                elif key == 'INGAME_SENSITIVITY':
                    INGAME_SENSITIVITY = float(value)
                    FLICKSPEED = 1.07437623 * (INGAME_SENSITIVITY ** -0.9936827126)
                    # ULTRA STRONG MODE: Updated config calculation too
                    MOVESPEED = 1 / (2.5 * INGAME_SENSITIVITY)
                elif key == 'SERIAL_PORT_SEARCH':
                    SERIAL_PORT_SEARCH = value
                elif key == 'FORCE_COM_PORT':
                    FORCE_COM_PORT = value
                elif key == 'TOGGLE_KEY_MOUSE':
                    # Safe conversion for hex or decimal
                    TOGGLE_KEY_MOUSE = int(value, 0)
    except Exception as e:
        print(f"[Warning] Config load error: {e}. Using defaults.")

class Colorant:
    LOWER_COLOR = np.array([140, 120, 180])
    UPPER_COLOR = np.array([160, 200, 255])

    def __init__(self, x, y, xfov, yfov, FLICKSPEED, MOVESPEED):
        readconfig()
        self.arduinomouse = ArduinoMouse()
        self.grabber = Capture(x, y, xfov, yfov)
        self.flickspeed = FLICKSPEED
        self.movespeed = MOVESPEED
        
        # Start the listener thread
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()
        
        self.toggled = False
        self.window_toggled = False
        
    def close(self):
        self.arduinomouse.close()
        
    def toggle(self):
        self.toggled = not self.toggled
        time.sleep(0.2)

    def listen(self):
        try:
            print("[Info] Aimbot thread started. (ULTRA INSANE Mode)")
            while True:
                # F2 Toggle Window (Always active)
                if win32api.GetAsyncKeyState(0x71) < 0:
                    toggle_window(self)
                    time.sleep(0.2)
                
                # Only check aim keys if Enabled
                if self.toggled:
                    # Mouse Button (Aim)
                    if win32api.GetAsyncKeyState(TOGGLE_KEY_MOUSE) < 0:
                        self.process("move")
                    
                    # Alt (Click)
                    elif win32api.GetAsyncKeyState(0x12) < 0: 
                        self.process("click")
                    
                    # Ctrl (Flick)
                    elif win32api.GetAsyncKeyState(0x11) < 0: 
                        self.process("flick")
                        
                time.sleep(0.001) # Prevent high CPU usage
                
        except Exception as e:
            print(f"\n[CRITICAL ERROR] Thread crashed: {e}")
            traceback.print_exc()

    def process(self, action):
        try:
            screen = self.grabber.get_screen()
            hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.LOWER_COLOR, self.UPPER_COLOR)
            dilated = cv2.dilate(mask, None, iterations=3) 
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return

            contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(contour)
            center = (x + w // 2, y + h // 2)
            
            # --- HEADSHOT OFFSET TUNING ---
            # 0.12 = Head Level (Adjusted for tracking)
            y_offset = int(h * 0.12)

            if action == "move":
                cX = center[0]
                cY = y + y_offset
                x_diff = cX - self.grabber.xfov // 2
                y_diff = cY - self.grabber.yfov // 2

                # --- STICKY TRACKING LOGIC ---
                
                # 1. Micro Deadzone: 1px 
                # Allows micro-adjustments when you are moving (strafing).
                if abs(x_diff) <= 1 and abs(y_diff) <= 1:
                    return

                current_speed = self.movespeed

                # 2. Distance Acceleration:
                # Snap instantly if far away.
                if abs(x_diff) > 30 or abs(y_diff) > 30:
                    current_speed = self.movespeed * 1.15

                # 3. Sticky Glue: 
                # When close (tracking range), we BOOST speed slightly to compensate for your own movement.
                # This keeps the crosshair "glued" to the head while you strafe.
                elif abs(x_diff) < 15 and abs(y_diff) < 15:
                     current_speed = self.movespeed * 1.05 

                self.arduinomouse.move(x_diff * current_speed, y_diff * current_speed)

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
                self.arduinomouse.flick(-flickx, -flicky)
        except Exception as e:
             # Just print small errors without crashing the whole loop
            print(f"Error in process: {e}")
