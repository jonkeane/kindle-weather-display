import datetime
import xml.etree.ElementTree as ET

from config import load_config
from constants import HIDE, SHOW
from utils import current_local_datetime


BOUNDS = {
    "Northbound": "nb",
    "Southbound": "sb",
    "Eastbound": "eb",
    "Westbound": "wb",
    "NORTH": "nb",
    "SOUTH": "sb",
    "EAST": "eb",
    "WEST": "wb",
}

TRAIN_STOP_IDS_TO_BOUNDS = {
    "30274": "sb",
    "30273": "nb",
    "30071": "sb",
    "30070": "nb",
}


def _xml_root(source):
    if isinstance(source, ET.Element):
        return source
    if hasattr(source, "read"):
        return ET.parse(source).getroot()
    if isinstance(source, bytes):
        return ET.fromstring(source)
    if isinstance(source, str) and source.lstrip().startswith("<"):
        return ET.fromstring(source)
    return ET.parse(source).getroot()


def _find_text(element, tag):
    child = element.find(tag)
    if child is None:
        return None
    return child.text


def parse_transit_predictions(
    bus_xml,
    train_xml,
    buses_to_track,
    trains_to_track,
    now=None,
    train_stop_ids_to_bounds=None,
):
    if now is None:
        now = current_local_datetime()
    if now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    train_stop_ids_to_bounds = train_stop_ids_to_bounds or TRAIN_STOP_IDS_TO_BOUNDS

    things_to_track = list(buses_to_track.keys()) + list(trains_to_track.keys())
    raw_predictions = {route: [] for route in things_to_track}
    arrivals = {route: [] for route in things_to_track}
    seen_vehicle_times = set()

    for prediction in _xml_root(bus_xml):
        if prediction.tag != "prd":
            continue

        direction = _find_text(prediction, "rtdir")
        route_number = _find_text(prediction, "rt")
        vehicle_id = _find_text(prediction, "vid")
        predicted_time = _find_text(prediction, "prdtm")
        if None in (direction, route_number, vehicle_id, predicted_time):
            continue

        bound = BOUNDS.get(direction)
        if bound is None:
            continue

        duplicate_key = "".join([bound, route_number, vehicle_id, predicted_time])
        if duplicate_key in seen_vehicle_times:
            continue
        seen_vehicle_times.add(duplicate_key)

        route = "".join([bound, route_number])
        if route in raw_predictions:
            raw_predictions[route].append(predicted_time)

    for prediction in _xml_root(train_xml):
        if prediction.tag != "eta":
            continue

        stop_id = _find_text(prediction, "stpId")
        route_name = _find_text(prediction, "rt")
        run_number = _find_text(prediction, "rn")
        arrival_time = _find_text(prediction, "arrT")
        if None in (stop_id, route_name, run_number, arrival_time):
            continue

        bound = train_stop_ids_to_bounds.get(stop_id)
        if bound is None:
            continue

        duplicate_key = "".join([bound, route_name, run_number, arrival_time])
        if duplicate_key in seen_vehicle_times:
            continue
        seen_vehicle_times.add(duplicate_key)

        route = "".join([bound, route_name]).lower()
        if route in raw_predictions:
            raw_predictions[route].append(arrival_time)

    for route, predictions in raw_predictions.items():
        for predicted_time in predictions:
            if len(predicted_time) == 14:
                arrival = datetime.datetime.strptime(
                    predicted_time, "%Y%m%d %H:%M"
                ) - now
                arrival = arrival - datetime.timedelta(seconds=60)
            elif len(predicted_time) == 17:
                arrival = datetime.datetime.strptime(
                    predicted_time, "%Y%m%d %H:%M:%S"
                ) - now
            else:
                continue

            if arrival > datetime.timedelta(seconds=60):
                arrivals[route].append(str(arrival).split(":")[1])

    return arrivals


def _format_arrival_for_display(arrival):
    if arrival == "00":
        return "0"
    if arrival.startswith("0"):
        return arrival[1:]
    return arrival


def render_transit(output, arrivals, bus_places, now=None):
    if now is None:
        now = current_local_datetime()
    if now.tzinfo is not None:
        now = now.replace(tzinfo=None)

    for route, route_arrivals in arrivals.items():
        bus_place = bus_places[route[2:]]
        if route[:2] == "nb" or route[:2] == "wb":
            bus_place = bus_place + "_D"
        else:
            bus_place = bus_place + "_U"

        for index in range(3):
            placeholder = bus_place + str(index + 1)
            display_placeholder = placeholder + "_DISP"
            try:
                arrival = _format_arrival_for_display(route_arrivals[index])
                output = output.replace(display_placeholder, SHOW)
                output = output.replace(placeholder, arrival)
            except IndexError:
                output = output.replace(display_placeholder, HIDE)
                output = output.replace(placeholder, "")

    display_time = (now + datetime.timedelta(seconds=60)).strftime("%H:%M")
    output = output.replace("TIME", display_time)
    output = output.replace("DISP_TRANSIT", SHOW)
    return output


def addTransit(output, paths=None, config=None, now=None):
    if paths is None:
        paths = ["localData/busPredictions.xml", "localData/trainPredictions.xml"]
    if config is None:
        config = load_config()

    arrivals = parse_transit_predictions(
        paths[0],
        paths[1],
        config.buses_to_track,
        config.trains_to_track,
        now=now,
    )
    return render_transit(output, arrivals, config.bus_places, now=now)
