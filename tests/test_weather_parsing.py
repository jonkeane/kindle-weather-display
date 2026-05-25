import datetime
import os

import utils
import weather


def test_celsius_to_fahrenheit():
    assert weather.celsius_to_fahrenheit(0) == 32
    assert weather.celsius_to_fahrenheit(100) == 212


def test_icon_map_uses_night_icon_when_available(server_dir):
    day_icon = weather.iconMap(
        "Clear", True, icons_dir=server_dir / "weather-icons"
    )
    night_icon = weather.iconMap(
        "Clear", False, icons_dir=server_dir / "weather-icons"
    )

    assert day_icon.endswith("clear.svg")
    assert "night" not in day_icon
    assert night_icon.endswith("night/clear.svg")


def test_file_checker_create_and_use_old(tmp_path):
    missing_path = tmp_path / "missing.json"
    assert utils.fileChecker(missing_path, 5) == "create"

    cached_path = tmp_path / "cached.json"
    cached_path.write_text("{}", encoding="utf-8")
    now = datetime.datetime.fromtimestamp(1_000)

    old_timestamp = 990
    os.utime(cached_path, (old_timestamp, old_timestamp))
    assert utils.fileChecker(cached_path, 5, now=now) == "create"

    fresh_timestamp = 998
    os.utime(cached_path, (fresh_timestamp, fresh_timestamp))
    assert utils.fileChecker(cached_path, 5, now=now) == "useOld"


def test_parse_current_weather(weather_data):
    current = weather.parse_current_weather(weather_data)

    assert current == {
        "temperature": 62,
        "feels_like": 64,
        "wind_speed": 8,
        "wind_direction": 201,
        "humidity": 76,
        "condition_code": "MostlyClear",
        "daylight": True,
    }


def test_parse_hourly_forecast(weather_data):
    hourly = weather.parse_hourly_forecast(
        weather_data, local_tz="America/Chicago"
    )

    assert len(hourly) == 12
    assert hourly[0] == {
        "hour": 8,
        "temperature": 62,
        "wind_speed": 9,
        "wind_direction": 201,
        "humidity": 76,
        "precipitation_chance": 0,
        "condition_code": "Clear",
    }
    assert hourly[-1] == {
        "hour": 19,
        "temperature": 76,
        "wind_speed": 11,
        "wind_direction": 153,
        "humidity": 48,
        "precipitation_chance": 0,
        "condition_code": "Clear",
    }


def test_parse_daily_forecast(weather_data):
    daily = weather.parse_daily_forecast(
        weather_data, local_tz="America/Chicago"
    )

    assert [day["day"] for day in daily] == [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
    ]
    assert daily[0] == {
        "day": "Monday",
        "high": 80,
        "low": 58,
        "condition_code": "Clear",
    }
    assert daily[-1] == {
        "day": "Friday",
        "high": 74,
        "low": 53,
        "condition_code": "MostlyClear",
    }
