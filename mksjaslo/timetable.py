import requests
import json
import os
from bs4 import BeautifulSoup
from mksjaslo import bus_stop

class TimetableSign:
    type: str = ''
    description: str = ''

class TimetableHour:
    hour: str = ''
    type: str = ''

class TimetableDirection:
    name: str = ''
    line: str = ''
    throught: list[str] = []
    hours: list[TimetableHour] = []
    
    def toJson(self):
        self_json = '{ "name": "' + self.name + '", "line": "' + self.line +'", '

        throught_json = json.dumps(self.throught, default=lambda o: o.__dict__, ensure_ascii=False)
        self_json += '"throught": ' + throught_json + ', '

        hours_json = json.dumps(self.hours, default=lambda o: o.__dict__, ensure_ascii=False)
        self_json += '"hours": ' + hours_json + ' }'

        return self_json

class Timetable:
    name: str = ''
    date: str = ''
    url: str = ''
    directions: list[TimetableDirection] = []
    signs: list[TimetableSign] = []
    
    def toJson(self):
        self_json = '{ "name": "' + self.name + '", "date": "'
        self_json += self.date + '", "url": "' + self.url + '", '

        directions_jsons = []

        for direction in self.directions:
            directions_jsons.append(direction.toJson())

        directions_json = '[' + ",".join(directions_jsons) + ']'
        self_json += '"directions": ' + directions_json + ', '

        signs_json = json.dumps(self.signs, default=lambda o: o.__dict__, ensure_ascii=False)
        self_json += '"signs": ' + signs_json + ' }'

        return self_json

def get_timetable_json(url: str) -> str:
    site = requests.get(url)
    site.encoding = site.apparent_encoding
    if site.status_code != 200:
        return ""

    if len(site.text) < 10:
        return ""

    soup = BeautifulSoup(site.text, "html.parser")

    timetable = Timetable()
    timetable.directions = []
    timetable.signs = []
    timetable.url = url
    name_node = soup.find("td", attrs={"align": "center"})
    timetable.name = name_node.text
    date_node = soup.find("td", attrs={"align": "right"})
    timetable.date = date_node.text.replace("Rozkład ważny od: ", "")

    tr_nodes = soup.find_all("tr")

    for i in range(len(tr_nodes) -1, 0, -1):
        tr_node = tr_nodes[i]
        td_nodes = tr_node.find_all("td")
        if len(td_nodes) != 2:
            break
        
        tt_sign = TimetableSign()
        tt_sign.type = td_nodes[0].text.strip()
        tt_sign.description = td_nodes[1].text.strip().replace("- ", "")
        timetable.signs.append(tt_sign)
    timetable.signs.reverse()

    tt_direction = TimetableDirection()
    tt_direction.hours = []
    tt_direction.throught = []
    with_line = False
    hard_brake = False

    for i in range(9, len(tr_nodes)):
        tr_node = tr_nodes[i]
        td_nodes = tr_node.find_all("td")
        if i == 9:
            if len(td_nodes) > 2:
                with_line = True
            continue

        row_type = 0
        for j in range(len(td_nodes)):
            td_node = td_nodes[j]
            if j == 0:
                colspan = td_node.attrs.get("colspan")
                rowspan = td_node.attrs.get("rowspan")
                b_nodes = td_node.find_all("b")
                
                if td_node.text == "OZNACZENIA KURSÓW" and rowspan is None:
                    hard_brake = True
                    break
                if len(b_nodes) > 0:
                    row_type = 1
                    if tt_direction.name:
                        timetable.directions.append(tt_direction)
                        tt_direction = TimetableDirection()
                        tt_direction.hours = []
                        tt_direction.throught = []
                    tt_direction.name = td_node.text.strip()
                elif colspan == "2" and rowspan is not None:
                    row_type = 2
                    span_value = str(td_node.next.decode_contents())
                    split = span_value.split("<br/>")
                    if len (split) > 0:
                        split[0] = split[0].replace("przez ", "")
                    tt_direction.throught = split
                elif colspan is None and rowspan is None:
                    row_type = 3
            elif j == 1 and row_type == 1 and with_line:
                tt_direction.line = td_node.text.strip()
            else:
                additional = 0
                if row_type == 3 or not with_line:
                    additional = 1
                
                if (j + additional) % 2 == 0:
                    timetable_hour = TimetableHour()
                    timetable_hour.hour = td_node.text.strip()
                    if not timetable_hour.hour: 
                        continue
                    timetable_hour.type = td_nodes[j + 1].text.strip()
                    if timetable_hour.hour and timetable_hour.type:
                        tt_direction.hours.append(timetable_hour)

        if hard_brake: 
            break

    if tt_direction.name:
        timetable.directions.append(tt_direction)

    timetable_json = timetable.toJson()
    return timetable_json

def save_timetables_json(bus_stops_filename: str, timetable_filename: str):
    if not os.path.exists(bus_stops_filename):
        print("Bus stop path does not exists")
        return
    bus_stops = []
    with open(bus_stops_filename, "rb") as file:
        bus_stops = json.load(file)
    bus_stops_urls = bus_stop.get_timetables_urls(bus_stops)
    
    timetables_json: list[str] = []
    for url in bus_stops_urls:
        url = url.strip()
        timetable_json = get_timetable_json(url)
        if timetable_json:
            timetables_json.append(timetable_json)
    
    linked_json = ("[" + ", ".join(timetables_json) + "]").encode("utf-8")

    dir_path = os.path.dirname(timetable_filename)
    os.makedirs(dir_path, exist_ok=True)

    with open(timetable_filename, "wb+") as file:
        file.write(linked_json)