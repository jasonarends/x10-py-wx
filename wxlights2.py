#!/usr/bin/python

import os, sys, serial
import json, sqlite3
import datetime, time
import logging

logging.basicConfig(filename='/home/pi/x10/wxlights.log',format='%(asctime)s %(message)s',level=logging.WARNING)

db = sqlite3.connect('/home/pi/database.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)



def dolights():

    rightnow = timeofday() #morning, day, night, etc
    brightness = lightlevel() #bright, dim, dark

    #previous values read from database
    previousbrightness = readstatus('wxlight')
    previoustime = readstatus('sun')

    #update database with current values
    updatestatus('sun',rightnow)
    updatestatus('wxlight',brightness)
    
    occupiedLr = readstatus('Living Room')[0] in "true"
    logging.debug('living room: %s',occupiedLr)
    occupiedOf = readstatus('Office')[0] in "true"
    logging.debug('office: %s',occupiedOf)


    if brightness in previousbrightness:
        brightnesschanged = False
    else:
        brightnesschanged = True

    if rightnow in previoustime:
        timechanged = False
    else:
        timechanged = True
        
    logging.debug('time of day: %s, brightness: %s',rightnow,brightness)
    
    if rightnow in ("morning"):
        # morning - all lights on (except 5)
        if occupiedLr:
            smartx10("j2","on")
            smartx10("j4","on")
            smartx10("j6","on")
            smartx10("j5","off")
        else:
            smartx10("j2","off")
            smartx10("j4","off")
            smartx10("j6","on")
            smartx10("j5","off")
        
        if occupiedOf:
            smartx10("j7","on")
        else:
            smartx10("j7","off")

    elif rightnow in ("sunup1"):
        # turn off j2, all else stay on
        if occupiedLr:
            smartx10("j2","off")
            smartx10("j4","on")
            smartx10("j6","on")
            smartx10("j5","off")
        else:
            smartx10("j2","off")
            smartx10("j4","off")
            smartx10("j6","on")
            smartx10("j5","off")
        
        if occupiedOf:
            smartx10("j7","on")
        else:
            smartx10("j7","off")

    elif rightnow in ("sunup2"):
        # turn off j2, others depend on wx
        smartx10("j2","off")

        if brightness in "bright":
            if occupiedLr:
                smartx10("j4","on")
                smartx10("j5","off")
                smartx10("j6","off")
            else:
                smartx10("j4","off")
                smartx10("j5","off")
                smartx10("j6","off")
            smartx10("j7","off")
        elif brightness in ("dim","dark","unknown"):
            if occupiedLr:
                smartx10("j4","on")
                smartx10("j5","off")
                smartx10("j6","on")
            else:
                smartx10("j4","off")
                smartx10("j5","off")
                smartx10("j6","off")
                
            if occupiedOf:
                smartx10("j7","on")
            else:
                smartx10("j7","off")

    elif rightnow in "day":
        # turn off j2,6 others depend on wx
        smartx10("j2","off")
        smartx10("j6","off")

        if brightness in "bright":
            smartx10("j4","off")
            smartx10("j5","off")
            smartx10("j7","off")
        elif brightness in "dim":
            if occupiedLr:
                smartx10("j4","on")
            else:
                smartx10("j4","off")
            smartx10("j5","off")
            smartx10("j7","off")
        elif brightness in ("dark","unknown"):
            if occupiedLr:
                smartx10("j4","on")
                smartx10("j5","on")
            else:
                smartx10("j4","off")
                smartx10("j5","off")
            if occupiedOf:
                smartx10("j7","on")
            else:
                smartx10("j7","off")

    elif rightnow in ("sunset1"):
        # turn off j2, others depend on wx
        smartx10("j2","off")
        smartx10("j6","off")

        if brightness in "bright":
            if occupiedLr:
                smartx10("j4","on")
                smartx10("j5","off")
            else:
                smartx10("j4","off")
                smartx10("j5","off")
            smartx10("j7","off")
        elif brightness in ("dim","dark","unknown"):
            if occupiedLr:
                smartx10("j4","on")
                smartx10("j5","on")
            else:
                smartx10("j4","off")
                smartx10("j5","off")
            if occupiedOf:
                smartx10("j7","on")
            else:
                smartx10("j7","off")

    elif rightnow in ("sunset2"):
        # turn off j2, all else stay on
        if occupiedLr:
            smartx10("j2","on")
            smartx10("j4","on")
            smartx10("j5","on")
            smartx10("j6","off")
        else:
            smartx10("j2","on")
            smartx10("j4","off")
            smartx10("j5","off")
            smartx10("j6","off")
        if occupiedOf:
            smartx10("j7","on")
        else:
            smartx10("j7","off")

    elif rightnow in ("night"):
        # night - all lights on
        if occupiedLr:
            smartx10("j2","on")
            smartx10("j4","on")
            smartx10("j5","on")
            smartx10("j6","on")
        else:
            smartx10("j2","on")
            smartx10("j4","off")
            smartx10("j5","off")
            smartx10("j6","off")
        if occupiedOf:
            smartx10("j7","on")
        else:
            smartx10("j7","off")

def smartx10(device,status):
    currentstatus = readx10(device)[0]
    lastchanged = readx10(device)[1]
    now = datetime.datetime.now()
    timesincechange = now - lastchanged
    if not currentstatus in status: #if the status is requested to be something other than we think it is, change it
        logging.debug('device %s requested to change to %s',device,status)
        if timesincechange > datetime.timedelta(minutes=10): #only change it if it's been more than 10 minutes since last change - to prevent rapid on/offs
            pheyu(device,status)
            logging.debug('more than 10 mins since last change, device %s changed to %s',device,status)
        else:
            logging.debug('last change <10 mins ago, nothing done.')
    else: #if status requested matches what we think it is, change it anyway if it's been 2 hours
        logging.debug('device %s already %s',device,status)
        if timesincechange > datetime.timedelta(hours=2):
            logging.debug('device %s last changed over 2 hours ago, forcing update',device)
            pheyu(device,status)
            

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

def lightlevel():
    conditions = formatwug()

    bright = ["Clear","Scattered Clouds","Patches of Fog","Shallow Fog","Light Snow Blowing Snow Mist","Low Drifting Sand","Light Low Drifting Sand","Low Drifting Snow","Light Low Drifting Snow","Dust Whirls","Light Dust Whirls","Light Spray","Spray","Light Haze","Sand","Light Sand","Light Fog Patches","Fog Patches"]

    dim = ["Unknown","Unknown Precipitation","Partly Cloudy","Partial Fog","Light Freezing Fog","Freezing Fog","Light Freezing Rain","Light Freezing Drizzle","Snow Blowing Snow Mist","Light Rain Showers","Light Rain Mist","Light Blowing Sand","Light Blowing Snow","Low Drifting Widespread Dust","Light Low Drifting Widespread Dust","Haze","Light Widespread Dust","Light Smoke","Light Fog","Light Mist","Light Snow","Light Rain","Light Drizzle","Snow","Light Snow Grains","Snow Grains","Light Snow Showers","Blowing Snow","Heavy Low Drifting Snow","Snow Showers","Heavy Snow Blowing Snow Mist","Light Ice Pellet Showers","Light Thunderstorms and Snow","Thunderstorms and Snow","Ice Pellet Showers","Smoke"]

    dark = ["Heavy Drizzle","Drizzle","Heavy Rain","Rain","Heavy Snow","Heavy Snow Grains","Light Ice Crystals","Heavy Ice Crystals","Ice Crystals","Light Ice Pellets","Heavy Ice Pellets","Ice Pellets","Light Hail","Heavy Hail","Hail","Heavy Mist","Mist","Heavy Fog","Fog","Heavy Fog Patches","Heavy Smoke","Light Volcanic Ash","Heavy Volcanic Ash","Volcanic Ash","Heavy Widespread Dust","Widespread Dust","Heavy Sand","Heavy Haze","Heavy Spray","Heavy Dust Whirls","Light Sandstorm","Heavy Sandstorm","Sandstorm","Heavy Low Drifting Widespread Dust","Heavy Low Drifting Sand","Heavy Blowing Snow","Light Blowing Widespread Dust","Heavy Blowing Widespread Dust","Blowing Widespread Dust","Heavy Blowing Sand","Blowing Sand","Heavy Rain Mist","Rain Mist","Heavy Rain Showers","Rain Showers","Heavy Snow Showers","Heavy Ice Pellet Showers","Light Hail Showers","Heavy Hail Showers","Hail Showers","Light Small Hail Showers","Heavy Small Hail Showers","Small Hail Showers","Light Thunderstorm","Heavy Thunderstorm","Thunderstorm","Light Thunderstorms and Rain","Heavy Thunderstorms and Rain","Thunderstorms and Rain","Heavy Thunderstorms and Snow","Light Thunderstorms and Ice Pellets","Heavy Thunderstorms and Ice Pellets","Thunderstorms and Ice Pellets","Light Thunderstorms with Hail","Heavy Thunderstorms with Hail","Thunderstorms with Hail","Light Thunderstorms with Small Hail","Heavy Thunderstorms with Small Hail","Thunderstorms with Small Hail","Heavy Freezing Drizzle","Freezing Drizzle","Heavy Freezing Rain","Freezing Rain","Heavy Freezing Fog","Overcast","Mostly Cloudy","Small Hail","Squalls","Funnel Cloud"]

    if conditions in bright:
        #print conditions + " = bright"
        logging.debug('%s is bright',conditions)
        return "bright"

    elif conditions in dim:
        #print conditions + " = dim"
        logging.debug('%s is dim',conditions)
        return "dim"

    elif conditions in dark:
        #print conditions + " = dark"
        logging.debug('%s is dark',conditions)
        return "dark"

    else:
        #print conditions + " (unknown)"
        logging.debug('%s is unknown',conditions)
        return "unknown"

def getsundata(currdate):
    # retrieve sun data from database - only needs to happen once a day
    # should also be called on startup of script

    with db:
        c = db.cursor()
        c.execute('select sunup,sunup3,sunup6,sunset,sunset3,sunset6 from suntimes where date = ?',(currdate,))
        sundata = c.fetchone()
    return sundata

def pheyu(device,status):

    if 'on' in status:
        active = '1'
        heyucmd = 'fon'
    elif 'off' in status:
        active = '0'
        heyucmd = 'foff'
    else:
        return

    with db:
        cur = db.cursor()

        cur.execute("update x10 set active = '%(act)s', timestamp = ? where device = '%(dev)s'" % {"act" : active, "dev" : device},[datetime.datetime.now()])
        os.system('heyu ' + heyucmd + ' ' + device)

def readx10(device):

    with db:
        cur = db.cursor()
        cur.execute("select active,timestamp from x10 where device = ?",[device])
        x10 = cur.fetchone()
        if x10[0]:
            status = "on"
        else:
            status = "off"
        return (status,x10[1])
        
def readAllX10():
    with db:
        cur = db.cursor()
        cur.execute("select device,active from x10")
        x10 = cur.fetchall()
        return x10

def updatestatus(thing,stats):

    with db:
        cur = db.cursor()
        #print "update things set status = '%(stats)s', timestamp = ? where object = '%(thing)s'" % {"thing" : thing, "stats" : stats}
        cur.execute("update things set status = '%(stats)s', timestamp = ? where object = '%(thing)s'" % {"thing" : thing, "stats" : stats},[datetime.datetime.now()])

def readstatus(thing):

    with db:
        c = db.cursor()
        c.execute("select status,timestamp from things where object = ?",[thing])
        data = c.fetchone()
    return data

def timeofday(now = datetime.datetime.now()):

    sundata = getsundata(now.date())

    if now < sundata[0]:
        #before sunrise
        return "morning"
    elif now < sundata[1]:
        #after sunup but before 3 degrees up
        return "sunup1"
    elif now < sundata[2]:
        #between 3 and 6 degrees up
        return "sunup2"
    elif now < sundata[5]:
        #above 6 degrees before sunset
        return "day"
    elif now < sundata[4]:
        #between 6 and 3 degrees down
        return "sunset1"
    elif now < sundata[3]:
        #before sundown but less than 3 degrees
        return "sunset2"
    elif now > sundata[3]:
        #after sunset
        return "night"

def matrixwritecommand(commandlist):
    ser = serial.Serial('/dev/ttyACM0', 19200, timeout=1)
    commandlist.insert(0, 0xFE)
    for i in range(0, len(commandlist)):
         ser.write(chr(commandlist[i]))

def lcdInit():
    # turn on display
    matrixwritecommand([0x42, 0])
    # setup contrast, brightness, color
    matrixwritecommand([0x91,220]) # contrast 220 seems best
    time.sleep(0.1)
    matrixwritecommand([0x99,128]) #brightness 256 is full
    time.sleep(0.1)
    matrixwritecommand([0x4b])
    time.sleep(0.1)
    matrixwritecommand([0x54])
    time.sleep(0.1)
    matrixwritecommand([0xd0,255,255,255]) #color RGB
    #go home
    matrixwritecommand([0x48])

def writeLCD(line1,line2):
    lcdInit()
    ser = serial.Serial('/dev/ttyACM0', 19200, timeout=1)
    ser.write(line1)
    # move to line 2
    matrixwritecommand([0x47, 1, 2])
    ser.write(line2)
    
def buildLcdDisplay():
    x10List = readAllX10()
    line1 = ''
    for device in x10List:
        if device[1]:
            line1 = line1 + device[0][-1]
        else:
            line1 = line1 + '-'
    line2 = str(datetime.datetime.now().hour) + ":%(m)02d " %{"m":datetime.datetime.now().minute} + timeofday() + " " + lightlevel()
    logging.debug(line1 + ' ' + line2)
    
    writeLCD(line1,line2)


dolights()
buildLcdDisplay()
