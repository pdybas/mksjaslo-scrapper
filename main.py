import mksjaslo

_bus_stops = "data/bus_stops.json"
_timetables = "data/timetables.json"

_test_bus_stops = "test_data/bus_stops.json"
_test_timetables = "test_data/timetables.json"

# real
# mksjaslo.save_bus_stops_json(_bus_stops)
# mksjaslo.save_timetables_json(_bus_stops, _timetables)

# test
mksjaslo.save_bus_stops_json(_test_bus_stops)
mksjaslo.save_timetables_json(_test_bus_stops, _test_timetables)

print("Done")