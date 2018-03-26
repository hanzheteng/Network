# CS164 Lab4 by Hanzhe Teng on 2/1/2018
# Socket Client Python Program
import socket
import sys

hostname = 'scratch.mit.edu'
port = 80

#Create an INET, STREAMing socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()
print 'Socket created'

#Resolve the hostname
try:
    hostip = socket.gethostbyname(hostname)
except socket.gaierror:
    print 'Hostname could not be resolved. Exiting'
    sys.exit()

#Connect to the remote server
s.connect((hostip, port))
print 'Socket connected to ' + hostname + ' on ip ' + hostip
 
#Send some data to remote server
message = "GET / HTTP/1.1\r\nHost: scratch.mit.edu\r\nConnection: close\r\n\r\n"
try :
    #Set the whole string
    s.sendall(message)
except socket.error:
    #Send failed
    print 'Send failed'
    sys.exit()
print 'Message send successfully'
 
#Now receive data
reply = s.recv(4096)
print reply

