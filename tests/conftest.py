import json
import os
from pathlib import Path

import pytest

from weather_transit import AppConfig


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = REPO_ROOT / "server"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def pytest_configure(config):
    # Keep tests independent of any developer-local .env values.
    os.environ.update(
        {
            "WUNDERGROUND_API_KEY": "test-wunderground-token",
            "WEATHERKIT_TOKEN": "test-weatherkit-token",
            "CTA_API_KEY": "test-cta-bus-token",
            "CTA_TRAIN_API_KEY": "test-cta-train-token",
            "ZIP_CODE": "60657",
            "LAT": "41.9721",
            "LNG": "-87.6890",
            "LOCAL_TZ": "America/Chicago",
            "BUSES_TO_TRACK_JSON": json.dumps(
                {
                    "sb36": "test-stop-sb22-a",
                    "nb36": "test-stop-nb22-a",
                    "wb80": "test-stop-wb152-a",
                    "eb80": "test-stop-eb152-a",
                    "sb81": "test-stop-sb9-a",
                    "nb81": "test-stop-nb9-a",
                }
            ),
            "TRAINS_TO_TRACK_JSON": json.dumps(
                {
                    "sbcyn": "test-stop-sbred-a",
                    "nbcyn": "test-stop-nbred-a",
                    "sbsep": "test-stop-sbbrn-a",
                    "nbsep": "test-stop-nbbrn-a",
                }
            ),
            "BUS_PLACES_JSON": json.dumps(
                {
                    "cyn": "BUS1",
                    "sep": "BUS2",
                    "36": "BUS3",
                    "80": "BUS4",
                    "81": "BUS5",
                }
            ),
        }
    )


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
        zip_code="60657",
        lat="41.9721",
        lng="-87.6890",
        local_tz="America/Chicago",
        buses_to_track={
            "sb36": "test-stop-sb22-a",
            "nb36": "test-stop-nb22-a",
            "wb80": "test-stop-wb152-a",
            "eb80": "test-stop-eb152-a",
            "sb81": "test-stop-sb9-a",
            "nb81": "test-stop-nb9-a",
        },
        trains_to_track={
            "sbcyn": "test-stop-sbred-a",
            "nbcyn": "test-stop-nbred-a",
            "sbsep": "test-stop-sbbrn-a",
            "nbsep": "test-stop-nbbrn-a",
        },
        bus_places={
            "cyn": "BUS1",
            "sep": "BUS2",
            "36": "BUS3",
            "80": "BUS4",
            "81": "BUS5",
        },
    )
