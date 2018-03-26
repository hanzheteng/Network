#!/usr/bin/env python
# CS164 Lab7 by Hanzhe Teng on 2/22/2018
# ARP Python Program

import socket
import sys
import time
from thread import *

HOST = ''   
PORT = 8003
IP = '10.0.100.5'
MAC = '00:24:1d:5c:5b:dc' 

global arp_table
arp_table = {}
global broadcast_table
broadcast_table = [ [8000,'10.0.100.1','00:00:00:00:00:00'],[8001,'10.0.100.1','00:00:00:00:00:00'], [8002,'10.0.100.1','00:00:00:00:00:00'] ]

# arp thread
def arp_thread(arp_info, des_ip):
    try:
        fw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    try:
        fwip = socket.gethostbyname('localhost')
    except socket.gaierror:
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

    fw.connect((fwip, arp_info[0]))
    fwmsg = '!arp ' + str(arp_info[0]) + ' ' + des_ip + ' ' + arp_info[2] + ' ' + str(PORT) + ' ' + IP + ' ' + MAC

    try:
        fw.sendall(fwmsg)
    except socket.error:
        print 'ARP request failed.'
        sys.exit()
    print 'sent ARP request to ' + str(arp_info[0])

    reply = fw.recv(4096)
    print 'got ARP reply ' + reply
    arp_info = reply[:-2].split(' ')
    if arp_info[1] not in arp_table:
        arp_table[arp_info[1]] = [int(arp_info[0]),arp_info[1],arp_info[2]]

    time.sleep(1)
    fw.sendall('!q')


# Client Thread
def client_thread(conn, addr):

    while True:
        data = conn.recv(1024)

        if data[:8] == 'pingmac ':
            ip = data[8:-2]
            if ip in arp_table:
                start_new_thread(arp_thread, (arp_table[ip],ip) )
            else:
                start_new_thread(arp_thread, (broadcast_table[0],ip) )
                start_new_thread(arp_thread, (broadcast_table[1],ip) )
                start_new_thread(arp_thread, (broadcast_table[2],ip) )

        elif data[:5] == '!arp ':
            arp_msg = data[5:-2].split(' ')
            if arp_msg[4] not in arp_table:
                arp_table[arp_msg[4]] = [int(arp_msg[3]),arp_msg[4],arp_msg[5]]
            if arp_msg[1] == IP:
                print 'Received ARP from ' + arp_msg[4] + ' ... replying'
                reply_msg = str(PORT) + ' ' + IP + ' ' + MAC
                conn.sendall(reply_msg)
            else:
                print 'Received ARP from ' + arp_msg[4] + ' ... ignoring'

        elif data[:6] == 'arp -a':
            print arp_table

        if data[:-2] == '!q': 
            break
        if not data: 
            break

    conn.close()

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
    print 'Welcome to node D!'

    while True:
        conn, addr = s.accept()
        #print 'Connected with ' + addr[0] + ':' + str(addr[1])
        start_new_thread(client_thread, (conn,addr))

    s.close()


