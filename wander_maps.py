import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime

import folium
import folium.plugins
import numpy as np
import xyzservices.providers as xyz
from geopy.geocoders import Nominatim

API_KEY_STADIA = os.getenv("API_KEY_STADIA")
if not API_KEY_STADIA:
    print("\033[93mNo Stadia API Key given. Using default maps\033[0m")


GEO_LOCATOR = Nominatim(user_agent="WanderMaps")


@dataclass
class Stop:
    """Class to store trip data"""

    name: str
    longitude: float
    latitude: float
    icon: str = "location-dot"
    icon_color: str = "blue"
    date: datetime = None

    def __repr__(self):
        return f"{self.name} ({self.latitude},{self.longitude}) on {self.date}"

    @property
    def coordinates(self) -> tuple[float, float]:
        """Returns the stop's location as (latitude, longitude)"""
        return (self.latitude, self.longitude)


def convert_trip_locations(locations: dict) -> list[Stop]:
    """Load in a trip's locations from JSON dictionary. Returns a list of `Stop` instances"""
    stops = []

    for location in locations:
        name = location.pop("name").title()
        # convert date to a datetime object. if no date given, it will default to
        # a randomly hardcoded date
        date = location.pop("date", "2025-01-01")

        print(f"\tFetching coordinates for {name}")
        # FIX: this is slow. cache?
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


def _get_map(center: tuple[int, int], zoom: int) -> folium.Map:
    print(f"Map center: {center}")
    base_map = folium.Map(location=center, tiles="OpenStreetMap", zoom_start=zoom)

    if API_KEY_STADIA:
        # set up pretty world map from Stadia
        # add the Stadia Maps Stamen Watercolor provider details via xyzservices
        # and update the URL to include the API key placeholder
        # see https://docs.stadiamaps.com/guides/migrating-from-stamen-map-tiles/#folium
        tile_provider = xyz.Stadia.StamenWatercolor
        tile_provider["url"] = tile_provider["url"] + f"?api_key={API_KEY_STADIA}"

        folium.TileLayer(
            tiles=tile_provider.build_url(api_key=API_KEY_STADIA),
            attr=tile_provider.attribution,
            name=tile_provider.name,
            max_zoom=tile_provider.max_zoom,
            # TODO: watercolour doesn't support retina?
            detect_retina=True,
        ).add_to(base_map)

    # leave with default setting if API key not given
    return base_map


def calculate_map_centroid(*coordinates: tuple[float, float]) -> tuple[float, float]:
    return np.mean(coordinates, axis=0)


def create_map(trip: list[Stop], center: tuple[int, int], zoom: int) -> folium.Map:
    """Creates a `folium.Map` from the given `Stop`s"""
    # initialise the map
    m = _get_map(center, zoom)

    # sort stops by date
    # antpath can't handle it if they're not and just ignores them
    # TODO: this sorts it in-place. either move to convert_trip_locations or
    # use sorted() instead to create a copy
    # TODO: more fine-grained than sorting by day?
    trip.sort(key=lambda x: datetime(x.date.year, x.date.month, x.date.day))

    # add stops
    for stop in trip:
        name = stop.name
        folium.Marker(
            location=stop.coordinates,
            popup=name,
            tooltip=name,
            icon=folium.Icon(icon=stop.icon, prefix="fa", color=stop.icon_color),
        ).add_to(m)

    folium.PolyLine([stop.coordinates for stop in trip]).add_to(m)

    return m


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--locations", type=str, required=True)
    parser.add_argument("-cx", help="Map center x-coordinate", type=int, required=False, default=None)
    parser.add_argument("-cy", help="Map center y-coordinate", type=int, required=False, default=None)
    parser.add_argument("-z", "--zoom", default=10, required=False, type=int)
    args = parser.parse_args()

    # load in the trip locations from file
    with open(args.locations, "r") as f:
        locations = json.load(f)

    trip = convert_trip_locations(locations)

    # create the map with the locations
    print("Create map")
    # calculate the centroid of all locations
    # use set to avoid weighted centroid if location got visited multiple times
    centroid = (args.cx, args.cy) if args.cx and args.cy else calculate_map_centroid(*set(t.coordinates for t in trip))
    m = create_map(trip, centroid, args.zoom)

    # save map to html
    m.save("trip_visualisation.html")
