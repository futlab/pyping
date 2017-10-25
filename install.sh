#!/bin/bash

mkdir -p /opt/udp-launch
cp udp-launch.py udp-uart.py ifaces.py /opt/udp-launch/
cp udp-launch.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable udp-launch
systemctl start udp-launch
