from datetime import datetime
from unittest.mock import patch

from geopy.location import Location

import app.trip as t


def test_stop():
    # test with necessary arguments
    stop_name = "copenhagen"
    lat, lon = 12.56848, 55.67670
    s = t.Stop(name=stop_name, longitude=lon, latitude=lat)

    assert s.name == "copenhagen"
    assert s.coordinates == (lat, lon)

    # test optional arguments
    col = "orange"
    icon = "sailboat"
    date = [datetime.now(), datetime(2025, 1, 1)]
    s = t.Stop(stop_name, lon, lat, icon_color=col, icon=icon, date=date)

    assert s.icon_color == col
    assert s.date == date
    assert s.icon == icon


def test_convert_trip_locations():
    random_locations = [
        {
            "name": "copenhagen",
            "icon": "sailboat",
            "date": ["2025-01-01", "2025-01-10"],
        }
    ]

    # Create a mock API client
    with patch.object(
        t.GEO_LOCATOR,
        "geocode",
        return_value=Location(address="", point=(12.5, 13.5), raw=""),
    ) as _:
        trip = t.convert_trip_locations(random_locations)

    assert len(trip) == 2  # two entries for copenhagen, since visited twice
