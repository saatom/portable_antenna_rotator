# Written by Wyatt Richrads to interface with the TB6600 stepper driver
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time

step = 7
dir = 8
ena = 25
steps_per_rev = 800*32
azimuth = RpiMotorLib.A4988Nema(dir, step, (-1, -1, -1), "A4988")
GPIO.setup(ena, GPIO.OUT)

globalAngle = 0

def move(angle, speed=50000): # Use to move azimuth relatively; angle is in degrees, speed is in steps/sec
	global globalAngle
	direction = angle<0
	globalAngle = globalAngle + angle
	angle = abs(angle)

	stp = int(angle/360 * steps_per_rev)
	GPIO.output(ena, GPIO.LOW)
	azimuth.motor_go(direction, "Full", stp, 1/speed, False, 0)
	GPIO.output(ena, GPIO.HIGH)

def set(angle, speed=50000): # Use to send azimuth to specific location
	global globalAngle
	dAngle = float(angle) - float(globalAngle)
	move(dAngle, speed)
	print("Stepper Setpoint |", globalAngle)

def updateAngle(val): # Use to update angle
	global globalAngle
	globalAngle = val

print("Stepper Library Loaded")