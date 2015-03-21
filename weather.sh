#!/bin/bash

# download latest METAR conditions - to be run by cron every x:10

curl -s http://weather.noaa.gov/pub/data/observations/metar/decoded/KJLN.TXT > /home/pi/x10/current.txt

