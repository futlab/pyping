#!/usr/bin/env python

import socket
from ifaces import enum_if
from threading import Thread
import time

threads = {}

UDP_PORT = 5005


def listen(listen_ip):
    print "Start listen at " + listen_ip + ":" + str(UDP_PORT)
    rxSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rxSock.bind((listen_ip, UDP_PORT))

    txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

    try:
        while True:
            text, (address, port) = rxSock.recvfrom(1024)
            data = text.split(' ')
            print "received:", text, "from", address
            if data[0] == 'ping':
                txSock.sendto("OK " + listen_ip + " " + socket.gethostname(), (address, int(data[1])))
    except Exception:
        print "Exception"
    finally:
        rxSock.close()
        txSock.close()

count = 0
while True:
    ifs = enum_if()

    for if_name in threads:
        if not threads.get(if_name).is_alive():
            threads.update({if_name: None})

    for if_name in ifs:
        if (if_name[0] == 'w' or if_name[0] == 'e') and threads.get(if_name) is None:
            thread = Thread(target=listen, args=(ifs.get(if_name), ))
            threads.update({if_name : thread})
            thread.start()
            count += 1
    if count >= 1:
        time.sleep(30)
    else:
        time.sleep(5)
