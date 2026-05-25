import json
from pathlib import Path

import weather_transit
import weather


def test_main_creates_local_data_directory(
    monkeypatch, tmp_path, server_dir, sample_config, weather_data
):
    app_dir = tmp_path / "server"
    app_dir.mkdir()
    (app_dir / "weather-transit-preprocess.svg").write_text(
        (server_dir / "weather-transit-preprocess.svg").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    local_data_dir = app_dir / "localData"
    output_data_dir = app_dir / "outputData"
    bus_payload = (
        Path(__file__).parent / "fixtures" / "busPredictions.xml"
    ).read_text(encoding="utf-8")
    train_payload = (
        Path(__file__).parent / "fixtures" / "trainPredictions.xml"
    ).read_text(encoding="utf-8")

    def fake_file_checker(path, refresh_interval):
        return "create"

    def fake_cta_pred_grabber(stopIDs, path, apiKey=None, request_get=None):
        Path(path).write_text(bus_payload, encoding="utf-8")

    def fake_cta_train_pred_grabber(stopIDs, path, apiKey=None, request_get=None):
        Path(path).write_text(train_payload, encoding="utf-8")

    def fake_weather_grabber(**kwargs):
        Path(kwargs["path"]).write_text(json.dumps(weather_data), encoding="utf-8")

    monkeypatch.setattr(weather_transit, "load_config", lambda: sample_config)
    monkeypatch.setattr(weather_transit, "fileChecker", fake_file_checker)
    monkeypatch.setattr(weather_transit, "ctaPredGrabber", fake_cta_pred_grabber)
    monkeypatch.setattr(
        weather_transit, "ctaTrainPredGrabber", fake_cta_train_pred_grabber
    )
    monkeypatch.setattr(weather_transit, "weatherGrabber", fake_weather_grabber)
    monkeypatch.setattr(weather, "_read_icon_line", lambda *args: "<icon />")

    weather_transit.main(base_dir=app_dir)

    assert local_data_dir.is_dir()
    assert output_data_dir.is_dir()
    assert (output_data_dir / "weather-script-output-current.svg").is_file()
    assert (output_data_dir / "weather-script-output-hourly.svg").is_file()
    assert (output_data_dir / "weather-script-output-daily.svg").is_file()
