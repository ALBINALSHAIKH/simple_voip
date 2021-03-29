import sys
import socket
from _thread import *
import threading

#Initial port and host. Both should be given as arguments.
port = -1
host = "localhost"

#An array to keep track of connected clients
client_addresses = []

#check_arg(): will check for valid argument inputs
def check_arg():
    if len(sys.argv) < 3:
        print("Usage:server_voip_UDP.py [host address] [port number]")
        return False
    elif len(sys.argv) > 3:
        print("Usage:server_voip_UDP.py [host address] [port number]")
        return False
    
    global port
    global host
    try:
        port = int(sys.argv[2])
        if port < 0 or port > 65353:
            print("Argument Error: port number out of bounds (0-65353)")
            return False
    except ValueError:
        print("Argument Error: port must be a number")
        return False
    
    host = sys.argv[1]
    return True

#start_server_process: prepares the sockets
def start_client_process():
    #Create the INET streaming socket
    sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recvsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    recvsocket.bind((host, port))

    while True:
        #Recieve 9274 bytes of serialized data.

        data, addr = recvsocket.recvfrom(9274)

        #Fix address
        addr = (addr[0], addr[1] - 1)
        
        #Add address if it does not exist
        if addr not in client_addresses:
            client_addresses.append(addr)
        
        #Spread the data except for the sending client
        for a in client_addresses:
            if a != addr:
                sendsocket.sendto(data, a)
    
    #Close the connection when the loop breaks
    recvsocket.close()
    sendsocket.close()

    #Exit the client program
    sys.exit(0)

#Check arguments
if check_arg():
    #Start client process for concurrent sending/recieving
    start_client_process()


