#!/bin/bash

# Coordinates (home in joplin)
lat="37.04353N"
lon="94.51663W"

echo "Waiting for sunrise" > /home/pi/x10/status.txt
sunwait sun up $lat $lon
heyu foff j2
echo "J2 off at sunrise, waiting for +3 deg" > /home/pi/x10/status.txt

/usr/local/bin/sunwaitJ2 custom up $lat $lon
/home/pi/x10/wxlights.py

sunwaitJ custom up $lat $lon
/home/pi/x10/wxlights.py

