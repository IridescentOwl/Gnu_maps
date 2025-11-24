import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const startDelivery = async (startCoords, destCoords, features) => {
  const payload = {
    features: features,
    destinationCoords: {
      destLat: destCoords.lat,
      destLong: destCoords.lng,
    },
    startCoords: {
      startLat: startCoords.lat,
      startLong: startCoords.lng,
    },
  };
  return await axios.post(`${API_URL}/start-delivery`, payload);
};

export const getEta = async (advance = false) => {
  return await axios.get(`${API_URL}/predict-eta?advance=${advance}`);
};
