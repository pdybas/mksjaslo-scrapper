import requests
import json
import os
from bs4 import BeautifulSoup

class BusStopDetail:
    name: str = ''
    url: str = ''

class BusStop:
    id: int
    name: str
    details: list[BusStopDetail] = []
    
    def toJson(self):
        self_json = '{ "id": ' + str(self.id) + ', "name": "' + self.name +'", '

        details_json = json.dumps(self.details, default=lambda o: o.__dict__, ensure_ascii=False)
        self_json += '"details": ' + details_json + ' }'

        return self_json

_base_url = "https://www.mksjaslo.com.pl"
_all_timetables_url = _base_url + "/rozklad-jazdy/tabliczki-przystankowe"

def _get_bus_stops() -> list[BusStop]:
    site = requests.get(_all_timetables_url)
    site.encoding = site.apparent_encoding
    if site.status_code != 200:
        return []
    soup = BeautifulSoup(site.text, "html.parser")
    option_nodes = soup.find_all("option")
    bus_stops: list[BusStop] = []
    i = 1
    for node in option_nodes:
        if i > 3:
            break
        value = str(node.attrs.get("value"))
        if value.isnumeric():
            bus_stop = BusStop()
            bus_stop.id = int(value)
            bus_stop.name = node.text.strip()
            bus_stop.details = []
            bus_stops.append(bus_stop)
        i += 1
        
    for bus in bus_stops:
        bus.details = _get_bus_stop_detail(bus.id)
    
    return bus_stops

def _get_bus_stop_detail(id: int) -> list[BusStopDetail]:
    details: list[BusStopDetail] = []
    bus_site = requests.post(
            _all_timetables_url, 
            data = {"polaczenia": id, "submit": "Szukaj" })
    bus_site.encoding = bus_site.apparent_encoding
    if bus_site.status_code == 200:
        bus_soup = BeautifulSoup(bus_site.text, "html.parser")
        a_nodes = bus_soup.find_all("a")
        
        for a_node in a_nodes:
            href = str(a_node.attrs.get("href"))
            if "ROZKLAD_JAZDY" in href:
                detail = BusStopDetail()
                detail.name = a_node.text.strip()
                detail.url = _base_url + href
                details.append(detail)

    return details


def get_bus_stops_json() -> str:
    bus_stops = _get_bus_stops()
    jsons: list[str] = []
    for bus_stop in bus_stops :
        json = bus_stop.toJson()
        jsons.append(json)
    linked_json = ("[" + ", ".join(jsons) + "]").encode("utf-8")
    return linked_json

def get_timetables_urls(bus_stops: dict[BusStop]):
    urls: list[str] = []
    for bus_stop in bus_stops:
        if not bus_stop["details"]:
            continue
        for detail in bus_stop["details"]:
            if not detail["url"]:
                continue
            urls.append(detail["url"])
    return urls
    
def save_bus_stops_json(filepath: str):
    bus_stops_json = get_bus_stops_json()
    
    dir_path = os.path.dirname(filepath)
    os.makedirs(dir_path, exist_ok=True)
    
    with open(filepath, "wb+") as file:
        file.write(bus_stops_json)