# :world_map: WanderMaps

A Python script to visualise trip itineraries with `folium`.

## Setup

```sh
poetry install
```

## Run

1. Create a JSON file with the trip details

```json
[
  { "name": "copenhagen", "icon": "sailboat" },
  { "name": "odense", "icon": "book" }
]
```

Available icons can be found here: https://fontawesome.com/icons?d=gallery

2. Run the wander maps script:

```sh
# create a map with a zoom of 8 to show the trip in full
cd ./app
python wander_maps.py -l ../data/example_trip.json -z 8
```

3. Open the generated `.html` file in a browser

![OpenStreetMap Demo](https://github.com/apukropski/wander-maps/blob/assets/map_openstreetmap.png)

## Even more beautiful maps

The script supports using Stadia's [Stamen Watercolor](https://stadiamaps.com/explore-the-map/#style=stamen_watercolor&map=10.22/55.718/12.4992) map. To use it as a background:

1. Create a Stadia account
2. Create an API key

To generate a map with the Stadia map:

```sh
API_KEY_STADIA=<YOUR_API_KEY> python wander_maps.py -l ../data/example_trip.json
```

![Stadia Stamen Watercolor Demo](../../assets/map_stadia.png)

## 🐛 Known Problems

### Timeout Error

This occurs when the external service for pulling the coordinates for a location errors out. For now, simply retry

```sh
geopy.exc.GeocoderUnavailable: HTTPSConnectionPool(host='nominatim.openstreetmap.org', port=443): Max retries exceeded with url: /search?q=Denmark%2C+Thy+National+Park&format=json&limit=1 (Caused by ReadTimeoutError("HTTPSConnectionPool(host='nominatim.openstreetmap.org', port=443): Read timed out. (read timeout=1)"))
```
