import serial
import serial.tools.list_ports
import random
import time
import pyautogui
import sys
from termcolor import colored

SERIAL_PORT_SEARCH = "Auto"
FORCE_COM_PORT = ""

class ArduinoMouse:
    def read_config(self):
        global SERIAL_PORT_SEARCH
        global FORCE_COM_PORT
        try:
            with open("config.txt", "r") as f:
                for line in f:
                    if line.strip().startswith("#") or line.strip() == "":
                        continue
                    key, value = [part.strip() for part in line.split("=", 1)]
                    if key == 'SERIAL_PORT_SEARCH':
                        SERIAL_PORT_SEARCH = value
                    elif key == 'FORCE_COM_PORT' and value.startswith("COM"):
                        FORCE_COM_PORT = value
        except:
            pass

    def __init__(self):
        self.read_config()
        self.serial_port = serial.Serial()
        # CHANGED: 115200 to match your Arduino sketch!
        self.serial_port.baudrate = 115200 
        self.serial_port.timeout = 0.01
        self.serial_port.port = self.find_serial_port()
        
        try:
            self.serial_port.open()
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            print(colored('[SPEED]', 'green'), "115200 Baud (Synced with Arduino) ✓")
        except serial.SerialException:
            print(colored('[Error]', 'red'), 'Serial port in use. Close other apps.')
            sys.exit()

    def search_for_arduino_by_description(self):
        port = next((port for port in serial.tools.list_ports.comports() if "Arduino" in port.description), None)
        return port
       
    def get_port_info_by_name(self,port_name):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if port.device == port_name:
                return port
        return None 

    def find_serial_port(self):
        port = None
        
        if FORCE_COM_PORT != "":
            print(colored('[Info]', 'green'), colored('Testing forced com port: '+FORCE_COM_PORT, 'white'))
            port = self.get_port_info_by_name(FORCE_COM_PORT)
            if port is None:
                print(colored('[Error]', 'red'), colored('In your config, the '+FORCE_COM_PORT+" was not found.", 'white'))
                port_name = input("Enter just the number of COM port: ")
                if not port_name.startswith("COM"):
                    port_name = "COM" + port_name
                port = self.get_port_info_by_name(port_name)
        elif SERIAL_PORT_SEARCH.lower()[0] == "a":
            port = self.search_for_arduino_by_description()

        elif SERIAL_PORT_SEARCH.lower()[0] == "m":
            print(colored('[Info]', 'green'), colored('Config says to start by asking manually.', 'white'))
            port_name = input("Enter just the number of COM port: ")
            if not port_name.startswith("COM"):
                    port_name = "COM" + port_name
            port = self.get_port_info_by_name(port_name)
        else:
            port = self.search_for_arduino_by_description()
        
        if port is not None: 
            return port.device
        else:
            port = None
            print(colored('[Error]', 'red'), colored('Unable to find serial port or the Arduino device, check usb connection or enter COM number manually:', 'white'))
            while port is None: 
                print(colored('[Status]', 'green'),end=" ")
                search_choise = input("Search for Arduino automatically or enter com manualy? (Auto/Manual): ")
                firstletter = search_choise.lower()[0]
                if firstletter == "a":
                    port = self.search_for_arduino_by_description()
                elif firstletter == "m":
                    port_name = input("Enter just the number of COM port: ")
                    if not port_name.startswith("COM"):
                            port_name = "COM" + port_name
                    port = self.get_port_info_by_name(port_name)
                else:
                    print(colored('[Error]', 'red'), colored("What?", 'white'))
                    
                if port is None:
                    print(colored('[Error]', 'red'), colored("Still didn't find it, retry.", 'white'))
                else:
                    print(colored('[Info]', 'green'), "Found it!")
                    return port.device
            print(colored('[Info]', 'green'), "Exiting program.")
            time.sleep(10)
            sys.exit()

    def move(self, x, y):
        # 1. Minimum Move Check
        if x != 0 and abs(x) < 1: x = 1 if x > 0 else -1
        if y != 0 and abs(y) < 1: y = 1 if y > 0 else -1

        # 2. Rounding
        val_x = int(round(x))
        val_y = int(round(y))

        # 3. Clamping (-127 to 127) for signed char compatibility
        val_x = max(-127, min(127, val_x))
        val_y = max(-127, min(127, val_y))
        
        if val_x == 0 and val_y == 0:
            return

        # 4. Convert to unsigned bytes
        x_byte = val_x & 0xFF
        y_byte = val_y & 0xFF
        
        self.serial_port.write(bytes([77, x_byte, y_byte]))

    def flick(self, x, y):
        val_x = int(round(x))
        val_y = int(round(y))
        
        val_x = max(-127, min(127, val_x))
        val_y = max(-127, min(127, val_y))
        
        if val_x == 0 and val_y == 0:
            return
            
        x_byte = val_x & 0xFF
        y_byte = val_y & 0xFF
        
        self.serial_port.write(bytes([77, x_byte, y_byte]))

    def click(self):
        self.serial_port.write(b'C')

    def close(self):
        if self.serial_port.is_open:
            self.serial_port.close()

    def __del__(self):
        self.close()
