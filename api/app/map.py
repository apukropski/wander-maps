import os
from datetime import datetime

import folium
import folium.plugins
import xyzservices.providers as xyz
from trip import Stop
from xyzservices import TileProvider

ARROWHEAD_OFFSET = 0.005

API_KEY_STADIA = os.getenv("API_KEY_STADIA")
if not API_KEY_STADIA:
    print("\033[93mNo Stadia API Key given. Using default maps\033[0m")


def _get_map(center: tuple[float, float], zoom: int) -> folium.Map:
    if API_KEY_STADIA:
        # set up watercolour map from Stadia
        # add the Stadia Maps Stamen Watercolor provider details via xyzservices
        # and update the URL to include the API key placeholder
        # see https://docs.stadiamaps.com/guides/migrating-from-stamen-map-tiles/#folium
        tile_provider: TileProvider = xyz.Stadia.StamenWatercolor
        tile_provider["url"] += f"?api_key={API_KEY_STADIA}"
        tile_url = tile_provider.build_url(api_key=API_KEY_STADIA)

    else:
        tile_provider: TileProvider = xyz.OpenStreetMap.Mapnik
        tile_url = tile_provider.build_url()

    return folium.Map(
        location=center,
        tiles=folium.TileLayer(
            tiles=tile_url,
            attr=tile_provider.html_attribution,
            detect_retina=True,
        ),
        zoom_start=zoom,
    )


def calculate_map_centroid(*coordinates: tuple[float, float]) -> tuple[float, float]:
    import numpy as np

    return np.mean(coordinates, axis=0)


def create_map(trip: list[Stop], center: tuple[float, float], zoom: int) -> folium.Map:
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

    # draw connecting route
    folium.PolyLine([stop.coordinates for stop in trip]).add_to(m)

    return m
