#!/usr/bin/env python2
# CS164 Lab5 by Hanzhe Teng on 2/8/2018
# Socket Forwarder Python Program

import socket
import sys
import time
from thread import *

HOST = ''   
PORT = 8888 

global forward_list
forward_list = []

# Forwarder thread
def forward_thread(fwhost, fwport, fwmsg, srcip, srcport):

    try:
        fw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    try:
        fwip = socket.gethostbyname(fwhost)
    except socket.gaierror:
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

    fw.connect((fwip, fwport))
 
    try:
        fw.sendall(fwmsg)
    except socket.error:
        print 'Send failed'
        sys.exit()
    print 'Forwarded message: ' + fwmsg

    forward_list.append((srcip+':'+str(srcport), fwip+':'+str(fwport), fwmsg))

    time.sleep(1)
    fw.sendall('!q')

# Client Thread
def client_thread(conn, addr):

    conn.send('Welcome to the forwarder.\nType "!fw hostname portnum msg" to forward a msg.\n ') 

    while True:
        data = conn.recv(1024)
        print 'Received from ' + addr[0] + ':' + str(addr[1]) + ' : ' + data[:-2]

        if data[:4] == '!fw ':
            fwinfo = data[4:].split(' ')
            fwhost = fwinfo[0]
            fwport = int(fwinfo[1])
            fwmsg = fwinfo[2][:-2]
            start_new_thread(forward_thread, (fwhost,fwport,fwmsg,addr[0],addr[1]))
            reply = 'OK... Forwarded: ' + fwmsg + '\n'
            conn.sendall(reply)
        elif data[:7] == '!report':
            print forward_list
        else:
            reply = 'OK... Received: ' + data
            conn.sendall(reply)

        if data[:-2] == '!q': 
            break
        if not data: 
            break

    conn.close()
    conn_list.remove(conn)
    print 'Disconnected with ' + addr[0] + ':' + str(addr[1])

# main thread
if __name__ == '__main__':

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((HOST, PORT))
    except socket.error, msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    s.listen(10)
    print 'Welcome to forwarder!'

    while True:
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        start_new_thread(client_thread, (conn,addr))

    s.close()


