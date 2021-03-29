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

#Global variables to keep track of the send socket and the recevied sound data
sendsocket = None
received = [[0.0, 0.0]]

#Thread lock to avoid race conditions
lock = threading.Lock()

#check_arg(): will check for valid argument inputs
def check_arg():
    if len(sys.argv) < 5:
        print("Usage:client_voip_UDP.py [your address] [port number] [host address] [port number]")
        return False
    elif len(sys.argv) > 5:
        print("Usage:client_voip_UDP.py [your address] [port number] [host address] [port number]")
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

#callback(): the callback function for the real-time sound streaming
def callback(indata, outdata, frames, time, status):
    global received
    if status:
        print(status)

    #Aquire a thread lock to prevent a race condition with "received"
    lock.acquire()

    #Assign sound output data
    outdata[:] = received

    #Reset received data to null
    received = [[0.0, 0.0]]

    lock.release()

    #Serialize the data and send to receiving host
    sending = pickle.dumps(indata)
    sendsocket.sendto(sending, (host, port))

#send(): handles sending sound data over UDP
def send():
    # Start streaming sound. Play received sound, record and send sound.
    with sd.Stream(channels=2, callback=callback):
        input()

#start_client_process: prepares the sockets, and the send/receive threads.
def start_client_process():
    #Create the INET streaming sockets
    global sendsocket, received
    sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recvsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    recvsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sendsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    recvsocket.bind((your_host, your_port))
    sendsocket.bind((your_host, your_port+1))

    #Create new thread for sending messages
    start_new_thread(send, ())

    while True:
        #Recieve 9274 bytes of serialized data.

        data, addr = recvsocket.recvfrom(9274)
        
        try:
            #Aquire thread lock to prevent race conditons.
            lock.acquire()

            #Unpack serialized data
            received = pickle.loads(data, encoding='bytes')

            lock.release()
        except Exception:
            continue
    
    #Close the connection when the loop breaks
    recvsocket.close()
    sendsocket.close()

    #Exit the client program
    sys.exit(0)

#Check arguments
if check_arg():
    #Start client process for concurrent sending/recieving
    start_client_process()


