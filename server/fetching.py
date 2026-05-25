import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import load_config

try:
    import requests
except ImportError:  # pragma: no cover - fetch paths raise a clearer error.
    requests = None


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


def weatherGrabber(
    path,
    apiKey=None,
    lat=None,
    lng=None,
    local_tz=None,
    now=None,
    request_get=None,
):
    if apiKey is None or lat is None or lng is None or local_tz is None:
        config = load_config()
    else:
        config = None

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
    get = _requests_get(request_get)
    response = get(
        f"https://weatherkit.apple.com/api/v1/weather/en/{lat}/{lng}?"
        + "dataSets=currentWeather,forecastDaily,forecastHourly,forecastNextHour"
        + f"&timezone={local_tz}"
        + f"&hourlyStart={hourly_start}",
        headers={"Authorization": f"Bearer {apiKey}"},
    )
    _write_response_text(response, path)


def ctaPredGrabber(stopIDs, path, apiKey=None, request_get=None):
    if apiKey is None:
        apiKey = load_config().cta_api_key
    if isinstance(stopIDs, str):
        stopIDs = [stopIDs]

    get = _requests_get(request_get)
    response = get(
        "https://www.ctabustracker.com/bustime/api/v3/getpredictions?key="
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
