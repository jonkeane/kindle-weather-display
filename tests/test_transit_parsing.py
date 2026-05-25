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
        "sb36": ["15", "25"],
        "nb36": ["05", "13"],
        "wb80": ["22"],
        "eb80": ["26"],
        "sb81": ["18", "26"],
        "nb81": ["08", "25"],
        "sbcyn": ["09", "20"],
        "nbcyn": ["03", "16", "22", "34"],
        "sbsep": ["03", "16"],
        "nbsep": ["04", "17", "29", "40", "53"],
    }


def test_render_transit_replaces_minutes_and_missing_slots(sample_config):
    now = datetime.datetime(2026, 5, 25, 7, 59)
    arrivals = {
        "sb36": ["15", "25"],
        "nb36": ["05"],
        "wb80": [],
        "eb80": [],
        "sb81": [],
        "nb81": [],
        "sbcyn": [],
        "nbcyn": [],
        "sbsep": [],
        "nbsep": [],
    }
    template = "BUS3_U1 BUS3_U1_DISP BUS3_U2 BUS3_U2_DISP BUS3_U3 BUS3_U3_DISP "
    template += "BUS3_D1 BUS3_D1_DISP BUS3_D2 BUS3_D2_DISP TIME DISP_TRANSIT"

    output = weather_transit.render_transit(
        template, arrivals, sample_config.bus_places, now=now
    )

    assert "15 inline 25 inline  none" in output
    assert "5 inline  none" in output
    assert "08:00 inline" in output
