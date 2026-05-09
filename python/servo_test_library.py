#Servo motor test code
import RPi.GPIO as GPIO
from time import sleep

pwmMax=2.5
pwmMin=0.5
frequency=50
period=1/frequency*1000
myGPIO=16
GPIO.setmode(GPIO.BCM)
GPIO.setup(myGPIO,GPIO.OUT)
pwm=GPIO.PWM(myGPIO,frequency)
pwm.start(0)


def move(angle):
    b = pwmMin/period*100
    a = 270/(pwmMax/period*100-b)
    duty = float(angle)/a+b
    pwm.ChangeDutyCycle(duty)
    print(angle)