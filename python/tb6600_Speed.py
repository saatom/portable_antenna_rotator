# Written By Isaac Newton to control the Stepper Motor with keystrokes
import time
from pynput import keyboard
from RpiMotorLib import RpiMotorLib
import RPi.GPIO as GPIO
import tb6600
import pynput
import ADC_readPot as Pot

moving = False
direction = True

step = 7
dir = 8
ena = 25
steps_per_rev = 800
stepmotor = RpiMotorLib.A4988Nema(dir, step, (-1, -1, -1), "A4988")
GPIO.setup(ena, GPIO.OUT)
temp = 1.7788667867061374 - 1.3080399182103946
temp1 = 3.5869844660786767 - 0.9620918607135228
print(90*temp1/temp)

def on_press(key):
    global moving, direction
    try:
        if not moving:
            if key == keyboard.Key.right:
                direction = True
                moving = True
            elif key == keyboard.Key.left:
                direction = False
                moving = True
    except AttributeError:
        pass

def on_release(key):
    global moving
    if key in [keyboard.Key.left, keyboard.Key.right]:
        moving = False
    if key == keyboard.Key.esc:
        return False
    
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    while listener.running:
        
        if moving and direction:
            tb6600.move(1)
            try:
                Angle = Pot.ReadPot()[2]
                CurrentAngle = 472 * (Angle - (3.5869844660786767 + 0.9620918607135228)/2) / (3.5869844660786767 - 0.9620918607135228)
                print(Angle, CurrentAngle)
            except:
                print("")
        elif moving and not direction:
            tb6600.move(-1)
            try:
                Angle = Pot.ReadPot()[2]
                CurrentAngle = 472 * (Angle - (3.5869844660786767 + 0.9620918607135228)/2) / (3.5869844660786767 - 0.9620918607135228)
                print(Angle, CurrentAngle)
            except:
                print("")
        else:
            try:
                Angle = Pot.ReadPot()[2]
                CurrentAngle = 472 * (Angle - (3.5869844660786767 + 0.9620918607135228)/2) / (3.5869844660786767 - 0.9620918607135228)
                print(Angle, CurrentAngle)
            except:
                print("")
      
except KeyboardInterrupt:
    print("Stopping")
finally:
    GPIO.cleanup()