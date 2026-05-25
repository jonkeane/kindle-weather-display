from constants import HIDE, SERVER_DIR, SHOW
from transit import addTransit
from weather import (
    parse_current_weather,
    parse_daily_forecast,
    parse_hourly_forecast,
    render_current_weather,
    render_daily_forecast,
    render_hourly_forecast,
)


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
    current_weather = parse_current_weather(weather_data)
    output = render_current_weather(template, current_weather, base_dir)
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
