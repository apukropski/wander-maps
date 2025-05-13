import argparse
import json

from map import calculate_map_centroid, create_map
from trip import convert_trip_locations

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--locations", type=str, required=True)
    parser.add_argument("-cx", help="Map center x-coordinate", type=float, required=False, default=None)
    parser.add_argument("-cy", help="Map center y-coordinate", type=float, required=False, default=None)
    parser.add_argument("-z", "--zoom", default=10, required=False, type=int)
    args = parser.parse_args()

    # load in the trip locations from file
    with open(args.locations, "r") as f:
        locations = json.load(f)
    trip = convert_trip_locations(locations)

    # calculate the centroid of all locations
    # use set to avoid weighted centroid if location got visited multiple times
    centroid = (args.cx, args.cy) if args.cx and args.cy else calculate_map_centroid(*set(t.coordinates for t in trip))

    # create the map with the locations
    print("Create map")
    m = create_map(trip, centroid, args.zoom)

    # save map to html
    m.save("trip_visualisation.html")
