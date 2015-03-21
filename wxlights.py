#!/usr/bin/python

import os, sys
import json

def getwug():
    # get conditions last reported (cron job updates this) and return formatted list
    while True:

        try:
            data_file = open('/home/pi/x10/wug.txt')
            data = json.load(data_file)
            data_file.close()
            break

        except ValueError:
            pass

        time.sleep(2)

    return data
    
def formatwug():

    data = getwug()
 
    returnvalue=data["current_observation"]["weather"]

    return returnvalue

conditions = formatwug()

bright = ["Clear","Scattered Clouds","Patches of Fog","Shallow Fog","Light Snow Blowing Snow Mist","Low Drifting Sand","Light Low Drifting Sand","Low Drifting Snow","Light Low Drifting Snow","Dust Whirls","Light Dust Whirls","Light Spray","Spray","Light Haze","Sand","Light Sand","Light Fog Patches","Fog Patches"]
dim = ["Unknown","Unknown Precipitation","Partly Cloudy","Partial Fog","Light Freezing Fog","Freezing Fog","Light Freezing Rain","Light Freezing Drizzle","Snow Blowing Snow Mist","Light Rain Showers","Light Rain Mist","Light Blowing Sand","Light Blowing Snow","Low Drifting Widespread Dust","Light Low Drifting Widespread Dust","Haze","Light Widespread Dust","Light Smoke","Light Fog","Light Mist","Light Snow","Light Rain","Light Drizzle"]
dark = ["Heavy Drizzle","Drizzle","Heavy Rain","Rain","Heavy Snow","Snow","Light Snow Grains","Heavy Snow Grains","Snow Grains","Light Ice Crystals","Heavy Ice Crystals","Ice Crystals","Light Ice Pellets","Heavy Ice Pellets","Ice Pellets","Light Hail","Heavy Hail","Hail","Heavy Mist","Mist","Heavy Fog","Fog","Heavy Fog Patches","Heavy Smoke","Smoke","Light Volcanic Ash","Heavy Volcanic Ash","Volcanic Ash","Heavy Widespread Dust","Widespread Dust","Heavy Sand","Heavy Haze","Heavy Spray","Heavy Dust Whirls","Light Sandstorm","Heavy Sandstorm","Sandstorm","Heavy Low Drifting Snow","Heavy Low Drifting Widespread Dust","Heavy Low Drifting Sand","Heavy Blowing Snow","Blowing Snow","Light Blowing Widespread Dust","Heavy Blowing Widespread Dust","Blowing Widespread Dust","Heavy Blowing Sand","Blowing Sand","Heavy Rain Mist","Rain Mist","Heavy Rain Showers","Rain Showers","Light Snow Showers","Heavy Snow Showers","Snow Showers","Heavy Snow Blowing Snow Mist","Light Ice Pellet Showers","Heavy Ice Pellet Showers","Ice Pellet Showers","Light Hail Showers","Heavy Hail Showers","Hail Showers","Light Small Hail Showers","Heavy Small Hail Showers","Small Hail Showers","Light Thunderstorm","Heavy Thunderstorm","Thunderstorm","Light Thunderstorms and Rain","Heavy Thunderstorms and Rain","Thunderstorms and Rain","Light Thunderstorms and Snow","Heavy Thunderstorms and Snow","Thunderstorms and Snow","Light Thunderstorms and Ice Pellets","Heavy Thunderstorms and Ice Pellets","Thunderstorms and Ice Pellets","Light Thunderstorms with Hail","Heavy Thunderstorms with Hail","Thunderstorms with Hail","Light Thunderstorms with Small Hail","Heavy Thunderstorms with Small Hail","Thunderstorms with Small Hail","Heavy Freezing Drizzle","Freezing Drizzle","Heavy Freezing Rain","Freezing Rain","Heavy Freezing Fog","Overcast","Mostly Cloudy","Small Hail","Squalls","Funnel Cloud"]

if bright.count(conditions):
    print conditions + " = bright"
    os.system('/home/pi/x10/pheyu.py j4,off j5,off')
elif dim.count(conditions):
    print conditions + " = dim"
    os.system('/home/pi/x10/pheyu.py j4,on j5,off')
elif dark.count(conditions):
    print conditions + " = dark"
    os.system('/home/pi/x10/pheyu.py j4,on j5,on')
else:
    print conditions + " (unknown)"
    os.system('/home/pi/x10/pheyu.py j4,on j5,off')
    
