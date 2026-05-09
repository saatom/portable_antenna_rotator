import smbus
import time

bus = smbus.SMBus(1)
address_accel = 0x19
address_mag   = 0x1e

global x

def get_accel():
    xH = bus.read_byte_data(address_mag,0x03)
    xL = bus.read_byte_data(address_mag,0x04)

    yH = bus.read_byte_data(address_mag,0x07)
    yL = bus.read_byte_data(address_mag,0x08)
    
    zH = bus.read_byte_data(address_mag,0x05)
    zL = bus.read_byte_data(address_mag,0x06)
    
    return xH, xL
    
while True:
    get_accel();
    print(xH, xL)
    #print('\n y')
    #print('\n z')
    time.sleep(1)