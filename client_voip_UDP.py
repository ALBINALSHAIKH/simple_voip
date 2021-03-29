#!/usr/bin/python

import sys
import socket
from _thread import *
import threading
import sounddevice as sd
import pickle

#Initial port and host. Both should be given as arguments.
your_port = -1
your_host = "localhost"
port = -1
host = "localhost"

sendsocket = None
received = [[0.0, 0.0]]

#Thread lock to avoid race conditions
lock = threading.Lock()

#check_arg(): will check for valid argument inputs
def check_arg():
    if len(sys.argv) < 5:
        print("Usage:client.py [your address] [port number] [host address] [port number]")
        return False
    elif len(sys.argv) > 5:
        print("Usage:client.py [your address] [port number] [host address] [port number]")
        return False
    
    global your_port
    global your_host
    global port
    global host
    try:
        port = int(sys.argv[4])
        your_port = int(sys.argv[2])
        if port < 0 or port > 65353 or your_port < 0 or your_port > 65353:
            print("Argument Error: port number out of bounds (0-65353)")
            return False
    except ValueError:
        print("Argument Error: port must be a number")
        return False
    
    your_host = sys.argv[1]
    host = sys.argv[3]
    return True

def callback(indata, outdata, frames, time, status):
    global received
    if status:
        print(status)
    lock.acquire()
    outdata[:] = received
    received = [[0.0, 0.0]]
    lock.release()

    sending = pickle.dumps(indata)
    sendsocket.sendto(sending, (host, port))

#server_send(): handles sending messages to the server
def server_send(ct):
    #Send data to server

    with sd.Stream(channels=2, callback=callback):
        input()

    # while True:
    #     #Wait for user input
    #     fs = 44100
    #     duration = 1
    #     while True:
    #         data = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    #         sd.wait()
    #         sd.play(data, fs)

    #     #Send the data
    #     data = pickle.dumps(data)
    #     insize = str(sys.getsizeof(data)).encode('utf-8')
    #     print(insize.decode())
    #     # ct.send(insize)
    #     ct.sendto(data, (host, port))

#start_client_process: prepares the client socket, connects to the server and creates the sending thread as well as recieving.
def start_client_process():
    #Create the INET streaming socket
    global sendsocket, received
    sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recvsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    recvsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sendsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # recvsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # sendsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    recvsocket.bind((your_host, your_port))
    sendsocket.bind((your_host, your_port+1))

    #Create new thread for sending messages
    start_new_thread(server_send, (recvsocket, ))

    while True:
        #Recieve a byte from server

        data, addr = recvsocket.recvfrom(9274)

        #If data is empty, then the server disconnected.
        if len(data) == 0:
            break
        
        try:
            lock.acquire()
            received = pickle.loads(data, encoding='bytes')
            lock.release()
        except Exception:
            continue
    
    #Close the connection when the loop breaks
    recvsocket.close()
    sendsocket.close()
    print("Disconnected from server.")

    #Exit the client program
    sys.exit(0)


#Check if the port is correct
if check_arg():
    #Start client process for concurrent sending/recieving
    start_client_process()


