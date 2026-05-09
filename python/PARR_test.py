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
import ADC_readPot as Pot
import threading as tr


### Port setup

gp_ip = 'localhost'
gp_port = 4533                  #Standard rotator TCP port
global rotor_pos
rotor_pos=b'123.45\n67.89\n'    #Current (simulated) rotor position


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

def OpenGpredict():
    GPredictProcess = subprocess.Popen(['gpredict']) 
    print("Gpredict would open here!")  # Placeholder for actual Gpredict opening code
    #start function
    print('\nWaiting for gpredict command to engage your rotor...')

    ### Setup for ports and stuff since this really sucks holy moly I love CODE!!!
    
    SetupSerial()
    ReadSerial()
        
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
        ConvertedAzimuth = float(Azimuth) - 180
        AngleChange = abs(ConvertedAzimuth - CurrentAngle)
        GoodSpeed1 = 50000*min(1,AngleChange/300)
        print("AngleChange and GoodSpeed1 - ",AngleChange, GoodSpeed1)
        
        MotorPairMove(ConvertedAzimuth,Elevation,GoodSpeed1)

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

def UpdateGPSData(TimesChecked=0):
    GPS_Text.set("GPS Data: " + f" (Checked {TimesChecked} times)")  # This would be replaced with actual GPS data retrieval and formatting

def UpdateMagneticHeading(TimesChecked=0):
    MagneticHeading_Text.set("Magnetic Heading: " + f" (Checked {TimesChecked} times)")  # This would be replaced with actual magnetic heading retrieval and formatting

def UpdateAccelerometerData(TimesChecked=0):  
    Accelerometer_Text.set("Accelerometer Data: " + f" (Checked {TimesChecked} times)")  # This would be replaced with actual accelerometer data retrieval and formatting

def CheckMotorAngles(TimesChecked=0):
    Motor_Azimuth.set("Azimuth: " + f" (Checked {TimesChecked} times)")  # This would be replaced with actual motor angle checking and formatting
    Motor_Elevation.set("Elevation: " + f" (Checked {TimesChecked} times)")  # This would be replaced with actual motor elevation checking and formatting

def CheckGpredictStatus(): # Check if gpredict is open or not!!!
        try:
            subprocess.check_output(["pgrep", 'gpredict'])
            print("Gpredict is running")
            return True
        except subprocess.CalledProcessError:
            return False

def DebugMotorAngles():
    MotorDebug = tk.Toplevel(root)
    MotorDebug.title("Motor Debug")
    MotorDebug.geometry("300x200") # Set the size of the new window
    
    tk.Scale(MotorDebug, from_=0, to=180, orient='horizontal',command=stepper.set).pack(pady=20)
    tk.Scale(MotorDebug, from_=0, to=180, orient='vertical',command=servo.move).pack(pady=20)
    ManualStepperAngle = tk.Entry(MotorDebug)
    ManualStepperAngle.pack(pady=20)
    ManualServoAngle = tk.Entry(MotorDebug)
    ManualServoAngle.pack(pady=20)
    tk.Button(MotorDebug, text="Move", command=lambda: stepper.move(float(ManualStepperAngle.get()))).pack(pady=5)
    tk.Button(MotorDebug, text="Set", command=lambda: MotorPairMove((float(ManualStepperAngle.get())), (float(ManualServoAngle.get())))).pack(pady=5)
    tk.Button(MotorDebug, text="Stop", command=lambda: stepper.set(0)).pack(pady=5)
    tk.Button(MotorDebug, text="Update Angle", command=StepperAngleCheck).pack(pady=5)
    tk.Button(MotorDebug, text="Update Right Max", command=UpdateRightMax).pack(pady=5)
    tk.Button(MotorDebug, text="Update Left Max", command=UpdateLeftMax).pack(pady=5)
    tk.Button(MotorDebug, text="Preset Test", command=TestPath).pack(pady=5)
    
def UpdateRightMax():
    global PotentiometerRightMax
    PotentiometerRightMax = Pot.ReadPot()[2]
    print(PotentiometerRightMax)
    
def UpdateLeftMax():
    global PotentiometerLeftMax
    PotentiometerLeftMax = Pot.ReadPot()[2]
    print(PotentiometerLeftMax)
    
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
    print("Azimuth Set To-", AzimuthSet, "Elevation Set To -", ElevationSet)
    Azimuth = tr.Thread(target=stepper.set(AzimuthSet, speed))
    Elevation = tr.Thread(target=servo.move(ElevationSet))
    Azimuth.start()
    Elevation.start()
    Azimuth.join()
    Elevation.join()

def TestPath():
    MotorPairMove(0,0)
    # Azimuth
    MotorPairMove(-180,0, 10000)
    MotorPairMove(180,0, 20000)
    # Elevation
    MotorPairMove(0,0)
    MotorPairMove(0,180)
    # Azimuth & Elevation
    MotorPairMove(-180,0, 10000)
    MotorPairMove(180,180, 20000)
    # Restart
    MotorPairMove(0,0)

def UpdateAllData(N):
    UpdateGPSData(N)
    UpdateMagneticHeading(N)
    UpdateAccelerometerData(N)
    CheckMotorAngles(N)
    CheckCounter = N + 1  # Update the global counter with the current value
    root.after(1000, UpdateAllData, N+1)  # Schedule the next update after 1000 milliseconds (1 second)

def OpenDiagnostics():
    # Create a new Toplevel window
    Diagnostics = tk.Toplevel(root)
    Diagnostics.title("New Window")
    Diagnostics.geometry("300x200") # Set the size of the new window

    # Add a label to the new window
    tk.Label(Diagnostics, text="Diagnostics Window").pack(side=tk.TOP, pady=5)
    tk.Label(Diagnostics, text=GPS_Text).pack(pady=0)
    tk.Label(Diagnostics, text=MagneticHeading_Text).pack(pady=0)
    tk.Label(Diagnostics, text=Accelerometer_Text).pack(pady=0)
    tk.Label(Diagnostics, text=Motor_Azimuth).pack(pady=0)
    tk.Label(Diagnostics, text=Motor_Elevation).pack(pady=0)

    # Optional: add a button to close the new window
    tk.Button(Diagnostics, text="GPS", command=UpdateGPSData).pack(side=tk.RIGHT, pady=5) 
    tk.Button(Diagnostics, text="Mag", command=UpdateMagneticHeading).pack(side=tk.RIGHT, pady=5)
    tk.Button(Diagnostics, text="Acc", command=UpdateAccelerometerData).pack(side=tk.RIGHT, pady=5)
    tk.Button(Diagnostics, text="Debug Motor Angles", command=DebugMotorAngles).pack(side=tk.RIGHT, pady=5)
    tk.Button(Diagnostics, text="Close", command=Diagnostics.destroy).pack(side=tk.BOTTOM, pady=5)  # Button to close the diagnostics window


root = tk.Tk()
root.title("Portable Antenna Rotator Router")
root.geometry("400x300")  # Set the window size

GPS_Text = tk.StringVar()
GPS_Text.set("GPS Data: LOADING...")  # Placeholder for GPS data

MagneticHeading_Text = tk.StringVar()
MagneticHeading_Text.set("Magnetic Heading: LOADING...")  # Placeholder for magnetic heading

Accelerometer_Text = tk.StringVar()
Accelerometer_Text.set("Accelerometer Data: LOADING...")  # Placeholder for accelerometer data

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

GPredictOpen = tk.Button(root, text="Update & Open Gpredict", command=OpenGpredict) # 'command' links to a function
GPredictOpen.pack(side=tk.LEFT, pady=5)  # Add some vertical padding to the button

MaidenHeadOpen = tk.Button(root, text="Open Maidenhead UI", command=OpenMaidenHead) # 'command' links to a function
MaidenHeadOpen.pack(side=tk.RIGHT, pady=5)  # Add some vertical padding to the button

OpenDiagnostics = tk.Button(root, text="Open Diagnostics", command=OpenDiagnostics) # Placeholder for actual diagnostics opening code
OpenDiagnostics.pack(side=tk.BOTTOM, pady=5)  # Add some vertical padding to the button

CheckCounter = 0  # Initialize the counter for data updates
UpdateAllData(CheckCounter)  # Start the periodic data update loop
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
StepperAngleCheck()
MotorPairMove(0,0)
root.mainloop() # Run everything
