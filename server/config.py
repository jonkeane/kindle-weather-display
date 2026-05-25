from dataclasses import dataclass
import importlib


@dataclass(frozen=True)
class AppConfig:
    weather_kit_token: str
    cta_api_key: str
    cta_train_api_key: str
    lat: object
    lng: object
    local_tz: str
    buses_to_track: dict
    trains_to_track: dict
    bus_places: dict


def _load_variables():
    return importlib.import_module("load_variables")


def load_config(variables=None):
    if variables is None:
        variables = _load_variables()

    return AppConfig(
        weather_kit_token=variables.weatherKitToken,
        cta_api_key=variables.ctaAPIkey,
        cta_train_api_key=variables.ctaTrainAPIkey,
        lat=variables.lat,
        lng=variables.lng,
        local_tz=variables.local_tz,
        buses_to_track=dict(variables.busesToTrack),
        trains_to_track=dict(variables.trainsToTrack),
        bus_places=dict(variables.busPlaces),
    )
