from fastapi import FastAPI, Query, Path, HTTPException, status
from typing import Optional
from pydantic import BaseModel
import json
import joblib
from mock_gps import process_coords
from osrmCoordsToDistances import coordsToDistance

class features(BaseModel):
    Weather_conditions: float
    Road_traffic_density: float
    Vehicle_condition: float
    multiple_deliveries: float
    Festival: float
    City: float

class destinationCoords(BaseModel):
    destLat: float
    destLong: float

class startCoords(BaseModel):
    startLat: float
    startLong: float

class DeliveryInput(BaseModel):
    features: features
    destinationCoords: destinationCoords
    startCoords: startCoords

app = FastAPI()
model = joblib.load('model.joblib')

@app.get("/")
async def root():
    return {"message": "Welcome to the delivery service API!"}

@app.post("/start-delivery")
async def start_delivery(data: DeliveryInput):
    features_dict = {
        "features": data.features.model_dump(),
    }

    coords = {
        "start": {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [data.startCoords.startLong, data.startCoords.startLat]
            },
            "properties": {}
        },
        "destination": {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [data.destinationCoords.destLong, data.destinationCoords.destLat]
            },
            "properties": {}
        }
    }

    destination_Coords = [data.destinationCoords.destLong, data.destinationCoords.destLat]

    with open('features.json', 'w') as f:
        json.dump(features_dict, f, indent=4)

    with open('coords.json', 'w') as f:
        json.dump(coords, f, indent=4)

    try:
        route_data = process_coords('coords.json', 'route.json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        with open('route.json', 'r') as f:
            routes = json.load(f)

        for currentCoord in routes["routes"]:
            try:
                currentDistance = coordsToDistance(currentCoord, destination_Coords)

    except
