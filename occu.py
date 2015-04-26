#!/usr/bin/python

import os, sys, datetime, time, logging
import json, requests, sqlite3
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

db = sqlite3.connect('/home/pi/database.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

# script to read thermostat data - specifically occupied status of ecobee3 and sensors
# flow is to read the auth file, see if it is expired and renew if necessary
# then do api request and update sql database with current status and time

def doPinReg():
    url='https://api.ecobee.com/authorize'
    payload={'response_type':'ecobeePin','client_id':'***REMOVED***','scope':'smartWrite'}
    r = requests.get(url,params=payload)
    print('Enter the following PIN in the ecobee portal:')
    print(r.json()['ecobeePin'])
    pinSuccess = False
    while(not pinSuccess):
        time.sleep(30)
        pinSuccess = doPinTokenReq(r.json()['code'])
	
    
def doPinTokenReq(authZToken):
    payload = {'grant_type':'ecobeePin', 'code':authZToken,'client_id':'***REMOVED***'}
    url = 'https://api.ecobee.com/token'
    
    r = requests.post(url,params=payload)
    if 'error' in r.json():
        print(r.json()['error_description'])
        return False
    else:
        print('Auth Success')
        with open('/home/pi/x10/ecobeeAuth.json','w') as f:
            json.dump(r.json(),f)
        return True

def readJsonFile(filename='/home/pi/x10/ecobeeAuth.json'):
    r = json.load(open(filename))
    return r
       
def isAuthTokenExpired(filename='/home/pi/x10/ecobeeAuth.json'):
    tokenAgeSecs = time.time() - os.path.getmtime(filename)
    if tokenAgeSecs > (59*60):
        expired = True
    else:
        expired = False
	
    return expired

def renewAuthToken(renewToken):
    payload = {'grant_type':'refresh_token', 'refresh_token':renewToken,'client_id':'***REMOVED***'}
    url = 'https://api.ecobee.com/token'
    
    r = requests.post(url,params=payload)
    
    if 'error' in r.json():
        #print(r.json()['error_description'])
        return False
    else:
        #print('Renew Success')
        with open('/home/pi/x10/ecobeeAuth.json','w') as f:
            json.dump(r.json(),f)
        return True
    
def getAuthToken():
    if isAuthTokenExpired():
        if not renewAuthToken(readJsonFile()["refresh_token"]):
            return 0
    
    authJson = readJsonFile()
    return authJson["access_token"]

def doApiRequest(requestUrl,requestDict):
    headers={'Content-Type':'application/json;charset=UTF-8','Authorization':'Bearer ' + getAuthToken()}
    url='https://api.ecobee.com/1/' + requestUrl
    requestPayload={'format':'json','body':json.dumps(requestDict)}
    r = requests.get(url,params=requestPayload,headers=headers)
    
    return r
    
def updateStatus(thing,stats):

    with db:
        cur = db.cursor()
        #print "update things set status = '%(stats)s', timestamp = ? where object = '%(thing)s'" % {"thing" : thing, "stats" : stats}
        cur.execute("update things set status = '%(stats)s', timestamp = ? where object = '%(thing)s'" % {"thing" : thing, "stats" : stats},[datetime.datetime.now()])

def readStatus(thing):

    with db:
        c = db.cursor()
        c.execute("select status,timestamp from things where object = ?",[thing])
        data = c.fetchone()
    return data
      
def sensorStatus():
    requestUrl = 'thermostat'
    requestDict = {'selection':{'selectionType':'registered','selectionMatch':'','includeSensors':'true'}}
    r = doApiRequest(requestUrl,requestDict)
    returnDict = dict()
    for sensor in r.json()["thermostatList"][0]["remoteSensors"]:
        for cap in sensor["capability"]:
            if "occupancy" in cap["type"]:
                returnDict[sensor["name"]]=cap["value"]
    
    return returnDict
    
def runtimeRev():
    requestUrl = 'thermostatSummary'
    requestDict = {'selection':{'selectionType':'registered','selectionMatch':'','includeRuntime':'true'}}
    r = doApiRequest(requestUrl,requestDict)
    return(r.json()["revisionList"][0].split(":")[5])
    
def main():
    prevRev = readStatus('runtimeRevision')[0]
    #print(prevRev)
    currentRev = runtimeRev()
    #print(currentRev)
    
    if prevRev not in currentRev:
        updateStatus('runtimeRevision',currentRev)
        sensorDict = sensorStatus()
        for sensor in sensorDict:
            updateStatus(sensor,sensorDict[sensor])
            
main()
