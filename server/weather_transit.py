#!/usr/bin/python3

# Kindle Transit-Weather Display
# Inspired by Matthew Petroff (http://www.mpetroff.net/)
# November 2013

from dataclasses import dataclass
import datetime
import importlib
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

try:
    import requests
except ImportError:  # pragma: no cover - fetch paths raise a clearer error.
    requests = None


SERVER_DIR = Path(__file__).resolve().parent
SHOW = "inline"
HIDE = "none"

BOUNDS = {
    "Northbound": "nb",
    "Southbound": "sb",
    "Eastbound": "eb",
    "Westbound": "wb",
    "NORTH": "nb",
    "SOUTH": "sb",
    "EAST": "eb",
    "WEST": "wb",
}

TRAIN_STOP_IDS_TO_BOUNDS = {
    "30274": "sb",
    "30273": "nb",
    "30071": "sb",
    "30070": "nb",
}

WEATHER_ICON_MAP = {
    "Clear": "clear.svg",
    "Rain": "rain.svg",
    "Snow": "snow.svg",
    "Sleet": "sleet.svg",
    "Windy": "wind.svg",
    "Fog": "fog.svg",
    "Dust": "fog.svg",
    "Haze": "hazy.svg",
    "Cloudy": "cloudy.svg",
    "MostlyClear": "mostlysunny.svg",
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
    "Thunderstorms": "tstorms.svg",
    "Tornado": "tstorms.svg",
    "TropicalStorm": "tstorms.svg",
}


@dataclass(frozen=True)
class AppConfig:
    wunderground_api_key: str
    weather_kit_token: str
    cta_api_key: str
    cta_train_api_key: str
    zip_code: str
    lat: object
    lng: object
    local_tz: str
    buses_to_track: dict
    trains_to_track: dict
    bus_places: dict


def _load_private_vars():
    return importlib.import_module("privateVars")


def load_config(private_vars=None):
    if private_vars is None:
        private_vars = _load_private_vars()

    return AppConfig(
        wunderground_api_key=private_vars.wundergroundAPIkey,
        weather_kit_token=private_vars.weatherKitToken,
        cta_api_key=private_vars.ctaAPIkey,
        cta_train_api_key=private_vars.ctaTrainAPIkey,
        zip_code=private_vars.zipCode,
        lat=private_vars.lat,
        lng=private_vars.lng,
        local_tz=private_vars.local_tz,
        buses_to_track=dict(private_vars.busesToTrack),
        trains_to_track=dict(private_vars.trainsToTrack),
        bus_places=dict(private_vars.busPlaces),
    )


def _requests_get(request_get=None):
    if request_get is not None:
        return request_get
    if requests is None:
        raise RuntimeError("The requests package is required to fetch live API data.")
    return requests.get


def _write_response_text(response, path):
    Path(path).write_text(response.text, encoding="utf-8")
    if hasattr(response, "close"):
        response.close()


def current_local_datetime():
    return datetime.datetime.fromtimestamp(time.mktime(time.localtime()))


def iconMap(condition, daylight, icons_dir="weather-icons"):
    out = WEATHER_ICON_MAP[condition]
    icons_dir = Path(icons_dir)

    if daylight is False and (icons_dir / "night" / out).is_file():
        out = Path("night") / out

    return str(icons_dir / out)


def fileChecker(path, refreshInterval, now=None):
    path = Path(path)
    if not path.is_file():
        return "create"

    if now is None:
        now_timestamp = time.time()
    elif isinstance(now, datetime.datetime):
        now_timestamp = now.timestamp()
    else:
        now_timestamp = float(now)

    if now_timestamp - path.stat().st_mtime > refreshInterval:
        return "create"
    return "useOld"


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


def weatherGrabber(
    type,
    path,
    source="weatherKit",
    apiKey=None,
    zipCode=None,
    lat=None,
    lng=None,
    local_tz=None,
    now=None,
    request_get=None,
):
    config = None
    get = _requests_get(request_get)

    if source == "wunderground":
        if apiKey is None or zipCode is None:
            config = load_config()
        apiKey = apiKey if apiKey is not None else config.wunderground_api_key
        zipCode = zipCode if zipCode is not None else config.zip_code
        response = get(
            "http://api.wunderground.com/api/"
            + apiKey
            + "/geolookup/"
            + type
            + "/q/"
            + zipCode
            + ".json"
        )
    elif source == "weatherKit":
        if apiKey is None or lat is None or lng is None or local_tz is None:
            config = load_config()
        apiKey = apiKey if apiKey is not None else config.weather_kit_token
        lat = lat if lat is not None else config.lat
        lng = lng if lng is not None else config.lng
        local_tz = local_tz if local_tz is not None else config.local_tz

        if now is None:
            now = datetime.datetime.now().astimezone(tz=ZoneInfo("UTC"))
        elif now.tzinfo is None:
            now = now.replace(tzinfo=ZoneInfo("UTC"))
        else:
            now = now.astimezone(tz=ZoneInfo("UTC"))

        hourly_start = now.isoformat().replace("+00:00", "Z")
        response = get(
            f"https://weatherkit.apple.com/api/v1/weather/en/{lat}/{lng}?"
            + "dataSets=currentWeather,forecastDaily,forecastHourly,forecastNextHour"
            + f"&timezone={local_tz}"
            + f"&hourlyStart={hourly_start}",
            headers={"Authorization": f"Bearer {apiKey}"},
        )
    else:
        raise ValueError(f"Unknown weather source: {source}")

    _write_response_text(response, path)


def ctaPredGrabber(stopIDs, path, apiKey=None, request_get=None):
    if apiKey is None:
        apiKey = load_config().cta_api_key
    if isinstance(stopIDs, str):
        stopIDs = [stopIDs]

    get = _requests_get(request_get)
    response = get(
        "http://www.ctabustracker.com/bustime/api/v1/getpredictions?key="
        + apiKey
        + "&stpid="
        + ",".join(str(stopID) for stopID in stopIDs)
    )
    _write_response_text(response, path)


def ctaTrainPredGrabber(stopIDs, path, apiKey=None, request_get=None):
    if apiKey is None:
        apiKey = load_config().cta_train_api_key
    if isinstance(stopIDs, str):
        stopIDs = [stopIDs]

    get = _requests_get(request_get)
    response = get(
        "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key="
        + apiKey
        + "&stpid="
        + ",".join(str(stopID) for stopID in stopIDs)
    )
    _write_response_text(response, path)


def _weather_json(data):
    if isinstance(data, (str, bytes)):
        return json.loads(data)
    return data


def parse_current_weather(data):
    data = _weather_json(data)
    current = data["currentWeather"]

    return {
        "temperature": int(round(celsius_to_fahrenheit(current["temperature"]))),
        "feels_like": int(
            round(celsius_to_fahrenheit(current["temperatureApparent"]))
        ),
        "wind_speed": int(round(current["windSpeed"])),
        "wind_direction": current["windDirection"],
        "humidity": int(current["humidity"] * 100),
        "condition_code": current["conditionCode"],
        "daylight": current["daylight"],
    }


def _parse_forecast_start(value, local_tz):
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        tz=ZoneInfo(local_tz)
    )


def parse_hourly_forecast(data, local_tz, start_index=1, count=12):
    data = _weather_json(data)
    hours = data["forecastHourly"]["hours"]

    forecast = []
    for index in range(start_index, start_index + count):
        hour = hours[index]
        forecast.append(
            {
                "hour": _parse_forecast_start(
                    hour["forecastStart"], local_tz
                ).hour,
                "temperature": int(
                    round(celsius_to_fahrenheit(hour["temperature"]))
                ),
                "wind_speed": int(round(hour["windSpeed"])),
                "wind_direction": int(hour["windDirection"]),
                "humidity": int(hour["humidity"] * 100),
                "precipitation_chance": int(hour["precipitationChance"] * 100),
                "condition_code": hour["conditionCode"],
            }
        )

    return forecast


def parse_daily_forecast(data, local_tz, count=5):
    data = _weather_json(data)
    days = data["forecastDaily"]["days"]

    forecast = []
    for index in range(count):
        day = days[index]
        forecast.append(
            {
                "day": _parse_forecast_start(
                    day["forecastStart"], local_tz
                ).strftime("%A"),
                "high": int(round(celsius_to_fahrenheit(day["temperatureMax"]))),
                "low": int(round(celsius_to_fahrenheit(day["temperatureMin"]))),
                "condition_code": day["conditionCode"],
            }
        )

    return forecast


def _xml_root(source):
    if isinstance(source, ET.Element):
        return source
    if hasattr(source, "read"):
        return ET.parse(source).getroot()
    if isinstance(source, bytes):
        return ET.fromstring(source)
    if isinstance(source, str) and source.lstrip().startswith("<"):
        return ET.fromstring(source)
    return ET.parse(source).getroot()


def _find_text(element, tag):
    child = element.find(tag)
    if child is None:
        return None
    return child.text


def parse_transit_predictions(
    bus_xml,
    train_xml,
    buses_to_track,
    trains_to_track,
    now=None,
    train_stop_ids_to_bounds=None,
):
    if now is None:
        now = current_local_datetime()
    if now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    train_stop_ids_to_bounds = train_stop_ids_to_bounds or TRAIN_STOP_IDS_TO_BOUNDS

    things_to_track = list(buses_to_track.keys()) + list(trains_to_track.keys())
    raw_predictions = {route: [] for route in things_to_track}
    arrivals = {route: [] for route in things_to_track}
    seen_vehicle_times = set()

    for prediction in _xml_root(bus_xml):
        if prediction.tag != "prd":
            continue

        direction = _find_text(prediction, "rtdir")
        route_number = _find_text(prediction, "rt")
        vehicle_id = _find_text(prediction, "vid")
        predicted_time = _find_text(prediction, "prdtm")
        if None in (direction, route_number, vehicle_id, predicted_time):
            continue

        bound = BOUNDS.get(direction)
        if bound is None:
            continue

        duplicate_key = "".join([bound, route_number, vehicle_id, predicted_time])
        if duplicate_key in seen_vehicle_times:
            continue
        seen_vehicle_times.add(duplicate_key)

        route = "".join([bound, route_number])
        if route in raw_predictions:
            raw_predictions[route].append(predicted_time)

    for prediction in _xml_root(train_xml):
        if prediction.tag != "eta":
            continue

        stop_id = _find_text(prediction, "stpId")
        route_name = _find_text(prediction, "rt")
        run_number = _find_text(prediction, "rn")
        arrival_time = _find_text(prediction, "arrT")
        if None in (stop_id, route_name, run_number, arrival_time):
            continue

        bound = train_stop_ids_to_bounds.get(stop_id)
        if bound is None:
            continue

        duplicate_key = "".join([bound, route_name, run_number, arrival_time])
        if duplicate_key in seen_vehicle_times:
            continue
        seen_vehicle_times.add(duplicate_key)

        route = "".join([bound, route_name]).lower()
        if route in raw_predictions:
            raw_predictions[route].append(arrival_time)

    for route, predictions in raw_predictions.items():
        for predicted_time in predictions:
            if len(predicted_time) == 14:
                arrival = datetime.datetime.strptime(
                    predicted_time, "%Y%m%d %H:%M"
                ) - now
                arrival = arrival - datetime.timedelta(seconds=60)
            elif len(predicted_time) == 17:
                arrival = datetime.datetime.strptime(
                    predicted_time, "%Y%m%d %H:%M:%S"
                ) - now
            else:
                continue

            if arrival > datetime.timedelta(seconds=60):
                arrivals[route].append(str(arrival).split(":")[1])

    return arrivals


def _format_arrival_for_display(arrival):
    if arrival == "00":
        return "0"
    if arrival.startswith("0"):
        return arrival[1:]
    return arrival


def render_transit(output, arrivals, bus_places, now=None):
    if now is None:
        now = current_local_datetime()
    if now.tzinfo is not None:
        now = now.replace(tzinfo=None)

    for route, route_arrivals in arrivals.items():
        bus_place = bus_places[route[2:]]
        if route[:2] == "nb" or route[:2] == "wb":
            bus_place = bus_place + "_D"
        else:
            bus_place = bus_place + "_U"

        for index in range(3):
            placeholder = bus_place + str(index + 1)
            display_placeholder = placeholder + "_DISP"
            try:
                arrival = _format_arrival_for_display(route_arrivals[index])
                output = output.replace(display_placeholder, SHOW)
                output = output.replace(placeholder, arrival)
            except IndexError:
                output = output.replace(display_placeholder, HIDE)
                output = output.replace(placeholder, "")

    display_time = (now + datetime.timedelta(seconds=60)).strftime("%H:%M")
    output = output.replace("TIME", display_time)
    output = output.replace("DISP_TRANSIT", SHOW)
    return output


def addTransit(output, paths=None, config=None, now=None):
    if paths is None:
        paths = ["localData/busPredictions.xml", "localData/trainPredictions.xml"]
    if config is None:
        config = load_config()

    arrivals = parse_transit_predictions(
        paths[0],
        paths[1],
        config.buses_to_track,
        config.trains_to_track,
        now=now,
    )
    return render_transit(output, arrivals, config.bus_places, now=now)


def _read_icon_line(condition, daylight, base_dir):
    icon_path = Path(
        iconMap(condition, daylight, icons_dir=Path(base_dir) / "weather-icons")
    )
    if not icon_path.is_file():
        icon_path = Path(base_dir) / "weather-icons" / "unknown.svg"

    with icon_path.open("r", encoding="utf-8") as icon_file:
        icon_file.readline()
        return icon_file.readline()


def render_current_weather(output, current_weather, base_dir=SERVER_DIR):
    output = output.replace("CURRTEMP", str(current_weather["temperature"]))
    output = output.replace("CURRFEELS", str(current_weather["feels_like"]))
    output = output.replace("CURRWIND", str(current_weather["wind_speed"]))
    output = output.replace("CURRHUM", str(current_weather["humidity"]))
    output = output.replace("WIND_DEGS", str(current_weather["wind_direction"]))
    output = output.replace(
        "CURR_COND_ICON",
        _read_icon_line(
            current_weather["condition_code"],
            current_weather["daylight"],
            base_dir,
        ),
    )
    return output


def render_hourly_forecast(output, hourly_forecast, base_dir=SERVER_DIR):
    for index, hour in enumerate(hourly_forecast, start=1):
        output = output.replace("H_" + str(index) + "_", str(hour["hour"]))
        output = output.replace(
            "TEMP_" + str(index) + "_", str(hour["temperature"])
        )
        output = output.replace(
            "WINDSPEED_" + str(index) + "_", str(hour["wind_speed"])
        )
        output = output.replace(
            "HOUR_" + str(index) + "_WIND_DEGS",
            str(hour["wind_direction"]),
        )
        output = output.replace(
            "HUMID_" + str(index) + "_", str(hour["humidity"])
        )
        output = output.replace(
            "PERC_" + str(index) + "_", str(hour["precipitation_chance"])
        )
        output = output.replace(
            "HOUR_" + str(index) + "_COND_ICON",
            _read_icon_line(hour["condition_code"], True, base_dir),
        )
    return output


def render_daily_forecast(output, daily_forecast, base_dir=SERVER_DIR):
    for index, day in enumerate(daily_forecast, start=1):
        output = output.replace("DAY_" + str(index) + "_", str(day["day"]))
        output = output.replace("TEMP_HI_" + str(index) + "_", str(day["high"]))
        output = output.replace("TEMP_LO_" + str(index) + "_", str(day["low"]))
        output = output.replace(
            "DAY_COND_ICON_" + str(index),
            _read_icon_line(day["condition_code"], True, base_dir),
        )
    return output


def apply_view_visibility(output, active_view):
    return (
        output.replace("DISP_CURR", SHOW if active_view == "current" else HIDE)
        .replace("DISP5DAY", SHOW if active_view == "daily" else HIDE)
        .replace("DISP12HOUR", SHOW if active_view == "hourly" else HIDE)
    )


def build_current_output(
    weather_data,
    template,
    config,
    transit_paths,
    now=None,
    base_dir=SERVER_DIR,
):
    output = render_current_weather(template, parse_current_weather(weather_data), base_dir)
    output = addTransit(output, paths=transit_paths, config=config, now=now)
    return apply_view_visibility(output, "current")


def build_hourly_output(
    weather_data,
    template,
    config,
    transit_paths,
    now=None,
    base_dir=SERVER_DIR,
):
    hourly = parse_hourly_forecast(weather_data, config.local_tz)
    output = render_hourly_forecast(template, hourly, base_dir)
    output = addTransit(output, paths=transit_paths, config=config, now=now)
    return apply_view_visibility(output, "hourly")


def build_daily_output(
    weather_data,
    template,
    config,
    transit_paths,
    now=None,
    base_dir=SERVER_DIR,
):
    daily = parse_daily_forecast(weather_data, config.local_tz)
    output = render_daily_forecast(template, daily, base_dir)
    output = addTransit(output, paths=transit_paths, config=config, now=now)
    return apply_view_visibility(output, "daily")


def main(base_dir=SERVER_DIR, now=None, request_get=None):
    base_dir = Path(base_dir)
    local_data_dir = base_dir / "localData"
    local_data_dir.mkdir(exist_ok=True)
    bus_predictions_path = local_data_dir / "busPredictions.xml"
    train_predictions_path = local_data_dir / "trainPredictions.xml"
    current_conditions_path = local_data_dir / "currentConditions.json"
    template_path = base_dir / "weather-transit-preprocess.svg"
    render_now = now or current_local_datetime()
    config = load_config()

    if fileChecker(bus_predictions_path, 5) == "create":
        ctaPredGrabber(
            stopIDs=config.buses_to_track.values(),
            path=bus_predictions_path,
            apiKey=config.cta_api_key,
            request_get=request_get,
        )

    if fileChecker(train_predictions_path, 5) == "create":
        ctaTrainPredGrabber(
            stopIDs=config.trains_to_track.values(),
            path=train_predictions_path,
            apiKey=config.cta_train_api_key,
            request_get=request_get,
        )

    if fileChecker(current_conditions_path, 300) == "create":
        weatherGrabber(
            type="conditions",
            path=current_conditions_path,
            apiKey=config.weather_kit_token,
            lat=config.lat,
            lng=config.lng,
            local_tz=config.local_tz,
            request_get=request_get,
        )

    weather_data = json.loads(current_conditions_path.read_text(encoding="utf-8"))
    template = template_path.read_text(encoding="utf-8")
    transit_paths = [bus_predictions_path, train_predictions_path]

    (base_dir / "weather-script-output-current.svg").write_text(
        build_current_output(
            weather_data,
            template,
            config,
            transit_paths,
            now=render_now,
            base_dir=base_dir,
        ),
        encoding="utf-8",
    )
    (base_dir / "weather-script-output-hourly.svg").write_text(
        build_hourly_output(
            weather_data,
            template,
            config,
            transit_paths,
            now=render_now,
            base_dir=base_dir,
        ),
        encoding="utf-8",
    )
    (base_dir / "weather-script-output-daily.svg").write_text(
        build_daily_output(
            weather_data,
            template,
            config,
            transit_paths,
            now=render_now,
            base_dir=base_dir,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
