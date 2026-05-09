# Help: https://pypi.org/project/pynmeagps/
import pynmeagps
import datetime
from serial import Serial
from pynmeagps import NMEAReader
from pynmeagps import latlon2dms, latlon2dmm

def GPSVal():
    with Serial('/dev/serial0', 9600, timeout=3) as stream:
        gpsVals = []
        GGA = 0
        RMC = 0
        
        nmr = NMEAReader(stream)
        
        if nmr is not None:
            
            while(GGA == 0):
                #print("While 1")
                #try:
                nmr = NMEAReader(stream)
                raw_data, parsed_data = nmr.read()
                if parsed_data is not None:
                    #return parsed_data.lat, parsed_data.lon, parsed_data.time, parsed_data. 
                    # Access the msgID to identify the message type
                    message_type = parsed_data.msgID
                    #print(message_type)

                    # Retrieve the date based on the message type
                    if message_type in ['GGA']:  # Example message types
                        GGA = 1
                        latitude = parsed_data.lat
                        longitude = parsed_data.lon
                        altitude = parsed_data.alt
                        gpsVals.append(latitude)
                        gpsVals.append(longitude)
                        gpsVals.append(altitude)
                    
            while(RMC == 0):
                #print("While 2")
                nmr = NMEAReader(stream)
                raw_data, parsed_data = nmr.read()
                
                if parsed_data is not None:
                    message_type = parsed_data.msgID
                    #print(message_type)
                    if message_type in ['RMC']:  # Example message types
                        RMC = 1
                        date = parsed_data.date
                        date_string = date.strftime('%d-%b-%Y')
                        time = parsed_data.time
                        time_string = time.strftime('%H:%M:%S')
                        gpsVals.append(date_string)
                        gpsVals.append(time_string)
            
            return gpsVals
            GGA = 0
            RMC = 0
            
        else:
            return "","",""


# def GPSVal():
#     with Serial('/dev/serial0', 9600, timeout=3) as stream:
#         try:
#             nmr = NMEAReader(stream)
#             raw_data, parsed_data = nmr.read()
#             if parsed_data is not None:
#                 return parsed_data.lat, parsed_data.lon, parsed_data.time, parsed_data.date
#         except:
#             return "", "", ""


def GPS_loc():
    with Serial('/dev/serial0', 9600, timeout=3) as stream:
        try:
            nmr = NMEAReader(stream)
            raw_data, parsed_data = nmr.read()
            if parsed_data is not None:
                
                return parsed_data.lat, parsed_data.lon
        except:
            return "", ""
    
def GPS_time():
    with Serial('/dev/serial0', 9600, timeout=3) as stream:
        try:
            nmr = NMEAReader(stream)
            raw_data, parsed_data = nmr.read()
            if parsed_data is not None:
                return parsed_data.time
        except:
            return ""
        
def IsEnabled():
    try:
        t1 = GPSVal()
        print("GPS | Working")
        return True
    except:
        print("GPS | Nope, doesn't work")
        return False
        
GPSValue = GPSVal()
print("GPS | ",GPSValue)
# IsEnabled()
# date = GPSValue[3]
# time = GPSValue[4]
# print(date, time)
