import argparse
import json
import os
from dataclasses import dataclass

import folium
import xyzservices.providers as xyz

API_KEY_STADIA = os.getenv("API_KEY_STADIA")
if not API_KEY_STADIA:
    print("\033[93mNo Stadia API Key given. Using default maps\033[0m")


@dataclass
class Stop:
    """Class to store trip data"""

    name: str
    location: tuple[float, float]
    icon: str
    alias: str = None


def load_trip_locations(fpath: str) -> list[Stop]:
    """Load in a trip's locations from JSON dictionary. Returns a list of `Stop` instances"""
    with open(fpath, "r") as f:
        locations = json.load(f)

    stops = []
    for name, details in locations.items():
        stops.append(Stop(name=name.replace("_", " ").title(), **details))

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


def create_map(trip: list[Stop], center: tuple[int, int], zoom: int) -> folium.Map:
    """Creates a `folium.Map` from the given `Stop`s"""
    # initialise the map
    m = _get_map(center, zoom)

    # add stops
    for stop in trip:
        folium.Marker(
            location=stop.location,
            popup=stop.alias if stop.alias else stop.name,
            icon=folium.Icon(icon=stop.icon, prefix="fa"),
        ).add_to(m)

    # draw connecting route
    folium.PolyLine([stop.location for stop in trip]).add_to(m)

    return m


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--locations", type=str, required=True)
    parser.add_argument(
        "-cx", help="Map center x-coordinate", type=int, required=False, default=0
    )
    parser.add_argument(
        "-cy", help="Map center y-coordinate", type=int, required=False, default=0
    )
    parser.add_argument("-z", "--zoom", default=10, required=False, type=int)
    args = parser.parse_args()

    # load in the trip locations from file
    trip = load_trip_locations(args.locations)

    # create the map with the locations
    m = create_map(trip, (args.cx, args.cy), args.zoom)

    # save map to html
    m.save("trip-visualisation.html")
