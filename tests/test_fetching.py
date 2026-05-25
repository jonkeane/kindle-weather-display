import datetime
from zoneinfo import ZoneInfo

import fetching


class FakeResponse:
    def __init__(self, text):
        self.text = text
        self.closed = False

    def close(self):
        self.closed = True


def test_weather_grabber_writes_mocked_weatherkit_response(tmp_path):
    calls = []
    response = FakeResponse("weather payload")

    def fake_get(url, headers=None):
        calls.append({"url": url, "headers": headers})
        return response

    output_path = tmp_path / "currentConditions.json"
    fetching.weatherGrabber(
        path=output_path,
        apiKey="test-token",
        lat="41.95",
        lng="-87.66",
        local_tz="America/Chicago",
        now=datetime.datetime(2026, 5, 25, 12, 0, tzinfo=ZoneInfo("UTC")),
        request_get=fake_get,
    )

    assert output_path.read_text(encoding="utf-8") == "weather payload"
    assert response.closed is True
    assert calls[0]["headers"] == {"Authorization": "Bearer test-token"}
    assert "weatherkit.apple.com/api/v1/weather/en/41.95/-87.66" in calls[0]["url"]
    assert "timezone=America/Chicago" in calls[0]["url"]
    assert "hourlyStart=2026-05-25T12:00:00Z" in calls[0]["url"]


def test_cta_bus_grabber_writes_mocked_response(tmp_path):
    calls = []

    def fake_get(url, headers=None):
        calls.append(url)
        return FakeResponse("<bus />")

    output_path = tmp_path / "busPredictions.xml"
    fetching.ctaPredGrabber(
        ["12558", "12559"],
        output_path,
        apiKey="bus-token",
        request_get=fake_get,
    )

    assert output_path.read_text(encoding="utf-8") == "<bus />"
    assert calls == [
        "https://www.ctabustracker.com/bustime/api/v3/getpredictions?"
        "key=bus-token&stpid=12558,12559"
    ]


def test_cta_train_grabber_writes_mocked_response(tmp_path):
    calls = []

    def fake_get(url, headers=None):
        calls.append(url)
        return FakeResponse("<train />")

    output_path = tmp_path / "trainPredictions.xml"
    fetching.ctaTrainPredGrabber(
        ["30070", "30071"],
        output_path,
        apiKey="train-token",
        request_get=fake_get,
    )

    assert output_path.read_text(encoding="utf-8") == "<train />"
    assert calls == [
        "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?"
        "key=train-token&stpid=30070,30071"
    ]
