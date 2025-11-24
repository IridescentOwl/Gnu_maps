import React, { useState, useMemo, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import { startDelivery, getEta } from '../api/delivery';

const center = {
  lat: 51.505,
  lng: -0.09,
};

function DraggableMarker({ position, setPosition, color }) {
  const markerRef = useRef(null);
  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker != null) {
          setPosition(marker.getLatLng());
        }
      },
    }),
    [setPosition],
  );

  return (
    <Marker
      draggable={true}
      eventHandlers={eventHandlers}
      position={position}
      ref={markerRef}
      icon={new (window.L.Icon)({
        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      })}
    >
        <Popup>Drag to select location</Popup>
    </Marker>
  );
}

function Map() {
  const [startPosition, setStartPosition] = useState(center);
  const [destPosition, setDestPosition] = useState({ lat: center.lat + 0.1, lng: center.lng + 0.1 });
  const [route, setRoute] = useState([]);
  const [eta, setEta] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [weather, setWeather] = useState(1);
  const [traffic, setTraffic] = useState(1);
  const [vehicle, setVehicle] = useState(1);
  const [deliveries, setDeliveries] = useState(1);
  const [festival, setFestival] = useState(1);
  const [city, setCity] = useState(1);

  const handleGetEta = useCallback(async () => {
    setLoading(true);
    setError(null);
    setRoute([]);
    setEta(null);

    const features = {
        Weather_conditions: weather,
        Road_traffic_density: traffic,
        Vehicle_condition: vehicle,
        multiple_deliveries: deliveries,
        Festival: festival,
        City: city
    }

    try {
      const startRes = await startDelivery(startPosition, destPosition, features);
      if (startRes.status === 200) {
        let currentEta = null;
        let routePoints = [];
        for (let i = 0; i < startRes.data.route_length; i++) {
          const etaRes = await getEta(true);
          currentEta = etaRes.data.eta_prediction;
          routePoints.push(etaRes.data.current_coord.reverse());
        }
        setRoute(routePoints);
        setEta(currentEta);
      }
    } catch (err) {
      setError('Failed to get ETA. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, [startPosition, destPosition, weather, traffic, vehicle, deliveries, festival, city]);

  return (
    <div>
      <MapContainer center={center} zoom={13} style={{ height: '600px', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <DraggableMarker position={startPosition} setPosition={setStartPosition} color="green" />
        <DraggableMarker position={destPosition} setPosition={setDestPosition} color="red" />
        {route.length > 0 && <Polyline positions={route} color="blue" />}
      </MapContainer>
      <div className="controls">
        <div className="sliders-container">
          <div className="slider-column">
            <div>
              <label>Weather Conditions: {weather}</label>
              <input type="range" min="1" max="6" value={weather} onChange={(e) => setWeather(e.target.value)} />
            </div>
            <div>
              <label>Road Traffic Density: {traffic}</label>
              <input type="range" min="1" max="4" value={traffic} onChange={(e) => setTraffic(e.target.value)} />
            </div>
          </div>
          <div className="slider-column">
            <div>
              <label>Vehicle Condition: {vehicle}</label>
              <input type="range" min="0" max="2" value={vehicle} onChange={(e) => setVehicle(e.target.value)} />
            </div>
            <div>
              <label>Multiple Deliveries: {deliveries}</label>
              <input type="range" min="0" max="3" value={deliveries} onChange={(e) => setDeliveries(e.target.value)} />
            </div>
          </div>
          <div className="slider-column">
            <div>
              <label>Festival: {festival}</label>
              <input type="range" min="0" max="1" value={festival} onChange={(e) => setFestival(e.target.value)} />
            </div>
            <div>
              <label>City: {city}</label>
              <input type="range" min="1" max="3" value={city} onChange={(e) => setCity(e.target.value)} />
            </div>
          </div>
        </div>
        <button onClick={handleGetEta} disabled={loading}>
          {loading ? 'Calculating...' : 'Get ETA'}
        </button>
        {eta && <div className="eta-display">Estimated Time of Arrival: {eta.toFixed(2)} minutes</div>}
        {error && <div className="error-display">{error}</div>}
      </div>
    </div>
  );
}

export default Map;
