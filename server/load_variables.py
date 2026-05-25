#!/usr/bin/python3

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency for env loading.
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def _required_env_str(name):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _required_env_float(name):
    value = _required_env_str(name)
    try:
        return float(value)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be a float, got: {value!r}"
        ) from exc


def _required_env_json(name):
    value = _required_env_str(name)
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be valid JSON: {exc.msg}"
        ) from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(
            f"Environment variable {name} must decode to a JSON object"
        )
    return parsed


weatherKitToken = _required_env_str("WEATHERKIT_TOKEN")
ctaAPIkey = _required_env_str("CTA_API_KEY")
ctaTrainAPIkey = _required_env_str("CTA_TRAIN_API_KEY")

lat = _required_env_float("LAT")
lng = _required_env_float("LNG")
local_tz = _required_env_str("LOCAL_TZ")


busesToTrack = _required_env_json("BUSES_TO_TRACK_JSON")

trainsToTrack = _required_env_json("TRAINS_TO_TRACK_JSON")

busPlaces = _required_env_json("BUS_PLACES_JSON")
