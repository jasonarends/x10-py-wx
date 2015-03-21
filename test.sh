#!/bin/bash

if grep -c -i -F --file=/home/pi/x10/light.txt /home/pi/x10/current.txt; then
	echo "light"
elif grep -c -i -F --file=/home/pi/x10/dark.txt /home/pi/x10/current.txt; then
	echo "dark"
elif grep -c -i -F --file=/home/pi/x10/darkest.txt /home/pi/x10/current.txt; then
	echo "darkest"
fi
