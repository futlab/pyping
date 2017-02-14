#!/usr/bin/env python

import socket
from ifaces import choose_ip

UDP_IP = choose_ip()
UDP_PORT = 5005

print "listen at " + UDP_IP + ":" + str(UDP_PORT)

rxSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rxSock.bind((UDP_IP, UDP_PORT))

txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

while True:
    text, (address, port) = rxSock.recvfrom(1024)
    data = text.split(' ')
    print "received:", text, "from", address
    if data[0] == 'ping':
        txSock.sendto("OK " + UDP_IP + " " + socket.gethostname(), (address, int(data[1])))

