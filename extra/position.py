import pyautogui
import keyboard
import time

#the loop is for running the program in background
#the start and stop timers are for ensuring that a single key press
#results in only one coordinate being identified

stop=0

while True:
    start=time.time()
    #Get the coordinates of mouse pointer or cursor everytime 'z' key is pressed
    if keyboard.is_pressed('z') and (start-stop)>1:
        # Get the X and Y coordinates of the mouse pointer or curser
        position = pyautogui.position()
        print(position)
        stop=time.time()
