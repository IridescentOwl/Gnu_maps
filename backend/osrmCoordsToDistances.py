import requests

OSRM_URL = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=false"

def coordsToDistance(current_coord, destination_coord):

    current_lat,current_long = current_coord[0], current_coord[1]
    destination_lat, destination_long = destination_coord[0], destination_coord[1]

    url = OSRM_URL.format(current_long, current_lat, destination_long, destination_lat)

    for i in range(2):
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data["routes"][0]["distance"]
        except requests.exceptions.RequestException as e:
            return {response.status_code: "Request Failed!"}
    raise Exception("OSRM conversion request failed!")

