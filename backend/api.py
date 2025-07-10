from fastapi import FastAPI, Query, Path, HTTPException, status
from typing import Optional
from pydantic import BaseModel
import pandas as pd
import json
import joblib
from mock_gps import process_coords
from osrmCoordsToDistances import coordsToDistance

currentRoute = []
currentStepIndex = 0
currentFeatures = {}
currentDestinationCoords = []

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
    global currentRoute, currentStepIndex, currentFeatures, currentDestinationCoords

    currentFeatures = data.features.model_dump()
    currentDestinationCoords = [data.destinationCoords.destLong, data.destinationCoords.destLat]

    features_dict = {"features" : currentFeatures}

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



    with open('features.json', 'w') as f:
        json.dump(features_dict, f, indent=4)

    with open('coords.json', 'w') as f:
        json.dump(coords, f, indent=4)

    try:
        process_coords('coords.json', 'route.json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        with open('route.json', 'r') as f:
            routes = json.load(f)
            currentRoute = routes["route"]
            currentStepIndex = 0
    except:
        raise HTTPException(status_code=500, detail=f"Error reading route.json: {e}")

    return {
        "status": "Route and features cached and saved",
        "route_length": len(currentRoute)
    }

@app.get("/predict-eta")
async def predict_eta(advance: bool = False):
    global currentRoute, currentStepIndex, currentFeatures, currentDestinationCoords

    if(currentStepIndex >= len(currentRoute)):
        raise HTTPException(status_code=400, detail="Rider has reached the Destination!")

    routePoint = currentRoute[currentStepIndex]
    distance = coordsToDistance(routePoint, currentDestinationCoords)

    modelInput = currentFeatures.copy()
    modelInput["distance_km"] = distance / 1000

    df = pd.DataFrame([modelInput])

    eta = model.predict(df)

    if advance:
        currentStepIndex += 1

    return {
        "step_index": currentStepIndex,
        "current_coord": routePoint,
        "distance_meters": int(distance),
        "eta_prediction": float(eta[0])
    }




