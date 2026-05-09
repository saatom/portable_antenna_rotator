import tkinter as tk # Used for UI
import subprocess # Used to run Gpredict
import tb6600 as stepper # Custom library for stepper driver
subprocess.run(['sudo', '/home/aarc_portable_rotator/rot-env/lib/python3.13/site-packages/pigpio-79/pigpiod'])
import servo_motion as servo # Makeshift library for servo
from RpiMotorLib import RpiMotorLib # I dont know what this is, but its needed
import RPi.GPIO as GPIO # Pi GPI usage. Dont know, but needed
from time import sleep # I hate sleeping
import socket # Used forserial port reading (gpredict)
import time # Used for
import threading as tr
import math
try:
    import GPS
    GPSEnable = True
except:
    print("Is the GPS connected?")
    GPSEnable = False
    
try:    
    import ADC_readVolt as Volt
    VoltEnable = True
except:
    print("Is the voltmeters connected?")
    VoltEnable = False
    
try:
    import ADC_readPot as Pot
    PotEnable = True
except:
    print("Is the rotator connected?")
    PotEnable = False
    
try:
    import ThreeDsensor as TDS
    TDSEnable = True
except:
    print("Is the 3D Sensor connected")
    TDSEnable = False
    

### Port setup
gp_ip = 'localhost'
gp_port = 4533                  #Standard rotator TCP port
global rotor_pos
rotor_pos=b'123.45\n67.89\n'    #Simulated rotor position


#start function
print('\nWaiting for gpredict command to engage your rotor...')

gp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gp.bind((gp_ip, gp_port))
gp.listen(1)
conn, addr = 0, 0
gpredict_open = False

### Stepper setup

# Left  - 202 degrees
# Right - 202 degrees

moving = False
direction = True

step = 7
dir = 8
ena = 25
steps_per_rev = 800
stepmotor = RpiMotorLib.A4988Nema(dir, step, (-1, -1, -1), "A4988")
GPIO.setup(ena, GPIO.OUT)
CurrentAngle = 0
CA1, CA2, CA3, CA4, CA5 = 0, 0, 0, 0, 0

PotentiometerLeftMax = 3.5869844660786767
PotentiometerRightMax = 0.9620918607135228

### Lots of functions

def UpdateGpredict(Lat, Lon, Alt):
    # Update GPS.qth - /home/aarc_portable_rotator/.config/Gpredict/GPS.qth
    GPSFile = [	"[QTH]\n",
                "DESCRIPTION=Automatically updated GPS Location\n",
                "LOCATION=Portable Antenna Rotator\n",
                "LAT=" + str(Lat) + "\n",
                "LON=" + str(Lon) + "\n",
                "ALT=" + str(Alt) + "\n",
                #"ALT=140\n",
                "WX=PAFA\n",
                "QTH_TYPE=0"]
    
    with open("/home/aarc_portable_rotator/.config/Gpredict/GPS.qth", "w") as file:
        file.writelines(GPSFile)
    
    print(f"GPS Updated | ({Lat}, {Lon}, {Alt})")

def OpenGpredict():
    #os.system("calc.exe")
    GPredictProcess = subprocess.Popen(['gpredict']) 
    #start function
    print('\nWaiting for gpredict command to engage your rotor...')

    ### Setup for ports
    SetupSerial()
    ReadSerial()
    
    # Gpredict will crash PARR when closed. It can also do it for no reason whatsoever. Should be fixed I think :thumbsup:
        
def SetupSerial():
    global conn, addr
    conn, addr = gp.accept()
    global gp_connected
    gp_connected = True
    print('\nConnection address:', addr)
    global gpredict_open
    gpredict_open = True
          
def ReadSerial():
    global CurrentAngle
    global conn, addr
    global gp_connected
    global rotor_pos
    packet = b''
    if not conn._closed:
        packet = conn.recv(30)
    print('\ngpredict command received:', packet)

    if packet == b'q\n':      #gpredict is closing the connection
        conn.close()
        print('Connection terminated by Gpredict...')
        #gp.close()
        gp_connected=False
        
    elif packet == b'p\n':    #gpredict requesting rotor position
        conn.send(rotor_pos) #fake rotor position back to gpredict
        print('response to "get_pos" command sent:', rotor_pos)
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
    elif packet[0:2] == b'P ':#gpredict setting rotor position
        mstr=b'RPRT 0\n'    #fake "no error' back to gpredict    
        conn.send(mstr)
        print('response to "set_pos" command sent:', mstr)
        rotor_pos = packet[2:].replace(b" ", b"\n")
        print(rotor_pos.decode('utf-8'))
        Azimuth = packet[2:packet.find(b" ",2)-1]
        Elevation = packet[packet.find(b" ",2)+1:packet.find(b"\n",packet.find(b"\n",2)-1)]
        print(Azimuth, Elevation)
        
        # Convert Azimuth from 360 to +-180
        ConvertedAzimuth = float(Azimuth)
        AngleChange = abs(ConvertedAzimuth - CurrentAngle)
        GoodSpeed1 = 50000*min(1,AngleChange/300) # Adjustement for angle speed in case of low angles
        print("AngleChange and GoodSpeed1 - ",AngleChange, GoodSpeed1)
        
        MotorPairMove(-ConvertedAzimuth,float(Elevation),GoodSpeed1)

    elif packet == b'':
        print('No message', packet)
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
    else:
        print('Other command', packet)
        mstr=b'\n'          # fake ack back to gpredict    
        conn.send(mstr)
        print('response sent:', mstr)
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
    
    gpredict_open = CheckGpredictStatus()
    
    if not gp_connected:
        SetupSerial()
        root.after(100, ReadSerial)
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
    elif gpredict_open:
        root.after(100, ReadSerial)
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()
        StepperAngleCheck()

def OpenMaidenHead():
    print("Maidenhead Locator Converter would open here!")  # Placeholder for actual Maidenhead Locator Converter opening code

def UpdateGPSData():
    GPSVal = GPS.GPSVal()
    gps_lat = GPSVal[0]
    gps_lon = GPSVal[1]
    gps_alt = GPSVal[2]  # meters above sea level
    gps_date = GPSVal[3] # DD MM(eg. MAR) YYYY UTC
    gps_time = GPSVal[4] # HH:MM:SS UTC
    
    GPS_Text.set("GPS Location: " + "Lat " + str(gps_lat) + ", Lon" + str(gps_lon) + "\nGPS Time: " + str(gps_time) + ", Alt: " + str(gps_alt))
    if (gps_lat+gps_lon):
        UpdateGpredict(gps_lat, gps_lon, gps_alt)


def UpdateMagneticHeading():
    MagVal = TDS.readMag()
    NorthAngle = math.degrees(math.atan2(MagVal[0],MagVal[1]))
    
    MagneticHeading_Text.set(f"Magnetometer\n{MagVal[0]:.4f} X\n{MagVal[1]:.4f} Y\n{MagVal[2]:.4f} Z\nNorth Angle | {NorthAngle:.2f}")

def UpdateAccelerometerData():
    AccVal = TDS.readAccl()
    PlanarAccel = (AccVal[0]**2 + AccVal[1]**2)**0.5
    LevelAngle = math.degrees(math.atan2(AccVal[2],PlanarAccel))

    Accelerometer_Text.set(f"Accelerometer\n{AccVal[0]:.4f} X\n{AccVal[1]:.4f} Y\n{AccVal[2]:.4f} Z\nLevel Angle | {LevelAngle:.2f}")  

def CheckMotorAngles():
    global CurrentAngle
    Motor_Azimuth.set(f"Azimuth | {CurrentAngle:.2f}")  # This would be replaced with actual motor angle checking and formatting
    Motor_Elevation.set(f"Elevation | {servo.GetAngle():.2f}")  # This would be replaced with actual motor elevation checking and formatting

def CheckGpredictStatus(): # Check if gpredict is open or not!!!
        try:
            subprocess.check_output(["pgrep", 'gpredict'])
            print("Gpredict is running")
            return True
        except subprocess.CalledProcessError:
            return False
    
def CurrentAngleAverage(AngleInput):
    global CA1, CA2, CA3, CA4, CA5, CurrentAngle
    CA5 = CA4
    CA4 = CA3
    CA3 = CA2
    CA2 = CA1
    CA1 = AngleInput
    CurrentAngle = (CA1+CA2+CA3+CA4+CA5)/5  
    
def StepperAngleCheck():
    global CurrentAngle
    CurrentVal = Pot.ReadPot()[2]
    print(CurrentVal)
    CurrentAngleTemp = 472 * (CurrentVal - (PotentiometerRightMax + PotentiometerLeftMax)/2) / (PotentiometerRightMax - PotentiometerLeftMax)
    CurrentAngleAverage(CurrentAngleTemp)
    print(CurrentAngle)
    stepper.updateAngle(CurrentAngle)
    print("Angle Set to: ", CurrentAngle)
    

def MotorPairMove(AzimuthSet, ElevationSet, speed=50000):
    print("Motors Moving")
    servo.SetAngle(ElevationSet)
    
    Elevation = tr.Thread(target=servo.MoveSlow)
    print("Elev thread created")
    Azimuth = tr.Thread(target=stepper.set, args=(AzimuthSet, speed))
    print("Azimuth thread created")
    
    Elevation.start()
    Azimuth.start()
    
    Azimuth.join()
    Elevation.join()
    print("Motors Finished")

def TestPath():
    MotorPairMove(0,0)
    # Azimuth
    MotorPairMove(-180,0, 10000)
    MotorPairMove(180,0, 20000)
    # Elevation
    MotorPairMove(0,0)
    MotorPairMove(0,90)
    # Azimuth & Elevation
    MotorPairMove(-180,0, 10000)
    MotorPairMove(180,90, 20000)
    # Restart
    MotorPairMove(0,90)

def UpdateAllData():
    global GPSEnable, TDSEnable, PotEnable, VoltEnable
    if GPSEnable:
        UpdateGPSData()
    if TDSEnable:
        UpdateMagneticHeading()
        UpdateAccelerometerData()
    if PotEnable:
        CheckMotorAngles()
    root.after(1000, UpdateAllData)  # Schedule the next update after 1000 milliseconds (1 second)

def OpenDiagnostics():
    MotorDebug = tk.Toplevel(root)
    MotorDebug.title("Motor Debug")
    MotorDebug.geometry("400x400") # Set the size of the new window
    
    OffsetValue = servo.GetOffsetAngle()
    ServoOffsetText = tk.StringVar()
    ServoOffsetText.set(f"ServoOffset | {OffsetValue:.4f} degrees")
    
    StepperDesc = tk.Label(MotorDebug, text="Stepper Angle").pack(pady=0)
    ManualStepperAngle = tk.Entry(MotorDebug)
    ManualStepperAngle.pack(pady=10)
    ServoDesc = tk.Label(MotorDebug, text="Servo Angle").pack(pady=0)
    ManualServoAngle = tk.Entry(MotorDebug)
    ManualServoAngle.pack(pady=10)
    OffsetDesc = tk.Label(MotorDebug, textvariable=ServoOffsetText).pack(pady=0)
    ServoOffset = tk.Entry(MotorDebug)
    ServoOffset.pack(pady=10)
    tk.Button(MotorDebug, text="Move", command=lambda: stepper.move(float(ManualStepperAngle.get()))).pack(side=tk.RIGHT, pady=5)
    tk.Button(MotorDebug, text="Set", command=lambda: MotorPairMove((float(ManualStepperAngle.get())), (float(ManualServoAngle.get())))).pack(side=tk.LEFT, pady=5)
    tk.Button(MotorDebug, text="Apply Servo Offset", command=lambda: UpdateOffset(float(ServoOffset.get()), ServoOffsetText)).pack(side=tk.BOTTOM,pady=5) # Doesnt work, not tested
    tk.Button(MotorDebug, text="Update Angle", command=StepperAngleCheck).pack(side=tk.BOTTOM,pady=5)
    tk.Button(MotorDebug, text="Preset Test", command=TestPath).pack(side=tk.BOTTOM, pady=5)

def UpdateOffset(offset, textbox):
    servo.OffsetAngle(offset)
    textbox.set(f"ServoOffset | {offset:.4f} degrees")
    
def setClockUTC():
    GPSVal = GPS.GPSVal()
    gps_date = GPSVal[3] # DD MM(eg. MAR) YYYY UTC
    gps_time = GPSVal[4] # HH:MM:SS UTC
    
    if(gps_date):
        gps_date = gps_date.replace('-',' ',2)
        run_str = f'{gps_date} {gps_time}'
        print(run_str)
        subprocess.run(['sudo', 'date', '-s',run_str])
        
        
servo.Stop()

root = tk.Tk()
root.title("Portable Antenna Rotator Router")
root.attributes('-zoomed',True)

GPS_Text = tk.StringVar()
GPS_Text.set("GPS Data: NOT ENABLED")  # Placeholder for GPS data

MagneticHeading_Text = tk.StringVar()
MagneticHeading_Text.set("Magnetic Heading: NOT ENABLED")  # Placeholder for magnetic heading

Accelerometer_Text = tk.StringVar()
Accelerometer_Text.set("Accelerometer Data: NOT ENABLED")  # Placeholder for accelerometer data

Motor_Azimuth = tk.StringVar()
Motor_Elevation = tk.StringVar()
Motor_Azimuth.set("Azimuth: LOADING...")  # Placeholder for motor azimuth
Motor_Elevation.set("Elevation: LOADING...")  # Placeholder for motor elevation

label = tk.Label(root, text="Welcome to the Portable Antenna Rotator Router!")
label.pack(pady=10)  # Add some vertical padding to the label

GPSData = tk.Label(root, textvariable=GPS_Text)  # Placeholder for GPS coordinates
GPSData.pack(pady=5)  # Add some vertical padding to the GPS label

MagneticHeading = tk.Label(root, textvariable=MagneticHeading_Text)  # Placeholder for magnetic heading
MagneticHeading.pack(pady=5)  # Add some vertical padding to the magnetic heading

Accelerometer = tk.Label(root, textvariable=Accelerometer_Text)  # Placeholder for accelerometer data
Accelerometer.pack(pady=5)  # Add some vertical padding to the accelerometer data

MotorAzimuth = tk.Label(root, textvariable=Motor_Azimuth)  # Placeholder for motor angles
MotorAzimuth.pack(pady=5)  # Add some vertical padding to the motor angles
MotorElevation = tk.Label(root, textvariable=Motor_Elevation)  # Placeholder for motor angles
MotorElevation.pack(pady=5)  # Add some vertical padding to the motor angles

GPredictOpen = tk.Button(root, text="Open Gpredict", command=OpenGpredict) # 'command' links to a function
GPredictOpen.pack(side=tk.LEFT, pady=5)  # Add some vertical padding to the button

MaidenHeadOpen = tk.Button(root, text="Open Maidenhead UI", command=OpenMaidenHead) # 'command' links to a function
MaidenHeadOpen.pack(side=tk.RIGHT, pady=5)  # Add some vertical padding to the button

OpenDiagnostics = tk.Button(root, text="Open Diagnostics", command=OpenDiagnostics) # Placeholder for actual diagnostics opening code
OpenDiagnostics.pack(side=tk.BOTTOM, pady=5)  # Add some vertical padding to the button

UpdateClock = tk.Button(root, text="Update RPi Clock", command=setClockUTC) 
UpdateClock.pack(side=tk.BOTTOM, pady=30)  # Add some vertical padding to the button

UpdateAllData()  # Start the periodic data update loop
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
servo.Start()
MotorPairMove(0,90)
root.mainloop() # Run everything
