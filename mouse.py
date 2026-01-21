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
            file1 = open("config.txt", "r")
        except:
            return
        
        filelines = file1.readlines()
        for line in filelines:
            if line[0]=="#" or line == "\n"or line == "":
                continue
            splitedline = line.split("=") 
            splitedline[0] = splitedline[0].strip().replace("\n","")
            splitedline[1] = splitedline[1].strip().replace("\n","")
            if splitedline[0] == 'SERIAL_PORT_SEARCH':
                SERIAL_PORT_SEARCH = splitedline[1]
            elif splitedline[0] == 'FORCE_COM_PORT' and splitedline[1].startswith("COM"):
                FORCE_COM_PORT = splitedline[1]

    def __init__(self, filter_length=3):
        self.read_config()

        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 1
        self.serial_port.port = self.find_serial_port()
        self.filter_length = filter_length
        self.x_history = [0] * filter_length
        self.y_history = [0] * filter_length
        try:
            self.serial_port.open()
        except serial.SerialException:
            print(colored('[Error]', 'red'), colored('ColorVant is already open or serial port in use by another app. Close ColorVant and other apps before retrying.', 'white'))
            time.sleep(10)
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
        self.x_history.append(x)
        self.y_history.append(y)

        self.x_history.pop(0)
        self.y_history.pop(0)

        smooth_x = int(sum(self.x_history) / self.filter_length)
        smooth_y = int(sum(self.y_history) / self.filter_length)

        finalx = smooth_x + 256 if smooth_x < 0 else smooth_x
        finaly = smooth_y + 256 if smooth_y < 0 else smooth_y
        self.serial_port.write(b"M" + bytes([int(finalx), int(finaly)]))

    def flick(self, x, y):
        x = x + 256 if x < 0 else x
        y = y + 256 if y < 0 else y
        self.serial_port.write(b"M" + bytes([int(x), int(y)]))
        
    def click(self):
        delay = random.uniform(0.01, 0.1)
        self.serial_port.write(b"C")
        time.sleep(delay)
        
    def close(self):
        self.serial_port.close()

    def __del__(self):
        self.close()
