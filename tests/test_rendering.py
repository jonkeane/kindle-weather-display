import datetime

import weather_transit


def test_build_current_output_replaces_weather_transit_and_view_placeholders(
    fixtures_dir, server_dir, sample_config, weather_data
):
    now = datetime.datetime(2026, 5, 25, 7, 59)
    template = (server_dir / "weather-transit-preprocess.svg").read_text(
        encoding="utf-8"
    )

    output = weather_transit.build_current_output(
        weather_data,
        template,
        sample_config,
        [fixtures_dir / "busPredictions.xml", fixtures_dir / "trainPredictions.xml"],
        now=now,
        base_dir=server_dir,
    )

    for placeholder in [
        "CURRTEMP",
        "CURRFEELS",
        "CURRWIND",
        "CURRHUM",
        "CURR_COND_ICON",
        "DISP_CURR",
        "DISP_TRANSIT",
        "DISP5DAY",
        "DISP12HOUR",
        "BUS1_U1",
        "BUS3_D1",
    ]:
        assert placeholder not in output

    assert ">62</text>" in output
    assert ">64</text>" in output
    assert ">08:00</text>" in output
    assert 'id="currentDynamicVars" display="inline"' in output
    assert 'id="_x35_dayForecastDynamicVars" display="none"' in output
    assert 'id="_x31_2hrForeDynamicVars" display="none"' in output


def test_build_hourly_output_replaces_hourly_placeholders(
    fixtures_dir, server_dir, sample_config, weather_data
):
    now = datetime.datetime(2026, 5, 25, 7, 59)
    template = (server_dir / "weather-transit-preprocess.svg").read_text(
        encoding="utf-8"
    )

    output = weather_transit.build_hourly_output(
        weather_data,
        template,
        sample_config,
        [fixtures_dir / "busPredictions.xml", fixtures_dir / "trainPredictions.xml"],
        now=now,
        base_dir=server_dir,
    )

    assert "H_1_" not in output
    assert "TEMP_1_" not in output
    assert "WINDSPEED_1_" not in output
    assert "HOUR_1_WIND_DEGS" not in output
    assert "HOUR_1_COND_ICON" not in output
    assert 'id="_x31_2hrForeDynamicVars" display="inline"' in output
    assert 'id="currentDynamicVars" display="none"' in output


def test_build_daily_output_replaces_daily_placeholders(
    fixtures_dir, server_dir, sample_config, weather_data
):
    now = datetime.datetime(2026, 5, 25, 7, 59)
    template = (server_dir / "weather-transit-preprocess.svg").read_text(
        encoding="utf-8"
    )

    output = weather_transit.build_daily_output(
        weather_data,
        template,
        sample_config,
        [fixtures_dir / "busPredictions.xml", fixtures_dir / "trainPredictions.xml"],
        now=now,
        base_dir=server_dir,
    )

    assert "DAY_3_" not in output
    assert "TEMP_HI_1_" not in output
    assert "TEMP_LO_1_" not in output
    assert "DAY_COND_ICON_1" not in output
    assert ">Wednesday</text>" in output
    assert ">Thursday</text>" in output
    assert ">Friday</text>" in output
    assert 'id="_x35_dayForecastDynamicVars" display="inline"' in output
    assert 'id="currentDynamicVars" display="none"' in output
