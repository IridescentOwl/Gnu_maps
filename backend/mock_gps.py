from mapbox import Directions
from dotenv import load_dotenv
import os
import json

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

directions_service = Directions(access_token=MAPBOX_TOKEN)

def process_coords(coords_file = 'coords.json', output = 'route.json'):
    with open(coords_file, 'r') as f:
        data = json.load(f)

    origin = data["start"]["geometry"]["coordinates"]
    destination = data["destination"]["geometry"]["coordinates"]

    print("Origin:", origin)
    print("Destination:", destination)

    response = directions_service.directions(
        [origin, destination],  
        profile='mapbox/driving',
        steps=True,
        geometries='geojson'
    )

    if response.status_code == 200:
        result = response.json()
        route = result['routes'][0]['geometry']['coordinates']

        route_data = {
            "route": route
        }

        with open(output, 'w') as f:
            json.dump(route_data, f, indent = 4)
    else:
        print("Error:", response.status_code, response.text)
        raise Exception(f"Mapbox API error {response.status_code}: {response.text}")
