"""
YubiLock - USB Device Monitoring and PC Locking Program

Coded by: ChatGPT (https://chat.openai.com/)
Imagined and Debugged by: DannyDzNuts (https://github.com/DannyDzNuts)

Description:
This program monitors USB device removal events on a Windows system and locks the PC if a recognized YubiKey/USB device is removed. It also maintains a log of removal events in the console.

Instructions:
1. Customize the list of known YubiKey device IDs and their nicknames in the 'yubikey_devices' list.
2. Set the desired rate limit duration for log messages (in seconds) using 'rate_limit_duration'.
   WARNING: Setting rate_limit_duration too short may result in multiple log messages per removal event.
3. Run the program to start USB device monitoring.

Dependencies:
- colorama
- pywin32

To install dependencies:
pip install pipenv  # If not already installed
pipenv shell
pipenv install colorama pywin32

"""

import win32com.client
import ctypes
from datetime import datetime
import time
from colorama import Fore, Style, init
import os

# Function to set the console title
def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

# Function to clear the screen
def clear_screen():
    # Clear the screen (works on Windows)
    os.system("cls" if os.name == "nt" else "clear")

# Function to print the banner at the top of the console
def print_banner():
    # Print the banner at the top of the console
    print("[Coded by ChatGPT, Imagined by DannyDzNuts]")

# Function to get YubiKey information based on device ID
def get_yubikey_info(device_id):
    # REPLACE DEVICE ID AND NICKNAME WITH YOUR OWN
    # Define a list of known YubiKey device IDs and their corresponding nicknames with colors
    yubikey_devices = [
        {"device_id": r"INSERT DEVICE ID", "nickname": "INSERT NICKNAME", "color": Fore.RED},
        # Add more YubiKeys and their nicknames with colors here
    ]

    for yubikey in yubikey_devices:
        if device_id == yubikey["device_id"]:
            return yubikey

    return {"nickname": "YubiKey", "color": Fore.GREEN}  # Default color

# Function to print colored message
def colored_print(message, color=Fore.WHITE):
    print(color + message + Style.RESET_ALL)

# Function to clear the second line and move all other lines up
def clear_second_line_and_shift_lines_up(lines):
    for i in range(1, len(lines) - 1):
        lines[i] = lines[i + 1]
    lines[-1] = ""

    clear_screen()
    print_banner()
    for line in lines:
        print(line)

# Function to detect USB changes
def detect_usb_changes():
    global last_removal_time

    # Initialize a circular buffer to store the last 10 lines
    lines = [""] * 10

    try:
        wmi = win32com.client.GetObject("winmgmts:")
        query = "SELECT * FROM __InstanceOperationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_PnPEntity'"
        watcher = wmi.ExecNotificationQuery(query)

        while True:
            usb_event = watcher.NextEvent()
            if usb_event.Path_.Class == "__InstanceDeletionEvent":
                device_id = usb_event.TargetInstance.PNPDeviceID
                current_time = datetime.now()
                if last_removal_time is None or (current_time - last_removal_time).total_seconds() > rate_limit_duration:
                    current_time = datetime.now()
                    time_str = current_time.strftime("%m-%d-%Y, %H:%M:%S")
                    yubikey_info = get_yubikey_info(device_id)
                    nickname = yubikey_info["nickname"]
                    nickname_color = yubikey_info["color"]
                    colored_time = f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}{time_str}{Style.RESET_ALL}"
                    colored_nickname = f"{nickname_color}{Style.BRIGHT}{nickname}{Style.RESET_ALL}"
                    colored_message = f"{colored_time}: Token Removed: {colored_nickname}"

                    # Check if there are already 10 lines in the buffer
                    if len(lines) >= 10:
                        clear_second_line_and_shift_lines_up(lines)
                        lines[-1] = colored_message
                    else:
                        lines.append(colored_message)

                    clear_screen()
                    print_banner()
                    for line in lines:
                        print(line)

                    LockWorkStation()
                    last_removal_time = current_time

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Initialize colorama
    init(autoreset=True)

    # Define the LockWorkStation function from the Windows API
    LockWorkStation = ctypes.windll.user32.LockWorkStation

    # Initialize variables to track the last removal event time and the rate-limiting duration (in seconds)
    last_removal_time = None
    rate_limit_duration = 5  # Adjust this value as needed

    try:
        print_banner()  # Print the banner at program start

        # Start USB detection
        detect_usb_changes()

    except KeyboardInterrupt:
        print("Program terminated by user.")
