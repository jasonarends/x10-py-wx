#!/usr/bin/python

import os, sys
import json
import sqlite3

db = sqlite3.connect('/home/pi/database.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

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
    
def currentcond():
    conditions = formatwug()

    bright = ["Clear","Scattered Clouds","Patches of Fog","Shallow Fog","Light Snow Blowing Snow Mist","Low Drifting Sand","Light Low Drifting Sand","Low Drifting Snow","Light Low Drifting Snow","Dust Whirls","Light Dust Whirls","Light Spray","Spray","Light Haze","Sand","Light Sand","Light Fog Patches","Fog Patches"]
    
    dim = ["Unknown","Unknown Precipitation","Partly Cloudy","Partial Fog","Light Freezing Fog","Freezing Fog","Light Freezing Rain","Light Freezing Drizzle","Snow Blowing Snow Mist","Light Rain Showers","Light Rain Mist","Light Blowing Sand","Light Blowing Snow","Low Drifting Widespread Dust","Light Low Drifting Widespread Dust","Haze","Light Widespread Dust","Light Smoke","Light Fog","Light Mist","Light Snow","Light Rain","Light Drizzle"]
    
    dark = ["Heavy Drizzle","Drizzle","Heavy Rain","Rain","Heavy Snow","Snow","Light Snow Grains","Heavy Snow Grains","Snow Grains","Light Ice Crystals","Heavy Ice Crystals","Ice Crystals","Light Ice Pellets","Heavy Ice Pellets","Ice Pellets","Light Hail","Heavy Hail","Hail","Heavy Mist","Mist","Heavy Fog","Fog","Heavy Fog Patches","Heavy Smoke","Smoke","Light Volcanic Ash","Heavy Volcanic Ash","Volcanic Ash","Heavy Widespread Dust","Widespread Dust","Heavy Sand","Heavy Haze","Heavy Spray","Heavy Dust Whirls","Light Sandstorm","Heavy Sandstorm","Sandstorm","Heavy Low Drifting Snow","Heavy Low Drifting Widespread Dust","Heavy Low Drifting Sand","Heavy Blowing Snow","Blowing Snow","Light Blowing Widespread Dust","Heavy Blowing Widespread Dust","Blowing Widespread Dust","Heavy Blowing Sand","Blowing Sand","Heavy Rain Mist","Rain Mist","Heavy Rain Showers","Rain Showers","Light Snow Showers","Heavy Snow Showers","Snow Showers","Heavy Snow Blowing Snow Mist","Light Ice Pellet Showers","Heavy Ice Pellet Showers","Ice Pellet Showers","Light Hail Showers","Heavy Hail Showers","Hail Showers","Light Small Hail Showers","Heavy Small Hail Showers","Small Hail Showers","Light Thunderstorm","Heavy Thunderstorm","Thunderstorm","Light Thunderstorms and Rain","Heavy Thunderstorms and Rain","Thunderstorms and Rain","Light Thunderstorms and Snow","Heavy Thunderstorms and Snow","Thunderstorms and Snow","Light Thunderstorms and Ice Pellets","Heavy Thunderstorms and Ice Pellets","Thunderstorms and Ice Pellets","Light Thunderstorms with Hail","Heavy Thunderstorms with Hail","Thunderstorms with Hail","Light Thunderstorms with Small Hail","Heavy Thunderstorms with Small Hail","Thunderstorms with Small Hail","Heavy Freezing Drizzle","Freezing Drizzle","Heavy Freezing Rain","Freezing Rain","Heavy Freezing Fog","Overcast","Mostly Cloudy","Small Hail","Squalls","Funnel Cloud"]

    if conditions in bright:
        #print conditions + " = bright"
        return 2
 
    elif conditions in dim:
        #print conditions + " = dim"
        return 1
    
    elif conditions in dark:
        #print conditions + " = dark"
        return 0

    else:
        #print conditions + " (unknown)"
        return -1
        
def getsundata(currdate):
    # retrieve sun data from database - only needs to happen once a day
    # should also be called on startup of script

    with db:
        c = db.cursor()
        c.execute('select sunup,sunup3,sunup6,sunset,sunset3,sunset6 from suntimes where date = ?',(currdate,))
        sundata = c.fetchone()
    return sundata
    
def pheyu(device,status):
       
    with db:
        cur = db.cursor()
        if 'on' in status:
            active = '1'
            heyucmd = 'fon'
        elif 'off' in status:
            active = '0'
            heyucmd = 'foff'
        else:
            return
            
        cur.execute("update x10 set active = " + active + ", timestamp = datetime('now')  where device = '" + device +"';")
        os.system('heyu ' + heyucmd + ' ' + device)
        
def storewxlights(level):
    
    with db:
        cur = db.cursor()
        cur.execute("update status set status = " + level + ", timestamp = datetime('now')  where object = 'wxlight';")
        
def readwxlights():

    with db:
        c = db.cursor()
        c.execute('select status,timestamp from status where object = "wxlight";')
        wxlightstatus = c.fetchone()
    return wxlightstatus
    