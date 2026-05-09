import socket
import time

gp_ip = 'localhost'
gp_port = 4533                  #Standard rotator TCP port
global rotor_pos
rotor_pos=b'123.45\n67.89\n'    #Current (simulated) rotor position


#start function
print('\nWaiting for gpredict command to engage your rotor...')

gp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gp.bind((gp_ip, gp_port))
gp.listen(1)
conn, addr = gp.accept()
global gp_connected
gp_connected = True
print('\nConnection address:', addr)


def openPort():
    global gp_connected
    global rotor_pos
    while gp_connected:
        if not conn._closed:
            packet = conn.recv(30)
        print('\ngpredict command received:', packet)
        if packet==b'q\n':      #gpredict is closing the connection
            #conn.close()
            print('Connection terminated by Gpredict...')
            #gp.close()
            gp_connected=False
            
        elif packet==b'p\n':    #gpredict requesting rotor position
            conn.send(rotor_pos)#fake rotor position back to gpredict
            print('response to "get_pos" command sent:', rotor_pos)
        elif packet[0:2]==b'P ':#gpredict setting rotor position
            mstr=b'RPRT 0\n'    #fake "no error' back to gpredict    
            conn.send(mstr)
            print('response to "set_pos" command sent:', mstr)
            rotor_pos = packet[2:].replace(b" ", b"\n")
            print(rotor_pos.decode('utf-8'))
        else:
            print('Other command', packet)
            mstr=b'\n'          # fake ack back to gpredict    
            conn.send(mstr)
            print('response sent:', mstr)
        
#     exit()
openPort()

# import socket
# import time
# 
# gp_ip = 'localhost'
# gp_port = 4533                  #Standard rotator TCP port
# rotor_pos=b'123.45\n67.89\n'    #Current (simulated) rotor position
# 
# def connectToGP():
#     print('\nWaiting for gpredict command to engage your rotor...')
#     gp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     gp.bind((gp_ip, gp_port))
#     gp.listen(1)
#     conn, addr = gp.accept()
#     gp_connected=True
#     print('\nConnection address:', addr)
# 
#     while gp_connected:
#         if not conn._closed:
#             packet = conn.recv(30)
#         print('\ngpredict command received:', packet)
#         if packet==b'q\n':      #gpredict is closing the connection
#             conn.close()
#             print('Connection terminated by Gpredict...')
#             gp.close()
#             gp_connected=False
#         elif packet==b'p\n':    #gpredict requesting rotor position
#             conn.send(rotor_pos)#fake rotor position back to gpredict
#             print('response to "get_pos" command sent:', rotor_pos)
#         elif packet[0:2]==b'P ':#gpredict setting rotor position
#             mstr=b'RPRT 0\n'    #fake "no error' back to gpredict    
#             conn.send(mstr)
#             print('response to "set_pos" command sent:', mstr)    
#         else:
#             print('Other command', packet)
#             mstr=b'\n'          # fake ack back to gpredict    
#             conn.send(mstr)
#             print('response sent:', mstr)
#         time.sleep(1)
#     exit()
