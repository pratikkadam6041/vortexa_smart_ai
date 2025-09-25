# Vortexa Crop Platform API Documentation

This document provides the necessary information for the frontend team to connect to the backend API.

---

## Get Live Weather

This endpoint retrieves the current weather conditions for a predefined location.

* **Method:** `GET`
* **URL:** `http://127.0.0.1:8000/weather`

---

# Success Response (Code: 200 OK)

If the request is successful, the API will return a JSON object with the following structure:

**Sample JSON:**
```json
{
  "coord": {
    "lon": 73.8139,
    "lat": 18.6278
  },
  "weather": [
    {
      "id": 801,
      "main": "Clouds",
      "description": "few clouds",
      "icon": "02d"
    }
  ],
  "main": {
    "temp": 26.5,
    "feels_like": 27.1,
    "humidity": 75
  },
  "wind": {
    "speed": 3.5
  },
  "name": "Pimpri"
}