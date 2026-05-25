#!/usr/bin/python3

# Kindle Transit-Weather Display
# Inspired by Matthew Petroff (http://www.mpetroff.net/)
# November 2013

import json
from pathlib import Path

from config import AppConfig, load_config
from constants import HIDE, SERVER_DIR, SHOW
from fetching import ctaPredGrabber, ctaTrainPredGrabber, weatherGrabber
from rendering import (
    apply_view_visibility,
    build_current_output,
    build_daily_output,
    build_hourly_output,
)
from transit import (
    BOUNDS,
    TRAIN_STOP_IDS_TO_BOUNDS,
    addTransit,
    parse_transit_predictions,
    render_transit,
)
from utils import current_local_datetime, fileChecker
from weather import (
    WEATHER_ICON_MAP,
    _read_icon_line,
    celsius_to_fahrenheit,
    iconMap,
    parse_current_weather,
    parse_daily_forecast,
    parse_hourly_forecast,
    render_current_weather,
    render_daily_forecast,
    render_hourly_forecast,
)


def main(base_dir=SERVER_DIR, now=None, request_get=None):
    base_dir = Path(base_dir)
    local_data_dir = base_dir / "localData"
    local_data_dir.mkdir(exist_ok=True)
    output_data_dir = base_dir / "outputData"
    output_data_dir.mkdir(exist_ok=True)
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

    (output_data_dir / "weather-script-output-current.svg").write_text(
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
    (output_data_dir / "weather-script-output-hourly.svg").write_text(
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
    (output_data_dir / "weather-script-output-daily.svg").write_text(
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
