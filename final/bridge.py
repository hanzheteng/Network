#!/usr/bin/env python
# CS164 Final Project by Hanzhe Teng on 3/15/2018
# Spanning Tree Protocol

import socket
import sys
import time
import commands
import thread

# initialize some global variables
HOSTNUM = 0
HOST = ''
PORT1 = 8001
PORT2 = 8002
PORT3 = 8003
# get mininet-assiged IP and MAC from command line
IP = commands.getoutput("/sbin/ifconfig | grep inet | sed '2,$d' | awk '{print $2}' | sed 's/^.*addr://g'")
MAC = commands.getoutput("/sbin/ifconfig | grep HWaddr | awk '{print $5}'")
# [root bridge ID, distance to root bridge, my bridge ID]
MYBPDU = ['32768.' + MAC, 0, '32768.' + MAC] # when I were the root
MYROOT = ['32768.' + MAC, 0, '32768.' + MAC] # the root accepted by me
ROOT_PORT = 0

# [my port number, port status, incoming MAC address]
port_status = { PORT1:['DP','00:00:00:00:00:00'], PORT2:['DP','00:00:00:00:00:00'], PORT3:['DP','00:00:00:00:00:00'] }

# [source bridge, destination bridge, destination port]
broadcast_table = [ [1, 2, 8003], [1, 3, 8001], [1, 4, 8002], \
                    [2, 1, 8003], [2, 3, 8002], [2, 4, 8001], \
                    [3, 1, 8001], [3, 2, 8002], [3, 4, 8003], \
                    [4, 1, 8002], [4, 2, 8001], [4, 3, 8003]  ]

# [bridge number, associated IP address]
ip_table = { 1:'10.0.0.1', 2:'10.0.0.2', 3:'10.0.0.3', 4:'10.0.0.4' }


# broadcast thread
def broadcast_bpdu(bpdu_msg):
    # traverse table to find neighbor info and broadcast msg
    for host in broadcast_table:
        if host[0] == HOSTNUM:
            ip = ip_table[host[1]]
            print 'broadcast bpdu to port ' + str(host[2]) + ' host ip ' + ip
            thread.start_new_thread(send_thread, (bpdu_msg, ip, host[2]))


# forward thread
def forward_bpdu(bpdu_msg, incoming_port):
    time.sleep(1)
    bpdu_msg[1] = int(bpdu_msg[1]) + 1
    bpdu_msg[2] = '32768.' + MAC
    # figure out which host is associated with this incoming port
    #for host in broadcast_table:
    #    if host[1] == HOSTNUM and host[2] == incoming_port:
    #        incoming_host = host[0]
    # aviod incoming host and forward to the other two hosts
    for host in broadcast_table:
        if host[0] == HOSTNUM and port_status[host[2]][0] == 'DP':
            ip = ip_table[host[1]]
            print 'forward bpdu to port ' + str(host[2]) + ' host ip ' + ip
            thread.start_new_thread(send_thread, (bpdu_msg, ip, host[2]))

def update_root_port(port):
    # check if there already exists a root port
    global ROOT_PORT
    if ROOT_PORT != 0:
        port_status[ROOT_PORT][0] = 'DP'
    ROOT_PORT = port
    port_status[ROOT_PORT][0] = 'RP'


# send thread
def send_thread(bpdu, ip, port):
    try:
        fw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    try:
        fw.connect((ip, port))
    except socket.error:
        print 'Failed to connect with host'
        sys.exit()

    # convert bpdu list to a string for sending
    msg = 'BPDU ' + bpdu[0] + ' ' + str(bpdu[1]) + ' ' + bpdu[2]

    try:
        fw.sendall(msg)
    except socket.error:
        print 'Failed to send message'
        sys.exit()

    # print 'Sent message to ' + ip + ':' + str(port)

    time.sleep(1)
    fw.sendall('!q')  # disconnect


# Client Thread
def client_thread(conn, addr, myport):
    # always work on incoming msg except receving disconnect msg '!q'
    while True:
        data = conn.recv(1024)
        if data[:5] == 'BPDU ':
            # convert the incoming string to a list with three components
            bpdu = data[5:].split(' ')
            root_ID = bpdu[0]
            hops = int(bpdu[1])
            src_ID = bpdu[2]
            my_root_ID = MYROOT[0]
            my_hops = MYROOT[1]
            my_src_ID = MYROOT[2]
            print 'received bpdu from port ' + str(myport)
            print 'incoming bpdu: root_ID=' + root_ID + ' hops=' + str(hops) + ' src_ID=' + src_ID
            print 'my root bpdu: my_root_ID=' + my_root_ID + ' my_hops=' + str(my_hops) + ' my_src_ID=' + my_src_ID

            # always update mac address first no matter what port status it is
            incoming_mac = bpdu[2].split('.')[1]
            port_status[myport][1] = incoming_mac

            # check incoming bpdu status
            if root_ID < my_root_ID:  # elect the root bridge
                # update my root bridge info
                MYROOT[0] = root_ID
                MYROOT[1] = hops
                MYROOT[2] = src_ID
                update_root_port(myport)
                forward_bpdu(bpdu, myport)
            elif root_ID == my_root_ID:    # consensus on root bridge
                if hops < my_hops:     # update parent bridge
                    MYROOT[1] = hops
                    MYROOT[2] = src_ID
                    update_root_port(myport)
                    forward_bpdu(bpdu, myport)
                elif hops == my_hops:
                    if src_ID < my_src_ID:   # update parent bridge
                        MYROOT[2] = src_ID
                        update_root_port(myport)
                        forward_bpdu(bpdu, myport)
                    elif src_ID > my_src_ID:   # stop to receive msg from other parents
                        port_status[myport][0] = 'BP'
                elif hops == my_hops + 1:  # bridge in the same level (brothers)
                    if src_ID < MYBPDU[2]:
                        port_status[myport][0] = 'BP'

        if data[:-2] == '!q':  # disconnect
            break
        if not data:
            break

    conn.close()
    #print 'Port ' + str(myport) + ' disconnected with ' + addr[0] + ':' + str(addr[1])

# server thread
def server_thread(port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((HOST, port))
    except socket.error, msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    s.listen(10)

    while True:
        conn, addr = s.accept()
        #print 'Port ' + str(port) + ' connected with ' + addr[0] + ':' + str(addr[1])
        thread.start_new_thread(client_thread, (conn,addr,port))

    s.close()


# main thread
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Please assign a host number! (from 1 to 4)'
        sys.exit()

    HOSTNUM = int(sys.argv[1])

    print 'Welcome to host' + str(HOSTNUM)
    print 'IP=' + IP + '  MAC=' + MAC + '  PORTS=' + str(PORT1) + ' ' + str(PORT2) + ' ' + str(PORT3)

    thread.start_new_thread(server_thread, (PORT1,))
    thread.start_new_thread(server_thread, (PORT2,))
    thread.start_new_thread(server_thread, (PORT3,))

    # boardcast once first in order to provide MAC address to its neighbors
    # (because manually run scripts on four nodes need a few seconds)
    print port_status
    time.sleep(10)
    broadcast_bpdu(MYBPDU)

    # update every five seconds
    while True:
        time.sleep(1)
        print port_status
        time.sleep(4)
        # boardcast only if I am the root
        if MYBPDU[0] == MYROOT[0]:
            broadcast_bpdu(MYBPDU)

