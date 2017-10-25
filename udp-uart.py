import socket
from threading import Thread
from ifaces import choose_ip, enum_if
import argparse
import re
import serial

parser = argparse.ArgumentParser(description='UDP-UART bridge')
parser.add_argument('-l', type=int, default=5006, help='Set listen port')
parser.add_argument('-t', type=str, help='Set target address')
parser.add_argument('-p', type=int, default=5005, help='Set target port')
parser.add_argument('-i', type=str, default='', help='interface or ip address to use')
parser.add_argument('-d', type=str, default='/dev/ttyUSB0', help='serial device')
parser.add_argument('-b', type=int, default=115200, help='serial device baudrate')


args = parser.parse_args()

print "Opening serial device " + args.d + " at baudrate " + str(args.b)

uart = serial.Serial(args.d, args.b, timeout=0.05);

txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

if args.i == '':
    LISTEN_IP = choose_ip()
else:
    ip = re.match('^\d+.\d+.\d+.\d+$', args.i)
    if ip is None:
        LISTEN_IP = enum_if().get(args.i)
        if LISTEN_IP is None:
            print "Unknown interface: " + args.i
            SystemExit()
    else:
        UDP_IP = ip

LISTEN_PORT = args.l
running = True

def listen(listen_ip):
    print "Start listen at " + listen_ip + ":" + str(LISTEN_PORT)
    rxSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rxSock.settimeout(1)
    rxSock.bind((listen_ip, LISTEN_PORT))

    try:
        while running:
            try:
                text, (address, port) = rxSock.recvfrom(1024)
                data = text.split(' ')
                #print "received:", text, "from", address
                if data[0] == 'ping':
                    txSock.sendto("OK " + listen_ip + " " + socket.gethostname(), (address, int(data[1])))
                uart.write(text);
            except socket.timeout:
                pass
    except Exception as e:
        print "Exception:", e
    finally:
        rxSock.close()

def read(uart):
    print "Target is " + args.t + ":" + str(args.p)
    while True:
        data = uart.read(10);
        if (data != ""):
            #print "received from uart:" + data
            txSock.sendto(data, (args.t, args.p))

listenThread = Thread(target=listen, args=(LISTEN_IP, ))
listenThread.start()

try:
    while True:
        read(uart)
except KeyboardInterrupt:
    print "Terminating..."
    running = False
    listenThread.join()
    txSock.close()

