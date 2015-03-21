#!/bin/bash


if grep -c -i -F --file=/home/pi/x10/light.txt /home/pi/x10/current.txt; then
	heyu foff j4,5
elif grep -c -i -F --file=/home/pi/x10/dark.txt /home/pi/x10/current.txt; then
	heyu foff j5; heyu fon j4 
elif grep -c -i -F --file=/home/pi/x10/darkest.txt /home/pi/x10/current.txt; then
	heyu fon j4,5 
fi

