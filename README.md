# :world_map: WanderMaps

A Python script to visualise trip itineraries with folium.

## Setup

Install the `folium` [package](https://github.com/python-visualization/folium?tab=readme-ov-file#installation)

## Run

1. Create a JSON file with the trip details

```json
{
  "copenhagen": { "location": [55.6767, 12.56848], "icon": "sailboat" },
  "odense": { "location": [55.39808, 10.38175], "icon": "book" }
}
```

Available icons can be found here: https://fontawesome.com/icons?d=gallery

2. Run the wander maps script:

```sh
# create a map with 0,0 as center coordinates and a default zoom of 10
python wander_maps.py -l example_trip.json

# create a map with custom center coordinates and zoom
python wander_maps.py -l example_trip.json -cx 55 -cy 11 -z 8
```

3. Open the generated `.html` file in a browser

![OpenStreetMap Demo](../assets/map-openstreetmap.png)

## Even more beautiful maps

The script supports using Stadia's [Stamen Watercolor](https://stadiamaps.com/explore-the-map/#style=stamen_watercolor&map=10.22/55.718/12.4992) map. To use it as a background:

1. Create a Stadia account
2. Create an API key

To generate a map with the Stadia map:

```sh
API_KEY_STADIA=<YOUR_API_KEY> python wander_maps.py -l my_trip.json
```

![Stadia Stamen Watercolor Demo](../assets/map-stadia.png)
