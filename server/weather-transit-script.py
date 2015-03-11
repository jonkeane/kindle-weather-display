#!/usr/bin/python

# Kindle Transit-Weather Display
# Inspired by Matthew Petroff (http://www.mpetroff.net/)
# November 2013	      

import urllib2
import json
import codecs
import os.path, time, datetime
import privateVars
import xml.etree.ElementTree as ET

iconMap = {"clear-day":  "clear.svg",
"clear-night":  "night/clear.svg",
"rain":  "rain.svg",
"snow":  "snow.svg",
"sleet":  "sleet.svg",
"wind":  "wind.svg",
"fog":  "fog.svg",
"cloudy":  "cloudy.svg",
"partly-cloudy-day":  "partlycloudy.svg",
"partly-cloudy-night":  "night/partlycloudy.svg"}

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
    
def weatherGrabber(type, path, source="forecastIO", apiKey=privateVars.forecastAPIkey, zipCode=privateVars.zipCode, lat=privateVars.lat, lng=privateVars.lng):
    if source == "wunderground":
        f = urllib2.urlopen('http://api.wunderground.com/api/'+apiKey+'/geolookup/'+type+'/q/'+zipCode+'.json')
    elif source == "forecastIO":
        f = urllib2.urlopen('https://api.forecast.io/forecast/'+apiKey+'/'+str(lat)+','+str(lng))
    currFile = open(path, "w")
    currFile.write(f.read())
    f.close()
    currFile.close()


def ctaPredGrabber(stopIDs, path, apiKey=privateVars.ctaAPIkey):
    if isinstance(stopIDs, str):
        stopIDs = [stopIDs]
    f = urllib2.urlopen('http://www.ctabustracker.com/bustime/api/v1/getpredictions?key='+apiKey+'&stpid='+','.join(stopIDs))
    currFile = open(path, "w")
    currFile.write(f.read())
    f.close()
    currFile.close()    
    
def ctaTrainPredGrabber(stopIDs, path, apiKey=privateVars.ctaTrainAPIkey):
    if isinstance(stopIDs, str):
        stopIDs = [stopIDs]
    f = urllib2.urlopen('http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key='+apiKey+'&stpid='+','.join(stopIDs))
    currFile = open(path, "w")
    currFile.write(f.read())
    f.close()
    currFile.close()    
    
def addTransit(output, paths=["localData/busPredictions.xml","localData/trainPredictions.xml"]):
    ########## transit ###########
    #establish display variables:
    show="inline"
    hide="none"

    thingsToTrack = privateVars.busesToTrack.keys() + privateVars.trainsToTrack.keys()

    buses = {x:[] for x in thingsToTrack}
    arrivals = {x:[] for x in thingsToTrack}
    
    
    bounds = {"Northbound": "nb", "Southbound": "sb", "Eastbound": "eb", "Westbound": "wb","NORTH": "nb", "SOUTH": "sb", "EAST": "eb", "WEST": "wb"}
    
    trainStopIDsToBounds = {"30020": "nb", "30021": "sb"} # this should be abstracted
    
    seenVIDs = []

    # parse the buses file
    parsed_xml = ET.parse(paths[0])
    root = parsed_xml.getroot()
    for child in root:
        if child.tag == "prd":
            dupCheck = ''.join([bounds[child.findall('rtdir')[0].text],child.findall('rt')[0].text,child.findall('vid')[0].text,child.findall('prdtm')[0].text])
            if dupCheck not in seenVIDs:
                seenVIDs.append(dupCheck)
                
                route = ''.join([bounds[child.findall('rtdir')[0].text],child.findall('rt')[0].text])
                try:
                    buses[route].append(child.findall('prdtm')[0].text)
                except KeyError:
                    pass
                    
    # parse the trains file
    parsed_xml = ET.parse(paths[1])
    root = parsed_xml.getroot()
    for child in root:
        if child.tag == "eta":
            dupCheck = ''.join([trainStopIDsToBounds[child.findall('stpId')[0].text],child.findall('rt')[0].text,child.findall('rn')[0].text,child.findall('arrT')[0].text])
            if dupCheck not in seenVIDs:
                seenVIDs.append(dupCheck)
             
                route = ''.join([trainStopIDsToBounds[child.findall('stpId')[0].text],child.findall('rt')[0].text]).lower()
                try:
                    buses[route].append(child.findall('arrT')[0].text)
                except KeyError:
                    pass                   
                                        
    #make a dictionary of arrival times
    for bus in arrivals.keys():     
        for indBus in buses[bus]:
            if len(indBus) == 14: # for buses
                arrival = datetime.datetime.strptime(indBus, "%Y%m%d %H:%M")-datetime.datetime.fromtimestamp(time.mktime(time.localtime()))            
                # subtract a minute from the minutes until arrival
                arrival = arrival-datetime.timedelta(seconds=60)
            if len(indBus) == 17: # for trains
                arrival = datetime.datetime.strptime(indBus, "%Y%m%d %H:%M:%S")-datetime.datetime.fromtimestamp(time.mktime(time.localtime()))            
                arrival = arrival-datetime.timedelta(seconds=00)
            # ensure that arrival times are longer than 1 minute
            if arrival>datetime.timedelta(seconds=60):
                # extract the minutes
                arrival = str(arrival).split(":")[1]  
                arrivals[bus].append(arrival)
            
    for bus in buses.keys():
        # grab the place identifier
        busPlace = privateVars.busPlaces[bus[2:]]
        # add the up or down designation 
        if bus[:2] == "nb" or  bus[:2] == "wb":
            busPlace = busPlace+"_D"
        else:
            busPlace = busPlace+"_U"        
        for n in range (3):
            try:
                arrival = arrivals[bus][n]
                # clean the arrival time
                if arrival == "00":
                    arrival = "0" # due does not fit with the current setup.
                elif arrival[0] == "0":
                    arrival = arrival[1:]
                output = output.replace(busPlace+str(n+1)+'_DISP', show)
                output = output.replace(busPlace+str(n+1), arrival)
            except IndexError:
                output = output.replace(busPlace+str(n+1)+'_DISP', hide)
                output = output.replace(busPlace+str(n+1), "")
                pass

    # Insert icons and temperatures

    #get localtime, add a minute to align better after synchronization
    lTime = str(datetime.datetime.fromtimestamp(time.mktime(time.localtime()))+ datetime.timedelta(seconds=60)).split(' ')[1]
    hrs = lTime.split(':')[0]
    mins = lTime.split(':')[1]
    if len(mins) < 2:
        mins = "0"+mins
    lTimeF = hrs+":"+mins
    output = output.replace('TIME',str(lTimeF))

    output = output.replace('DISP_TRANSIT',show)

    return(output)



# check the ctabusPredictions file to see if it's older than 5 seconds
if fileChecker("localData/busPredictions.xml", 5) == "create":
    ctaPredGrabber(stopIDs=privateVars.busesToTrack.values(), path="localData/busPredictions.xml")

# check the cttrainPredictions file to see if it's older than 5 seconds
if fileChecker("localData/trainPredictions.xml", 5) == "create":
    ctaTrainPredGrabber(stopIDs=privateVars.trainsToTrack.values(), path="localData/trainPredictions.xml")


    
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

# parse out the dynamic variables for wunderground
# CURRTEMP = int(round(parsed_json['current_observation']['temp_f']))
# CURRFEELS = int(round(float(parsed_json['current_observation']['feelslike_f'])))
# CURRWIND = int(round(parsed_json['current_observation']['wind_mph']))
# WIND_DEGS = parsed_json['current_observation']['wind_degrees']
# CURRHUM = parsed_json['current_observation']['relative_humidity']
# CURR_COND_ICON = parsed_json['current_observation']['icon']
# # check if the icon url has nt_ at the beginning
# if parsed_json['current_observation']['icon_url'].split('/')[-1][:3] == "nt_":
#     pre = "night/"
# else:
#     pre = ""
# CURR_COND_ICON_url = 'weather-icons/' + pre + CURR_COND_ICON + '.svg'

# parse out the dynamic variables for forecast
CURRTEMP = int(round(parsed_json['currently']['temperature']))
CURRFEELS = int(round(float(parsed_json['currently']['apparentTemperature'])))
CURRWIND = int(round(parsed_json['currently']['windSpeed']))
WIND_DEGS = parsed_json['currently']['windBearing']
CURRHUM = parsed_json['currently']['humidity']
CURR_COND_ICON = parsed_json['currently']['icon']
CURR_COND_ICON_url = 'weather-icons/' + iconMap[CURR_COND_ICON]

# Insert icons and temperatures
output = output.replace('CURRTEMP',str(CURRTEMP))
output = output.replace('CURRFEELS',str(CURRFEELS))
output = output.replace('CURRWIND',str(CURRWIND))
# output = output.replace('CURRHUM',str(CURRHUM.strip('%'))) # for wunderground
output = output.replace('CURRHUM',str(int(CURRHUM*100))) # for forecast.io
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

# add transit information
output = addTransit(output)

output = output.replace('DISP_CURR',show)
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
# if fileChecker("localData/hourly.json", 3600) == "create":
#     weatherGrabber(type="hourly", path="localData/hourly.json")
# fCurrCond = open("localData/hourly.json",'r')
fCurrCond = open("localData/currentConditions.json",'r')

# read the file
json_string = fCurrCond.read()
parsed_json = json.loads(json_string)
fCurrCond.close()

# parse out the dynamic variables wunderground
# hours = [int(parsed_json['hourly_forecast'][x]['FCTTIME']['hour']) for x in range(1,13)]
# temps = [int(parsed_json['hourly_forecast'][x]['temp']['english']) for x in range(1,13)]
# winds = [int(parsed_json['hourly_forecast'][x]['wspd']['english']) for x in range(1,13)]
# winds_degs = [int(parsed_json['hourly_forecast'][x]['wdir']['degrees']) for x in range(1,13)]
# humids = [int(parsed_json['hourly_forecast'][x]['humidity']) for x in range(1,13)]
# percips = [int(parsed_json['hourly_forecast'][x]['pop']) for x in range(1,13)]
# cond_icons = [(parsed_json['hourly_forecast'][x]['icon'],  parsed_json['hourly_forecast'][x]['icon_url'].split('/')[-1][:3]) for x in range(1,13)]

# parse out the dynamic variables forecastio
hours = [time.strftime("%H", time.localtime(int(parsed_json['hourly']['data'][x]['time'])))  for x in range(1,13)]
temps = [int(round(parsed_json['hourly']['data'][x]['temperature'])) for x in range(1,13)]
winds = [int(round(parsed_json['hourly']['data'][x]['windSpeed'])) for x in range(1,13)]
winds_degs = [int(parsed_json['hourly']['data'][x]['windBearing']) for x in range(1,13)]
humids = [int(parsed_json['hourly']['data'][x]['humidity']*100) for x in range(1,13)]
percips = [int(parsed_json['hourly']['data'][x]['precipProbability']*100) for x in range(1,13)]
cond_icons = [(parsed_json['hourly']['data'][x]['icon']) for x in range(1,13)]

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
    # for wunderground
    # if v[1] == "nt_":
    #     pre = "night/"
    # else:
    #     pre = ""
    # CURR_COND_ICON_url = 'weather-icons/' + pre + v[0] + '.svg'
    CURR_COND_ICON_url = 'weather-icons/' + iconMap[v]
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

#Add transit information
output = addTransit(output)

output = output.replace('DISP_CURR',hide)
output = output.replace('DISP5DAY',hide)
output = output.replace('DISP12HOUR',show)

# Write output
codecs.open('weather-script-output-hourly.svg', 'w', encoding='utf-8').write(output)


########## daily ###########
# Open SVG to process
output = codecs.open('weather-transit-preprocess.svg', 'r', encoding='utf-8').read()

#establish display variables:
show="inline"
hide="none"

### Deal with the hourly file
# check the currenConditions file to see if it's older than 5 minutes
# if fileChecker("localData/hourly.json", 3600) == "create":
#     weatherGrabber(type="hourly", path="localData/hourly.json")
# fCurrCond = open("localData/hourly.json",'r')
fCurrCond = open("localData/currentConditions.json",'r')

# read the file
json_string = fCurrCond.read()
parsed_json = json.loads(json_string)
fCurrCond.close()


# parse out the dynamic variables forecastio
days = [time.strftime("%A", time.localtime(int(parsed_json['daily']['data'][x]['time'])))  for x in range(0,5)]
hitemps = [int(round(parsed_json['daily']['data'][x]['temperatureMax'])) for x in range(0,5)]
lotemps = [int(round(parsed_json['daily']['data'][x]['temperatureMin'])) for x in range(0,5)]
cond_icons = [(parsed_json['daily']['data'][x]['icon']) for x in range(0,5)]

# Insert icons and temperatures
h = 1
for v in days:
    output = output.replace('DAY_'+str(h)+'_',str(v))
    h += 1
h = 1
for v in hitemps:
    output = output.replace('TEMP_HI_'+str(h)+'_',str(v))
    h += 1    
h = 1
for v in lotemps:
    output = output.replace('TEMP_LO_'+str(h)+'_',str(v))
    h += 1    
  
    

# Grab the icon for the condition
h = 1       
for v in cond_icons:
    # for wunderground
    # if v[1] == "nt_":
    #     pre = "night/"
    # else:
    #     pre = ""
    # CURR_COND_ICON_url = 'weather-icons/' + pre + v[0] + '.svg'
    CURR_COND_ICON_url = 'weather-icons/' + iconMap[v]
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
    output = output.replace('DAY_COND_ICON_'+str(h),icon)
    h += 1

#Add transit information
output = addTransit(output)

output = output.replace('DISP_CURR',hide)
output = output.replace('DISP5DAY',show)
output = output.replace('DISP12HOUR',hide)

# Write output
codecs.open('weather-script-output-daily.svg', 'w', encoding='utf-8').write(output)




