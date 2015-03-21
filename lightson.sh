#!/bin/bash

# Coordinates (home in joplin)
lat="37.04353N"
lon="94.51663W"

echo "Waiting to check weather 45 minutes before sunset" > /home/pi/x10/status.txt
sunwaitJ custom down -45 $lat $lon

if grep -c -i -F --file=/home/pi/x10/light.txt /home/pi/x10/current.txt; then
	delay=-1
elif grep -c -i -F --file=/home/pi/x10/dark.txt /home/pi/x10/current.txt; then
	delay=-15
elif grep -c -i -F --file=/home/pi/x10/darkest.txt /home/pi/x10/current.txt; then
	delay=-30
else
	delay=-1
fi
echo "Waiting for sunset $delay" > /home/pi/x10/status.txt

#email the status to yourself

#do the actual waiting
sunwaitJ custom down $delay $lat $lon
heyu fon j4 #turn on lights
echo "J4 ON at J sunset $delay" > /home/pi/x10/status.txt

/usr/local/bin/sunwaitJ2 custom down $lat $lon
heyu fon j5
echo "J5 on at J2 sunset" > /home/pi/x10/status.txt

sunwaitJ sun down $lat $lon
heyu fon j2
echo "J2 on at sunset" > /home/pi/x10/status.txt

#sunwait civ down $lat $lon
#heyu fon j3
