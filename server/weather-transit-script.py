#!/usr/bin/python2

# Kindle Transit-Weather Display
# Inspired by Matthew Petroff (http://www.mpetroff.net/)
# November 2013	      

import urllib2
import json
import codecs
import os.path, time, datetime
import privateVars

def fileChecker(path, refreshInterval):
    # check if the file exists
    if os.path.isfile(path):
        #check the time and compare it to the refresh interval
        mTime = time.strptime(time.ctime(os.path.getmtime(path)))
        lTime = time.localtime()
        # difference between modified time and local time in seconds
        if time.mktime(lTime)-time.mktime(mTime) > refreshInterval:
            output = "create"
        else:
            output = "useOld"        
    else:  
        output = "create"
    return output
    
def weatherGrabber(type, path, apiKey=privateVars.apiKey, zipCode=privateVars.zipCode):
    f = urllib2.urlopen('http://api.wunderground.com/api/'+apiKey+'/geolookup/'+type+'/q/'+zipCode+'.json')
    currFile = open(path, "w")
    currFile.write(f.read())
    f.close()
    currFile.close()
    
########## current ###########
# Open SVG to process
output = codecs.open('weather-transit-preprocess.svg', 'r', encoding='utf-8').read()

#establish display variables:
show="inline"
hide="none"

### Deal with the currentConditions file
# check the currenConditions file to see if it's older than 5 minutes
if fileChecker("localData/currentConditions.json", 300) == "create":
    weatherGrabber(type="conditions", path="localData/currentConditions.json")
fCurrCond = open("localData/currentConditions.json",'r')

# read the file
json_string = fCurrCond.read()
parsed_json = json.loads(json_string)
fCurrCond.close()

# parse out the dynamic variables
CURRTEMP = int(round(parsed_json['current_observation']['temp_f']))
CURRFEELS = int(round(float(parsed_json['current_observation']['feelslike_f'])))
CURRWIND = int(round(parsed_json['current_observation']['wind_mph']))
WIND_DEGS = parsed_json['current_observation']['wind_degrees']
CURRHUM = parsed_json['current_observation']['relative_humidity']
CURR_COND_ICON = parsed_json['current_observation']['icon']
CURR_COND_ICON = "mostlysunny"
CURR_COND_ICON_url = 'weather-icons/' + CURR_COND_ICON + '.svg'

# Insert icons and temperatures
output = output.replace('CURRTEMP',str(CURRTEMP))
output = output.replace('CURRFEELS',str(CURRFEELS))
output = output.replace('CURRWIND',str(CURRWIND))
output = output.replace('CURRHUM',str(CURRHUM.strip('%')))
output = output.replace('WIND_DEGS',str(WIND_DEGS))

# Grab the icon for the condition
if os.path.isfile(CURR_COND_ICON_url):
    fIcon = codecs.open(CURR_COND_ICON_url ,'r', encoding='utf-8')
    fIcon.readline()
    icon = fIcon.readline()
    fIcon.close()
else:
    fIcon = codecs.open("weather-icons/unknown.svg" ,'r', encoding='utf-8')
    fIcon.readline()
    icon = fIcon.readline()
    fIcon.close()        
output = output.replace('CURR_COND_ICON',icon)

#get localtime, add a minute to align better after synchronization
lTime = time.localtime()
hrs = str(lTime.tm_hour)
mins = str(lTime.tm_min+1)
if len(mins) < 2:
    mins = "0"+mins
lTimeF = hrs+":"+mins
output = output.replace('TIME',str(lTimeF))

output = output.replace('DISP_CURR',show)
output = output.replace('DISP_TRANSIT',show)
output = output.replace('DISP5DAY',hide)
output = output.replace('DISP12HOUR',hide)

# Write output
codecs.open('weather-script-output-current.svg', 'w', encoding='utf-8').write(output)



########## hourly ###########
# Open SVG to process
output = codecs.open('weather-transit-preprocess.svg', 'r', encoding='utf-8').read()

#establish display variables:
show="inline"
hide="none"

### Deal with the hourly file
# check the currenConditions file to see if it's older than 5 minutes
if fileChecker("localData/hourly.json", 3600) == "create":
    weatherGrabber(type="hourly", path="localData/hourly.json")
fCurrCond = open("localData/hourly.json",'r')

# read the file
json_string = fCurrCond.read()
parsed_json = json.loads(json_string)
fCurrCond.close()

# parse out the dynamic variables
hours = [int(parsed_json['hourly_forecast'][x]['FCTTIME']['hour']) for x in range(12)]
temps = [int(parsed_json['hourly_forecast'][x]['temp']['english']) for x in range(12)]
winds = [int(parsed_json['hourly_forecast'][x]['wspd']['english']) for x in range(12)]
winds_degs = [int(parsed_json['hourly_forecast'][x]['wdir']['degrees']) for x in range(12)]
humids = [int(parsed_json['hourly_forecast'][x]['humidity']) for x in range(12)]
percips = [int(parsed_json['hourly_forecast'][x]['pop']) for x in range(12)]
cond_icons = [parsed_json['hourly_forecast'][x]['icon'] for x in range(12)]

#CURR_COND_ICON = "mostlysunny"
#CURR_COND_ICON_url = 'weather-icons/' + CURR_COND_ICON + '.svg'

# Insert icons and temperatures
h = 1
for v in hours:
    output = output.replace('H_'+str(h)+'_',str(v))
    h += 1
h = 1
for v in temps:
    output = output.replace('TEMP_'+str(h)+'_',str(v))
    h += 1    
h = 1
for v in winds:
    output = output.replace('WINDSPEED_'+str(h)+'_',str(v))
    h += 1  
h = 1
for v in winds_degs:
    output = output.replace('HOUR_'+str(h)+'_WIND_DEGS',str(v))
    h += 1  
h = 1
for v in humids:
    output = output.replace('HUMID_'+str(h)+'_',str(v))
    h += 1  
h = 1       
for v in percips:
    output = output.replace('PERC_'+str(h)+'_',str(v))
    h += 1      
    

# Grab the icon for the condition
h = 1       
for v in cond_icons:
    CURR_COND_ICON_url = 'weather-icons/' + v + '.svg'
    if os.path.isfile(CURR_COND_ICON_url):
        fIcon = codecs.open(CURR_COND_ICON_url ,'r', encoding='utf-8')
        fIcon.readline()
        icon = fIcon.readline()
        fIcon.close()
    else:
        fIcon = codecs.open("weather-icons/unknown.svg" ,'r', encoding='utf-8')
        fIcon.readline()
        icon = fIcon.readline()
        fIcon.close()        
    output = output.replace('HOUR_'+str(h)+'_COND_ICON',icon)
    h += 1

#get localtime, add a minute to align better after synchronization
lTime = time.localtime()
hrs = str(lTime.tm_hour)
mins = str(lTime.tm_min+1)
if len(mins) < 2:
    mins = "0"+mins
lTimeF = hrs+":"+mins
output = output.replace('TIME',str(lTimeF))

output = output.replace('DISP_TRANSIT',show)
output = output.replace('DISP_CURR',hide)
output = output.replace('DISP5DAY',hide)
output = output.replace('DISP12HOUR',show)

# Write output
codecs.open('weather-script-output-hourly.svg', 'w', encoding='utf-8').write(output)


