#!/usr/bin/env python

import socket
from ifaces import enum_if
from threading import Thread
import subprocess
import time
from argparse import ArgumentParser

parser = ArgumentParser(description='UDP service-launcher')
parser.add_argument('-p', type=int, default=5007, help='Set listen port')

args = parser.parse_args()

threads = {}

UDP_port = args.p

process_ctr = 1

running = True


def launch(args, ip, port, tx_sock, id):
    try:
        start = "START #" + str(id) + " " + " ".join(args)
        print start + " output to " + ip + ":" + str(port)
        tx_sock.sendto("\n" + start, (ip, port))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout:
            tx_sock.sendto("\n#" + str(id) + " " + line, (ip, port))
        p.stdout.close()
        result = "QUIT #" + str(id)
        print result
        tx_sock.sendto("\n" + result, (ip, port))
    except Exception as e:
        print "Launch exception:", e
        tx_sock.sendto("\nERROR #" + str(id) + " " + str(e), (ip, port))


def listen(listen_ip, udp_port):
    global process_ctr
    print "Start listen at " + listen_ip + ":" + str(udp_port)
    rxSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rxSock.settimeout(1)
    rxSock.bind((listen_ip, udp_port))

    txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

    try:
        while running:
            try:
                text, (address, port) = rxSock.recvfrom(1024)
                data = text.strip().split(' ')
                print "received:", text, "from", address
                if data[0] == 'ping':
                    txSock.sendto("\nOK " + listen_ip + " " + socket.gethostname(), (address, int(data[1])))
                if data[0] == 'launch':
                    args = data[2:]
                    launch_thread = Thread(target=launch, args=(args, address, int(data[1]), txSock, process_ctr))
                    process_ctr += 1
                    launch_thread.start()
            except socket.timeout:
                pass
    except Exception as e:
        print "Exception: ", e
    finally:
        rxSock.close()
        txSock.close()


count = 0
try:
    while True:
        ifs = enum_if()

        for if_name in threads:
            if not threads.get(if_name).is_alive():
                threads.update({if_name: None})

        for if_name in ifs:
            if (if_name[0] == 'w' or if_name[0] == 'e') and threads.get(if_name) is None:
                thread = Thread(target=listen, args=(ifs.get(if_name), UDP_port))
                threads.update({if_name: thread})
                thread.start()
                count += 1
        if count >= 1:
            time.sleep(30)
        else:
            time.sleep(5)
except KeyboardInterrupt:
    print "Terminating..."
    running = False
    for if_name in threads:
        threads[if_name].join()

