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

app = FastAPI()
model = joblib.load('model.joblib')

@app.get("/")
async def root():
    return {"message": "Welcome to the delivery service API!"}

@app.post("/start-delivery")
async def start_delivery(
    features: features,
    destinationCoords: destinationCoords,
    startCoords: startCoords
):
    features = {
        "features": features.model_dump(),
    }

    coords = {
        "destinationCoords": destinationCoords.model_dump(),
        "startCoords": startCoords.model_dump()
    }

    with open('features.json', 'w') as f:
        json.dump(features, f, indent = 4)

    with open('route.json', 'w') as f:
        json.dump(coords, f, indent = 4)

    try:
        route_data = process_coords('coords.json', 'route.json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

