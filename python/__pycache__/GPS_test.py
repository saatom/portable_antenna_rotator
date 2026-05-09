import serial
import time
import sys
import re

serial = serial.Serial("/dev/serial0")
gpgga_info = "$GPGGA,"
GPGGA_buffer = 0
NMEA_buffer = 0

def convert_to_degrees(raw_value):
    decimal_val = raw_val/100
    degrees = int(decimal_val)
    mm_mmmm = (decimal_val - int(decimal_val))/0.6
    position = degrees + mm_mmmm
    position = "%.4f"%(position)
    return position

try:
    while True:
        received_data = (str)(serial.readline()) #read NMEA string received
        GPGGA_data_available = received_data.find(gpgga_info) #check for NMEA GPGGA String
        if(GPGGA_data_available>0):
            GPGGA_buffer = received_data.split("$GPGGA,",1)[1]
            NMEA_buffer = (GPGGA_buffer.split(','))
            NMEA_time = []
            NMEA_latitude = []
            NMEA_longitude = []
            NMEA_time = NMEA_buffer[0]
            NMEA_latitude = NMEA_buffer[1]
            NMEA_longitude = NMEA_buffer[3]
            
            print("NMEA Time: ", NMEA_time,'\n')
            lat = (float)(NMEA_latitude)
            lat = convert_to_degrees(lat)
            lon = (float)(NMEA_longitude)
            lon = convert_to_degrees(lon)
            print("NMEA Latitude: ", lat,"NMEA Longitude: ", lon,'\n')
            
except KeyboardInterrupt:
    sys.exit(0) 
        