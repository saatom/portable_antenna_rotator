import ADS1x15
import time
import RPi.GPIO as GPIO
import threading as tr

ADC = ADS1x15.ADS1115(1, 0x48)
ADC.setDataRate(7)

#ADC.setMode(ADC.MODE_CONTINUOUS)
ADC.setMode(1) #single shot mode
ADC.setGain(0)

def ReadVolt():
    #ADC.request
    V0_raw = ADC.readADC(0)
    V1_raw = ADC.readADC(1)
    V2_raw = ADC.readADC(2)
    V3_raw = ADC.readADC(3)

    V0 = ADC.toVoltage(V0_raw)
    V1 = ADC.toVoltage(V1_raw)
    V2 = ADC.toVoltage(V2_raw)
    V3 = ADC.toVoltage(V3_raw)

    #print(V0, V1, V2, V3)
    #print(ADC.getDataRate())
    
    #Vdd_Vg_raw = ADC.readADC_Differential_1_3()
    #Vwiper_Vg_raw = ADC.readADC_Differential_2_3()
    
    #Vdd_Vg = ADC.toVoltage(Vdd_Vg_raw)
    #Vwiper_Vg = ADC.toVoltage(Vwiper_Vg_raw)
    #print("Vdd to ground:",-1*Vdd_Vg,"\nWiper to ground:",-1*Vwiper_Vg,"\n")
    
    return V0, V1, V2, V3

def AveVolt(Average):
    V = 0, 0, 0, 0
    V0Ave, V1Ave, V2Ave, V3Ave = 0, 0, 0, 0
    
    for n in range(Average):
        V = ReadVolt()
        V0Ave = V0Ave + V[0]/Average
        V1Ave = V1Ave + V[1]/Average
        V2Ave = V2Ave + V[2]/Average
        V3Ave = V3Ave + V[3]/Average
        time.sleep(0.3)
    
    return V0Ave, V1Ave, V2Ave, V3Ave

def IsEnabled():
    try:
        t1 = ReadVolt()
        print("Volt | Working")
        return True
    except:
        print("Volt | Nope, doesn't work")
        return False

# IsEnabled()
a, b, c, d = ReadVolt()
print(a,b,c,d)