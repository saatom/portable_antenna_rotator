#Old code do not use
import serial
import time
import sys
import re

serial = serial.Serial("/dev/serial0")
gpgll_info = "$GPGLL,"
GPGLL_buffer = 0
NMEA_buffer = 0

def convert_to_degrees(raw_val):
    try:
        raw_val = (float)(raw_val)
        decimal_val = raw_val/100
        degrees = int(decimal_val)
        mm_mmmm = (decimal_val - int(decimal_val))/0.6
        position = degrees + mm_mmmm
        position = "%.4f"%(position)
        return position
    except ValueError:
        return 0        

def DoxxUrself():
    try:
        while True:
            received_data = (str)(serial.readline()) #read NMEA string received
            GPGLL_data_available = received_data.find(gpgll_info) #check for NMEA GPGGA String
            if(GPGLL_data_available>0):
                GPGLL_buffer = received_data.split("$GPGLL,",1)[1]
                NMEA_buffer = (GPGLL_buffer.split(','))
                NMEA_time = []
                NMEA_latitude = []
                NMEA_longitude = []
                NMEA_time = NMEA_buffer[4]
                NMEA_latitude = NMEA_buffer[0]
                NMEA_longitude = NMEA_buffer[2]
                
                print("NMEA Time: ", NMEA_time,'\n')
                #print("NMEA latitude: ", NMEA_latitude,'\n')
                lat = (NMEA_latitude)
                lat = convert_to_degrees(lat)
                lon = (NMEA_longitude)
                lon = convert_to_degrees(lon)
                print("NMEA Latitude: ", lat,NMEA_buffer[4],"NMEA Longitude: ", lon,NMEA_buffer[2],'\n')
                
    except KeyboardInterrupt:
        sys.exit(0)
    
try:
    while True:
        received_data = (str)(serial.readline()) #read NMEA string received
        GPGLL_data_available = received_data.find(gpgll_info) #check for NMEA GPGGA String
        if(GPGLL_data_available>0):
            GPGLL_buffer = received_data.split("$GPGLL,",1)[1]
            NMEA_buffer = (GPGLL_buffer.split(','))
            NMEA_time = []
            NMEA_latitude = []
            NMEA_longitude = []
            NMEA_time = NMEA_buffer[4]
            NMEA_latitude = NMEA_buffer[0]
            NMEA_longitude = NMEA_buffer[2]
            
            print("NMEA Time: ", NMEA_time,'\n')
            #print("NMEA latitude: ", NMEA_latitude,'\n')
            lat = (NMEA_latitude)
            lat = convert_to_degrees(lat)
            lat_mkr = NMEA_buffer[1]
            lon = (NMEA_longitude)
            lon = convert_to_degrees(lon)
            lon_mkr = NMEA_buffer[3]
            print("NMEA Latitude:", lat,lat_mkr,"NMEA Longitude:", lon,lon_mkr,'\n')
            print(GPGLL_buffer)
except KeyboardInterrupt:
    sys.exit(0)
