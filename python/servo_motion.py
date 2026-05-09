#Servo motor test code
# import RPi.GPIO as GPIO
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import time
import subprocess
subprocess.run(['sudo', '/home/aarc_portable_rotator/rot-env/lib/python3.13/site-packages/pigpio-79/pigpiod'])

factory = PiGPIOFactory()
SetAngleVal = 90
pwmMax=2.5
pwmMin=0.5
frequency=50
period=1/frequency*1000
myGPIO=16
MoveOn = False


servo = Servo(myGPIO, initial_value=None, min_pulse_width=pwmMin/1000, max_pulse_width=pwmMax/1000, pin_factory=factory) # intiail value set to none to prevent max force angle changes
# Max force angle changes still exist. This bugfix didnt work :)

GlobalAngle = 90
AngleOffset = 0
with open("ServoSaveState.txt", "r") as file:
    lines = file.readlines()
    GlobalAngle = float(lines[0])
    AngleOffset = float(lines[1])       

# servo takes in values between -1 and 1 for full range of motion
# Input from gpredict will be in degrees: 0 to 90
def sign(x):
    return (x>0)-(x<0)

def move(angle):
    global GlobalAngle
    global AngleOffset
    # Servo motor ranges 270 deg.
    # On the rotator, 22.5deg is level with horizon.
    # 5 degrees added to make the rotator level
    # (angle/90*5) added to compensate for an odd non-linearity
    angle1 = (float(angle) + 22.5 + 5) + (float(angle)/90*5)
    angle2 = (angle1-135)/(135)
    #print(angle)
    servo.value = angle2
    with open("ServoSaveState.txt", "w") as file:
        file.write(str(angle)+"\n")
        file.write(str(AngleOffset))
        GlobalAngle = angle
        
    
def SetAngle(angle):
    global SetAngleVal
    SetAngleVal = angle
    print("Servo Setpoint |", SetAngleVal)

def MoveSlow(DegreesPerSecond = 10):
    global GlobalAngle
    global SetAngleVal
    global MoveOn
    AngleDifference = SetAngleVal - GlobalAngle
    TimeStep = 1e-3
    Tolerance = True
    while MoveOn & Tolerance:
        TimeStart = time.perf_counter()
        #print("TimeStep -", TimeStep)
        Increment = sign(AngleDifference)*min(abs(AngleDifference),DegreesPerSecond*TimeStep)
        #print("Setpoint -", Increment+GlobalAngle, Increment)
        move(Increment+GlobalAngle)
        AngleDifference = SetAngleVal - GlobalAngle
        Tolerance = not(ToleranceCheck(1e-1))
        TimeStop = time.perf_counter()
        TimeStep = TimeStop - TimeStart

def Start():
    global MoveOn
    MoveOn = True
    print("Motor Started")
            
def Stop():
    global MoveOn
    MoveOn = False
    print("Motor Stopped")
    
def ToleranceCheck(Tolerance):
    global SetAngleVal
    global GlobalAngle
    #print("Tolerance Values -", SetAngleVal, GlobalAngle)
    return Tolerance>abs(SetAngleVal - GlobalAngle)

def GetAngle():
    global GlobalAngle
    return GlobalAngle

def OffsetAngle(angle):
    global AngleOffset
    AngleOffset = angle
    
def GetOffsetAngle():
    global AngleOffset
    return AngleOffset
    