# CS164 Lab4 by Hanzhe Teng on 2/1/2018
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

#Create a list to store connections
global conn_list
conn_list = []

#Function for handling connections. This will be used to create threads
def clientthread(conn, addr):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:
        #Receiving from client
        data = conn.recv(1024)
        print 'Received from ' + addr[0] + ':' + str(addr[1]) + ' : ' + data[:-2]

        if data[:9] == '!sendall ':
            for con in conn_list:
                con.sendall(data[9:])
        else:
            reply = 'OK...' + data
            conn.sendall(reply)

        if data[:-2] == '!q': 
            break
        if not data: 
            break

    #Close the connection
    conn.close()
    conn_list.remove(conn)
    print 'Disconnected with ' + addr[0] + ':' + str(addr[1])

#now keep talking with the client
while True:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,addr))
    conn_list.append(conn)

 
s.close()
