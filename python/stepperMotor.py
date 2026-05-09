import sys
import time
import RPi.GPIO as GPIO

#Select RPI GPIO pins
IN1 = 16
IN2 = 24
IN3 = 18
IN4 = 26

#Set pins to output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

#Start program with motrs at rest
GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(IN3, GPIO.LOW)
GPIO.output(IN4, GPIO.LOW)

#stepper motor sequence for full step
step_seq = [
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 0, 1],
    ]

# Half Step
# step_seq = [
#     [1, 0, 1, 0],
#     [0, 0, 1, 0],
#     [0, 1, 1, 0],
#     [0, 1, 0, 0],
#     [0, 1, 0, 1],
#     [0, 0, 0, 1],
#     [1, 0, 0, 1],
#     [1, 0, 0, 0],
#     ]


def set_step(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)

def stepper_step(delay, steps, direction):
    if direction > 0:
        for _ in range(steps):
            for step in step_seq:
                set_step(step[0], step[1], step[2], step[3])
                time.sleep(delay)
        set_step(0, 0, 0, 0)
    elif direction < 0:
        for _ in range(steps):
            for step in reversed(step_seq):
                set_step(step[0], step[1], step[2], step[3])
                time.sleep(delay)
        set_step(0, 0, 0, 0)
    else:
        print("Invalid direction input. Input \"direction = -1\" for reverse or \"direction = 1\" for forward")
        
    
            
try:
    #while True:
        stepper_step(0.001, 80, 1)
        time.sleep(1)
        stepper_step(0.001, 80, -1)
        time.sleep(1)
        stepper_step(0.001, 80, 1)
        time.sleep(1)
        stepper_step(0.001, 80, -1)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()