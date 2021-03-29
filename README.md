# Simple VOIP

A simple python VOIP program. Streams sounds data using the UDP protocol. 
This program could be used P2P between two clients, or using a server and multiple clients.

## Requisites
* Python 3
* sounddevice
* pickle

## Usage

### P2P
`python client_voip_UDP.py [your IP] [your port] [peer IP] [peer port]`

### Client-Server

#### Client
`python client_voip_UDP.py [your IP] [your port] [server IP] [server port]`
#### Server
`python server_voip_UDP.py [your server IP] [your server port]`