import json
from pathlib import Path

import pytest

from weather_transit import AppConfig


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = REPO_ROOT / "server"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def server_dir():
    return SERVER_DIR


@pytest.fixture
def weather_data(fixtures_dir):
    return json.loads((fixtures_dir / "currentConditions.json").read_text())


@pytest.fixture
def sample_config():
    return AppConfig(
        wunderground_api_key="wunderground-token",
        weather_kit_token="weather-token",
        cta_api_key="bus-token",
        cta_train_api_key="train-token",
        zip_code="60613",
        lat="41.95",
        lng="-87.66",
        local_tz="America/Chicago",
        buses_to_track={
            "sb22": "stop-sb22",
            "nb22": "stop-nb22",
            "wb152": "stop-wb152",
            "eb152": "stop-eb152",
            "sb9": "stop-sb9",
            "nb9": "stop-nb9",
        },
        trains_to_track={
            "sbred": "stop-sbred",
            "nbred": "stop-nbred",
            "sbbrn": "stop-sbbrn",
            "nbbrn": "stop-nbbrn",
        },
        bus_places={
            "red": "BUS1",
            "brn": "BUS2",
            "22": "BUS3",
            "152": "BUS4",
            "9": "BUS5",
        },
    )
