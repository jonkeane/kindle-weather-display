import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from constants import SERVER_DIR


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


def iconMap(condition, daylight, icons_dir="weather-icons"):
    out = WEATHER_ICON_MAP[condition]
    icons_dir = Path(icons_dir)

    if daylight is False and (icons_dir / "night" / out).is_file():
        out = Path("night") / out

    return str(icons_dir / out)


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


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
                "hour": _parse_forecast_start(hour["forecastStart"], local_tz).hour,
                "temperature": int(round(celsius_to_fahrenheit(hour["temperature"]))),
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
        output = output.replace("TEMP_" + str(index) + "_", str(hour["temperature"]))
        output = output.replace(
            "WINDSPEED_" + str(index) + "_", str(hour["wind_speed"])
        )
        output = output.replace(
            "HOUR_" + str(index) + "_WIND_DEGS",
            str(hour["wind_direction"]),
        )
        output = output.replace("HUMID_" + str(index) + "_", str(hour["humidity"]))
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
