from dataclasses import dataclass
from datetime import datetime

from geopy.geocoders import Nominatim

GEO_LOCATOR = Nominatim(user_agent="WanderMaps")


@dataclass
class Stop:
    """Class to store trip data"""

    name: str
    longitude: float
    latitude: float
    icon: str = "location-dot"
    icon_color: str = "blue"
    date: datetime | list[datetime] = None

    def __repr__(self):
        return f"{self.name} ({self.latitude},{self.longitude}) on {self.date}"

    @property
    def coordinates(self) -> tuple[float, float]:
        """Returns the stop's location as (latitude, longitude)"""
        return (self.latitude, self.longitude)


def convert_trip_locations(locations: list[dict]) -> list[Stop]:
    """Load in a trip's locations from JSON dictionary. Returns a list of `Stop` instances"""
    stops = []

    for location in locations:
        name = location.pop("name").title()
        # convert date to a datetime object. if no date given, it will default to
        # a randomly hardcoded date
        date = location.pop("date", "2025-01-01")

        print(f"\tFetching coordinates for {name}")
        # FIX: this is slow. cache with redis?
        coordinates = GEO_LOCATOR.geocode(name)

        if isinstance(date, str):  # single visit
            stops.append(
                Stop(
                    name=name,
                    longitude=coordinates.longitude,
                    latitude=coordinates.latitude,
                    date=datetime.strptime(date, "%Y-%m-%d"),
                    **location,
                )
            )
        else:  # multiple visits
            # for every time a location was visited, create a new Stop instance
            _stops = [
                Stop(
                    name=name,
                    longitude=coordinates.longitude,
                    latitude=coordinates.latitude,
                    date=datetime.strptime(d, "%Y-%m-%d"),
                    **location,
                )
                for d in date
            ]

            stops.extend(_stops)

    return stops
