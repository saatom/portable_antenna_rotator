from gpiozero import LED
from time import sleep

led = LED(20)
led2 = LED(21)

try:
    while True:
        led.toggle()
        led2.toggle()
        sleep(0.1)
except KeyboardInterrupt: 
    pass
  