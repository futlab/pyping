#!/usr/bin/env python

import socket
import threading
from ifaces import choose_ip, enum_if
import argparse
import re

parser = argparse.ArgumentParser(description='Local network UDP spamer')
parser.add_argument('-l', type=int, default=5006, help='Set listen port')
parser.add_argument('-p', type=int, default=5005, help='Set target port')
parser.add_argument('-i', type=str, default='', help='interface or ip address to use')

args = parser.parse_args()

if args.i == '':
    UDP_IP = choose_ip()
else:
    ip = re.match('^\d+.\d+.\d+.\d+$', args.i)
    if ip is None:
        UDP_IP = enum_if().get(args.i)
        if UDP_IP is None:
            print "Unknown interface: " + args.i
            SystemExit()
    else:
        UDP_IP = ip

UDP_PORT = args.p
UDP_LISTEN_PORT = args.l
MESSAGE = "ping " + str(UDP_LISTEN_PORT)


def receive():
    print "listen at " + UDP_IP + ":" + str(UDP_LISTEN_PORT)
    rxSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rxSock.bind((UDP_IP, UDP_LISTEN_PORT))
    rxSock.settimeout(2)
    try:
        while True:
            data, (address, port) = rxSock.recvfrom(1024)
            print "received:", data, "from", address
    except socket.timeout:
        rxSock.close()

UDP_IP_CONST = re.match('^(\d+.\d+.\d+.)\d+$', UDP_IP).group(1)

print "UDP target IPs:", UDP_IP_CONST + '*'
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

receiver = threading.Thread(target=receive)
receiver.start()

txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
#txSock.setsockopt(socket.IPPROTO_IP, socket.SO_ , 5)
txSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
txSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
for a in range(1, 254):
    txSock.sendto(MESSAGE, ("10.30.38." + str(a), UDP_PORT))
#    print('.')

receiver.join()
