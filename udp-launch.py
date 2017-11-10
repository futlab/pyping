#!/usr/bin/env python

import socket
from ifaces import enum_if
from threading import Thread
import subprocess
import time
from argparse import ArgumentParser
from os import listdir
from os.path import isfile, join

parser = ArgumentParser(description='UDP service-launcher')
parser.add_argument('-p', type=int, default=5007, help='Set listen port')
parser.add_argument('-d', type=str, default='/home/igor/launch/', help='Directory with .launch files')

args = parser.parse_args()

listen_threads = {}
launch_threads = {}

UDP_port = args.p
launchDir = args.d

running = True


def task_list():
    return "\n".join(map(lambda k: k + " " + " ".join(launch_threads[k]['args']), launch_threads.keys()))


def launch(args, ip, port, id):
    tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        start = "START " + id + " " + " ".join(args)
        print start + " output to " + ip + ":" + str(port)
        tx_sock.sendto("\n" + start, (ip, port))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=launchDir)
        launch_threads[id].update({'popen': p})
        for line in p.stdout:
            tx_sock.sendto("\n" + id + " " + line, (ip, port))
        p.stdout.close()
        p.wait()
        result = "QUIT " + id + " " + str(p.returncode)
        print result
        tx_sock.sendto("\n" + result, (ip, port))
    except Exception as e:
        print "Launch exception:", e
        tx_sock.sendto("\nERROR " + id + " " + str(e), (ip, port))
    finally:
        tx_sock.close()
        launch_threads.pop(id, None)


def listen(listen_ip, udp_port):
    rxSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    try:
        print "Start listen at " + listen_ip + ":" + str(udp_port)
        rxSock.settimeout(1)
        rxSock.bind((listen_ip, udp_port))

        while running:
            try:
                text, (address, port) = rxSock.recvfrom(1024)
                print "received:", text, "from", address
                data = text.strip().split(' ')
                cmd = data[0]
                tx_port = int(data[1])

                def answer(msg):
                    txSock.sendto(msg, (address, tx_port))
                try:
                    if cmd == 'ping':
                        answer("\nOK " + listen_ip + " " + socket.gethostname())
                    elif cmd == 'list':
                        files = [f for f in listdir(launchDir) if f.endswith('.launch') and isfile(join(launchDir, f))]
                        answer("\nLIST " + " ".join(files))
                    elif cmd == 'launch':
                        args = data[3:]
                        id = data[2]
                        launch_thread = Thread(target=launch, args=(args, address, tx_port, id))
                        launch_threads.update({id: { 'thread': launch_thread, 'args': args}})
                        launch_thread.start()
                    elif cmd == 'roslaunch':
                        args = ['roslaunch', launchDir + data[3]] + data[4:]
                        id = data[2]
                        launch_thread = Thread(target=launch, args=(args, address, tx_port, id))
                        launch_threads.update({id: { 'thread': launch_thread, 'args': args}})
                        launch_thread.start()
                    elif cmd == 'stop':
                        id = data[2]
                        lt = launch_threads.get(id)
                        if lt is None:
                            answer("\nSTOP " + id + " NF")
                        else:
                            lt['popen'].send_signal(subprocess.signal.SIGINT)
                            answer("\nSTOP " + id + " OK")
                    elif cmd == 'kill':
                        id = data[2]
                        lt = launch_threads.get(id)
                        if lt is None:
                            answer("\nKILL " + id + " NF")
                        else:
                            lt['popen'].kill()
                            answer("\nKILL " + id + " OK")
                    if cmd == 'tasks':
                        answer("\nTASKS " + task_list())
                except Exception as e:
                    print "Process exception: ", e
                    answer("\nEXCEPTION " + cmd + " " + str(e))
            except socket.timeout:
                pass
    except Exception as e:
        print "Loop exception: ", e
    finally:
        rxSock.close()
        txSock.close()


count = 0
try:
    while True:
        ifs = enum_if()

        for if_name in listen_threads: # remove dead
            if not listen_threads.get(if_name).is_alive():
                listen_threads.update({if_name: None})

        for if_name in ifs:
            ip = ifs.get(if_name)
            if (if_name[0] == 'w' or if_name[0] == 'e') and listen_threads.get(ip) is None:
                thread = Thread(target=listen, args=(ip, UDP_port))
                listen_threads.update({ip: thread})
                thread.start()
                count += 1
        if count >= 1:
            time.sleep(30)
        else:
            time.sleep(5)
except KeyboardInterrupt:
    print "Terminating..."
    running = False
    for if_name in listen_threads:
        listen_threads[if_name].join()

