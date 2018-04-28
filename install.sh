#!/bin/bash

pip2 install pexpect

mkdir -p /opt/udp-launch
cp udp-launch.py udp-uart.py ifaces.py /opt/udp-launch/
# cp udp-launch.service /etc/systemd/system/
sed "s/<user>/odroid/g" udp-launch.service > /etc/systemd/system/udp-launch.service

systemctl daemon-reload
systemctl enable udp-launch
systemctl start udp-launch
