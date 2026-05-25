import datetime

import weather_transit


def test_parse_transit_predictions_from_saved_cta_responses(
    fixtures_dir, sample_config
):
    now = datetime.datetime(2026, 5, 25, 7, 59)

    arrivals = weather_transit.parse_transit_predictions(
        fixtures_dir / "busPredictions.xml",
        fixtures_dir / "trainPredictions.xml",
        sample_config.buses_to_track,
        sample_config.trains_to_track,
        now=now,
    )

    assert arrivals == {
        "sb22": ["15", "25"],
        "nb22": ["05", "13"],
        "wb152": ["22"],
        "eb152": ["26"],
        "sb9": ["18", "26"],
        "nb9": ["08", "25"],
        "sbred": ["09", "20"],
        "nbred": ["03", "16", "22", "34"],
        "sbbrn": ["03", "16"],
        "nbbrn": ["04", "17", "29", "40", "53"],
    }


def test_render_transit_replaces_minutes_and_missing_slots(sample_config):
    now = datetime.datetime(2026, 5, 25, 7, 59)
    arrivals = {
        "sb22": ["15", "25"],
        "nb22": ["05"],
        "wb152": [],
        "eb152": [],
        "sb9": [],
        "nb9": [],
        "sbred": [],
        "nbred": [],
        "sbbrn": [],
        "nbbrn": [],
    }
    template = "BUS3_U1 BUS3_U1_DISP BUS3_U2 BUS3_U2_DISP BUS3_U3 BUS3_U3_DISP "
    template += "BUS3_D1 BUS3_D1_DISP BUS3_D2 BUS3_D2_DISP TIME DISP_TRANSIT"

    output = weather_transit.render_transit(
        template, arrivals, sample_config.bus_places, now=now
    )

    assert "15 inline 25 inline  none" in output
    assert "5 inline  none" in output
    assert "08:00 inline" in output
