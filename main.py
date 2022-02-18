import mksjaslo
import os

_data_dir = "data"
_bus_stops_filename = "bus_stops.json"
_bus_stops_urls_filename = "bus_stops_urls.txt"
_timetables_filename = "timetables.json"

def create_dir_if_not_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def get_absolute_path(relative_path: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

def save_bus_stops():
    bus_stops = mksjaslo.get_bus_stops()
    jsons: list[str] = []
    for bus_stop in bus_stops :
        json = bus_stop.toJson()
        jsons.append(json)
    linked_json = ("[" + ", ".join(jsons) + "]").encode("utf-8")
    data_path = get_absolute_path(_data_dir)
    create_dir_if_not_exists(data_path)
    filepath = os.path.join(data_path, _bus_stops_filename)
    with open(filepath, "wb+") as file:
        file.write(linked_json)

def save_timetables():
    lines = []
    data_path = get_absolute_path(_data_dir)
    filepath = os.path.join(data_path, _bus_stops_urls_filename)
    with open(filepath, "r") as file:
        lines = file.readlines()

    jsons: list[str] = []
    for url in lines:
        url = url.strip()
        json = mksjaslo.get_timetable(url)
        if json:
            jsons.append(json)
    
    linked_json = ("[" + ", ".join(jsons) + "]").encode("utf-8")
    filepath = os.path.join(data_path, _timetables_filename)
    with open(filepath, "wb+") as file:
        file.write(linked_json)

# save_bus_stops()
# save_timetables()

print("Done")