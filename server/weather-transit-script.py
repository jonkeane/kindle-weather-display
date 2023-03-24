#!/usr/bin/python

# Kindle Transit-Weather Display
# Inspired by Matthew Petroff (http://www.mpetroff.net/)
# November 2013

import requests
import json
import codecs
import os.path, time, datetime
import privateVars
import xml.etree.ElementTree as ET

from zoneinfo import ZoneInfo


def iconMap(condition, daylight):
    # deal with other codes? https://github.com/hrbrmstr/weatherkit/blob/batman/R/enumerations.R
    map = {
        "Clear": "clear.svg",
        "Rain": "rain.svg",
        "Snow": "snow.svg",
        "Sleet": "sleet.svg",
        "Windy": "wind.svg",
        "Fog": "fog.svg",
        "Dust": "fog.svg",
        "Haze": "hazy.svg",
        "Cloudy": "cloudy.svg",
        "MostlyClear": "mostlyclear.svg",
        "MostlyCloudy": "mostlycloudy.svg",
        "PartlyCloudy": "partlycloudy.svg",
        "ScatteredThunderstorms": "tstorms.svg",
        "Smoke": "hazy.svg",
        "Breezy": "wind.svg",
        "Drizzle": "rain.svg",
        "HeavyRain": "rain.svg",
        "Showers": "rain.svg",
        "Flurries": "flurries.svg",
        "HeavySnow": "snow.svg",
        "MixedRainAndSleet": "sleet.svg",
        "MixedRainAndSnow": "snow.svg",
        "MixedRainfall": "rain.svg",
        "MixedSnowAndSleet": "sleet.svg",
        "ScatteredShowers": "rain.svg",
        "ScatteredSnowShowers": "snow.svg",
        "Sleet": "sleet.svg",
        "SnowShowers": "snow.svg",
        "Blizzard": "snow.svg",
        "BlowingSnow": "snow.svg",
        "FreezingDrizzle": "sleet.svg",
        "FreezingRain": "sleet.svg",
        "Frigid": "snow.svg",
        "Hail": "sleet.svg",
        "Hot": "sunny.svg",
        "Hurricane": "tstorms.svg",
        "IsolatedThunderstorms": "tstorms.svg",
        "SevereThunderstorm": "tstorms.svg",
        "Thunderstorm": "tstorms.svg",
        "Tornado": "tstorms.svg",
        "TropicalStorm": "tstorms.svg",
    }

    out = map[condition]

    # if it's night see if there's a night option, use that if so
    if daylight == False and os.path.isfile(f"weather-icons/night/{out}"):
        out = f"night/{out}"

    return f"weather-icons/{out}"


def fileChecker(path, refreshInterval):
    # check if the file exists
    if os.path.isfile(path):
        # check the time and compare it to the refresh interval
        mTime = time.strptime(time.ctime(os.path.getmtime(path)))
        lTime = time.localtime()
        # difference between modified time and local time in seconds
        if time.mktime(lTime) - time.mktime(mTime) > refreshInterval:
            output = "create"
        else:
            output = "useOld"
    else:
        output = "create"
    return output

def celsius_to_fahrenheit(celsius):
    """
    Convert temperature from Celsius to Fahrenheit.

    Arguments:
    celsius -- a temperature value in Celsius (float or integer)

    Returns:
    fahrenheit -- the equivalent temperature value in Fahrenheit (float)
    """
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

def weatherGrabber(
    type,
    path,
    source="weatherKit",
    apiKey=privateVars.weatherKitToken,
    zipCode=privateVars.zipCode,
    lat=privateVars.lat,
    lng=privateVars.lng,
):
    if source == "wunderground":
        f = requests.get(
            "http://api.wunderground.com/api/"
            + apiKey
            + "/geolookup/"
            + type
            + "/q/"
            + zipCode
            + ".json"
        )
    elif source == "weatherKit":
        f = requests.get(
            f"https://weatherkit.apple.com/api/v1/weather/en/{lat}/{lng}?"
            + f"dataSets=currentWeather,forecastDaily,forecastHourly,forecastNextHour"
            + f"&timezone={privateVars.local_tz}"
            + f"&hourlyStart={datetime.datetime.now().astimezone(tz=ZoneInfo('UTC')).isoformat().replace('+00:00', 'Z')}",
            headers={"Authorization": f"Bearer {apiKey}"},
        )
    currFile = open(path, "w")
    currFile.write(f.text)
    f.close()
    currFile.close()


def ctaPredGrabber(stopIDs, path, apiKey=privateVars.ctaAPIkey):
    if isinstance(stopIDs, str):
        stopIDs = [stopIDs]
    f = requests.get(
        "http://www.ctabustracker.com/bustime/api/v1/getpredictions?key="
        + apiKey
        + "&stpid="
        + ",".join(stopIDs)
    )
    currFile = open(path, "w")
    currFile.write(f.text)
    f.close()
    currFile.close()


def ctaTrainPredGrabber(stopIDs, path, apiKey=privateVars.ctaTrainAPIkey):
    if isinstance(stopIDs, str):
        stopIDs = [stopIDs]
    f = requests.get(
        "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key="
        + apiKey
        + "&stpid="
        + ",".join(stopIDs)
    )
    currFile = open(path, "w")
    currFile.write(f.text)
    f.close()
    currFile.close()


def addTransit(
    output, paths=["localData/busPredictions.xml", "localData/trainPredictions.xml"]
):
    ########## transit ###########
    # establish display variables:
    show = "inline"
    hide = "none"

    thingsToTrack = list(privateVars.busesToTrack.keys()) + list(
        privateVars.trainsToTrack.keys()
    )

    buses = {x: [] for x in thingsToTrack}
    arrivals = {x: [] for x in thingsToTrack}

    bounds = {
        "Northbound": "nb",
        "Southbound": "sb",
        "Eastbound": "eb",
        "Westbound": "wb",
        "NORTH": "nb",
        "SOUTH": "sb",
        "EAST": "eb",
        "WEST": "wb",
    }

    # this should be abstracted
    trainStopIDsToBounds = {"30274": "sb", "30273": "nb", "30071": "sb", "30070": "nb"}
    seenVIDs = []

    # parse the buses file
    parsed_xml = ET.parse(paths[0])
    root = parsed_xml.getroot()
    for child in root:
        if child.tag == "prd":
            dupCheck = "".join(
                [
                    bounds[child.findall("rtdir")[0].text],
                    child.findall("rt")[0].text,
                    child.findall("vid")[0].text,
                    child.findall("prdtm")[0].text,
                ]
            )
            if dupCheck not in seenVIDs:
                seenVIDs.append(dupCheck)

                route = "".join(
                    [
                        bounds[child.findall("rtdir")[0].text],
                        child.findall("rt")[0].text,
                    ]
                )
                try:
                    buses[route].append(child.findall("prdtm")[0].text)
                except KeyError:
                    pass

    # parse the trains file
    parsed_xml = ET.parse(paths[1])
    root = parsed_xml.getroot()
    for child in root:
        if child.tag == "eta":
            dupCheck = "".join(
                [
                    trainStopIDsToBounds[child.findall("stpId")[0].text],
                    child.findall("rt")[0].text,
                    child.findall("rn")[0].text,
                    child.findall("arrT")[0].text,
                ]
            )
            if dupCheck not in seenVIDs:
                seenVIDs.append(dupCheck)

                route = "".join(
                    [
                        trainStopIDsToBounds[child.findall("stpId")[0].text],
                        child.findall("rt")[0].text,
                    ]
                ).lower()
                try:
                    buses[route].append(child.findall("arrT")[0].text)
                except KeyError:
                    pass

    # make a dictionary of arrival times
    for bus in arrivals.keys():
        for indBus in buses[bus]:
            if len(indBus) == 14:  # for buses
                arrival = datetime.datetime.strptime(
                    indBus, "%Y%m%d %H:%M"
                ) - datetime.datetime.fromtimestamp(time.mktime(time.localtime()))
                # subtract a minute from the minutes until arrival
                arrival = arrival - datetime.timedelta(seconds=60)
            if len(indBus) == 17:  # for trains
                arrival = datetime.datetime.strptime(
                    indBus, "%Y%m%d %H:%M:%S"
                ) - datetime.datetime.fromtimestamp(time.mktime(time.localtime()))
                arrival = arrival - datetime.timedelta(seconds=00)
            # ensure that arrival times are longer than 1 minute
            if arrival > datetime.timedelta(seconds=60):
                # extract the minutes
                arrival = str(arrival).split(":")[1]
                arrivals[bus].append(arrival)

    for bus in buses.keys():
        # grab the place identifier
        busPlace = privateVars.busPlaces[bus[2:]]
        # add the up or down designation
        if bus[:2] == "nb" or bus[:2] == "wb":
            busPlace = busPlace + "_D"
        else:
            busPlace = busPlace + "_U"
        for n in range(3):
            try:
                arrival = arrivals[bus][n]
                # clean the arrival time
                if arrival == "00":
                    arrival = "0"  # due does not fit with the current setup.
                elif arrival[0] == "0":
                    arrival = arrival[1:]
                output = output.replace(busPlace + str(n + 1) + "_DISP", show)
                output = output.replace(busPlace + str(n + 1), arrival)
            except IndexError:
                output = output.replace(busPlace + str(n + 1) + "_DISP", hide)
                output = output.replace(busPlace + str(n + 1), "")
                pass

    # Insert icons and temperatures

    # get localtime, add a minute to align better after synchronization
    lTime = str(
        datetime.datetime.fromtimestamp(time.mktime(time.localtime()))
        + datetime.timedelta(seconds=60)
    ).split(" ")[1]
    hrs = lTime.split(":")[0]
    mins = lTime.split(":")[1]
    if len(mins) < 2:
        mins = "0" + mins
    lTimeF = hrs + ":" + mins
    output = output.replace("TIME", str(lTimeF))

    output = output.replace("DISP_TRANSIT", show)

    return output


# check the ctabusPredictions file to see if it's older than 5 seconds
if fileChecker("localData/busPredictions.xml", 5) == "create":
    ctaPredGrabber(
        stopIDs=privateVars.busesToTrack.values(), path="localData/busPredictions.xml"
    )

# check the cttrainPredictions file to see if it's older than 5 seconds
if fileChecker("localData/trainPredictions.xml", 5) == "create":
    ctaTrainPredGrabber(
        stopIDs=privateVars.trainsToTrack.values(),
        path="localData/trainPredictions.xml",
    )


########## current ###########
# Open SVG to process
output = codecs.open("weather-transit-preprocess.svg", "r", encoding="utf-8").read()

# establish display variables:
show = "inline"
hide = "none"

### Deal with the currentConditions file
# check the currenConditions file to see if it's older than 5 minutes
if fileChecker("localData/currentConditions.json", 300) == "create":
    weatherGrabber(type="conditions", path="localData/currentConditions.json")
fCurrCond = open("localData/currentConditions.json", "r")

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
CURRTEMP = int(round(celsius_to_fahrenheit(parsed_json["currentWeather"]["temperature"])))
CURRFEELS = int(round(celsius_to_fahrenheit(parsed_json["currentWeather"]["temperatureApparent"])))
CURRWIND = int(round(parsed_json["currentWeather"]["windSpeed"]))
WIND_DEGS = parsed_json["currentWeather"]["windDirection"]
CURRHUM = parsed_json["currentWeather"]["humidity"]
CURR_COND_ICON = parsed_json["currentWeather"]["conditionCode"]
CURR_DAYLIGHT = parsed_json["currentWeather"]["daylight"]
CURR_COND_ICON_url = iconMap(CURR_COND_ICON, CURR_DAYLIGHT)

# Insert icons and temperatures
output = output.replace("CURRTEMP", str(CURRTEMP))
output = output.replace("CURRFEELS", str(CURRFEELS))
output = output.replace("CURRWIND", str(CURRWIND))
output = output.replace("CURRHUM", str(int(CURRHUM * 100)))  # for forecast.io
output = output.replace("WIND_DEGS", str(WIND_DEGS))

# Grab the icon for the condition
if os.path.isfile(CURR_COND_ICON_url):
    fIcon = codecs.open(CURR_COND_ICON_url, "r", encoding="utf-8")
    fIcon.readline()
    icon = fIcon.readline()
    fIcon.close()
else:
    fIcon = codecs.open("weather-icons/unknown.svg", "r", encoding="utf-8")
    fIcon.readline()
    icon = fIcon.readline()
    fIcon.close()
output = output.replace("CURR_COND_ICON", icon)

# add transit information
output = addTransit(output)

output = output.replace("DISP_CURR", show)
output = output.replace("DISP5DAY", hide)
output = output.replace("DISP12HOUR", hide)

# Write output
codecs.open("weather-script-output-current.svg", "w", encoding="utf-8").write(output)


########## hourly ###########
# Open SVG to process
output = codecs.open("weather-transit-preprocess.svg", "r", encoding="utf-8").read()

# establish display variables:
show = "inline"
hide = "none"

### Deal with the hourly file
# check the currenConditions file to see if it's older than 5 minutes
# if fileChecker("localData/hourly.json", 3600) == "create":
#     weatherGrabber(type="hourly", path="localData/hourly.json")
# fCurrCond = open("localData/hourly.json",'r')
fCurrCond = open("localData/currentConditions.json", "r")

# read the file
json_string = fCurrCond.read()
parsed_json = json.loads(json_string)
fCurrCond.close()

# parse out the dynamic variables weatherKit
hours = [
    datetime.datetime.fromisoformat(
        parsed_json["forecastHourly"]["hours"][x]["forecastStart"].replace(
            "Z", "+00:00"
        )
    ).astimezone(tz=ZoneInfo(privateVars.local_tz)).hour
    for x in range(1, 13)
]
temps = [
    int(round(celsius_to_fahrenheit(parsed_json["forecastHourly"]["hours"][x]["temperature"])))
    for x in range(1, 13)
]
winds = [
    int(round(parsed_json["forecastHourly"]["hours"][x]["windSpeed"]))
    for x in range(1, 13)
]
winds_degs = [
    int(parsed_json["forecastHourly"]["hours"][x]["windDirection"]) for x in range(1, 13)
]
humids = [
    int(parsed_json["forecastHourly"]["hours"][x]["humidity"] * 100)
    for x in range(1, 13)
]
percips = [
    int(parsed_json["forecastHourly"]["hours"][x]["precipitationChance"] * 100)
    for x in range(1, 13)
]
cond_icons = [(parsed_json["forecastHourly"]["hours"][x]["conditionCode"]) for x in range(1, 13)]

# Insert icons and temperatures
h = 1
for v in hours:
    output = output.replace("H_" + str(h) + "_", str(v))
    h += 1
h = 1
for v in temps:
    output = output.replace("TEMP_" + str(h) + "_", str(v))
    h += 1
h = 1
for v in winds:
    output = output.replace("WINDSPEED_" + str(h) + "_", str(v))
    h += 1
h = 1
for v in winds_degs:
    output = output.replace("HOUR_" + str(h) + "_WIND_DEGS", str(v))
    h += 1
h = 1
for v in humids:
    output = output.replace("HUMID_" + str(h) + "_", str(v))
    h += 1
h = 1
for v in percips:
    output = output.replace("PERC_" + str(h) + "_", str(v))
    h += 1


# Grab the icon for the condition
h = 1
for v in cond_icons:
    CURR_COND_ICON_url = iconMap(v, True)
    if os.path.isfile(CURR_COND_ICON_url):
        fIcon = codecs.open(CURR_COND_ICON_url, "r", encoding="utf-8")
        fIcon.readline()
        icon = fIcon.readline()
        fIcon.close()
    else:
        fIcon = codecs.open("weather-icons/unknown.svg", "r", encoding="utf-8")
        fIcon.readline()
        icon = fIcon.readline()
        fIcon.close()
    output = output.replace("HOUR_" + str(h) + "_COND_ICON", icon)
    h += 1

# Add transit information
output = addTransit(output)

output = output.replace("DISP_CURR", hide)
output = output.replace("DISP5DAY", hide)
output = output.replace("DISP12HOUR", show)

# Write output
codecs.open("weather-script-output-hourly.svg", "w", encoding="utf-8").write(output)


########## daily ###########
# Open SVG to process
output = codecs.open("weather-transit-preprocess.svg", "r", encoding="utf-8").read()

# establish display variables:
show = "inline"
hide = "none"

### Deal with the hourly file
# check the currenConditions file to see if it's older than 5 minutes
# if fileChecker("localData/hourly.json", 3600) == "create":
#     weatherGrabber(type="hourly", path="localData/hourly.json")
# fCurrCond = open("localData/hourly.json",'r')
fCurrCond = open("localData/currentConditions.json", "r")

# read the file
json_string = fCurrCond.read()
parsed_json = json.loads(json_string)
fCurrCond.close()


# parse out the dynamic variables weatherKit

days = [
    datetime.datetime.fromisoformat(
        parsed_json["forecastDaily"]["days"][x]["forecastStart"].replace(
            "Z", "+00:00"
        )
    ).astimezone(tz=ZoneInfo(privateVars.local_tz)).strftime('%A')
    for x in range(0, 5)
]
hitemps = [
    int(round(celsius_to_fahrenheit(parsed_json["forecastDaily"]["days"][x]["temperatureMax"])))
    for x in range(0, 5)
]
lotemps = [
    int(round(celsius_to_fahrenheit(parsed_json["forecastDaily"]["days"][x]["temperatureMin"])))
    for x in range(0, 5)
]
cond_icons = [(parsed_json["forecastDaily"]["days"][x]["conditionCode"]) for x in range(0, 5)]

# Insert icons and temperatures
h = 1
for v in days:
    output = output.replace("DAY_" + str(h) + "_", str(v))
    h += 1
h = 1
for v in hitemps:
    output = output.replace("TEMP_HI_" + str(h) + "_", str(v))
    h += 1
h = 1
for v in lotemps:
    output = output.replace("TEMP_LO_" + str(h) + "_", str(v))
    h += 1


# Grab the icon for the condition
h = 1
for v in cond_icons:
    CURR_COND_ICON_url = iconMap(v, True)
    if os.path.isfile(CURR_COND_ICON_url):
        fIcon = codecs.open(CURR_COND_ICON_url, "r", encoding="utf-8")
        fIcon.readline()
        icon = fIcon.readline()
        fIcon.close()
    else:
        fIcon = codecs.open("weather-icons/unknown.svg", "r", encoding="utf-8")
        fIcon.readline()
        icon = fIcon.readline()
        fIcon.close()
    output = output.replace("DAY_COND_ICON_" + str(h), icon)
    h += 1

# Add transit information
output = addTransit(output)

output = output.replace("DISP_CURR", hide)
output = output.replace("DISP5DAY", show)
output = output.replace("DISP12HOUR", hide)

# Write output
codecs.open("weather-script-output-daily.svg", "w", encoding="utf-8").write(output)
