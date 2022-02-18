import requests
import json
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

def get_bus_stops() -> list[BusStop]:
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
            bus_stops.append(bus_stop)
        i += 1
        
    for bus in bus_stops:
        bus_site = requests.post(
                _all_timetables_url, 
                data = {"polaczenia": bus.id, "submit": "Szukaj" })
        bus_site.encoding = bus_site.apparent_encoding
        if bus_site.status_code == 200:
            bus_soup = BeautifulSoup(bus_site.text, "html.parser")
            a_nodes = bus_soup.find_all("a")
            bus.details = []
            for a_node in a_nodes:
                href = str(a_node.attrs.get("href"))
                if "ROZKLAD_JAZDY" in href:
                    detail = BusStopDetail()
                    detail.name = a_node.text.strip()
                    detail.url = _base_url + href
                    bus.details.append(detail)
    
    return bus_stops