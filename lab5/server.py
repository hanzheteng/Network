#!/usr/bin/env python2
# CS164 Lab5 by Hanzhe Teng on 2/8/2018
# Socket Server Python Program

import socket
import sys
from thread import *

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 3093 # Arbitrary non-privileged port

#Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
print 'Socket bind complete'

#Start listening on socket
s.listen(10)
print 'Socket now listening'

#Function for handling connections. This will be used to create threads
def clientthread(conn, addr):
    while True:
        data = conn.recv(1024)
        if data == '!q': 
            break
        else:
            print 'Received from ' + addr[0] + ':' + str(addr[1]) + ' : ' + data
        if not data: 
            break
    conn.close()
    #print 'Disconnected with ' + addr[0] + ':' + str(addr[1])

#now keep talking with the client
while True:
    conn, addr = s.accept()
    #print 'Connected with ' + addr[0] + ':' + str(addr[1])

    start_new_thread(clientthread ,(conn,addr))

s.close()


