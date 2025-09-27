# api_handler.py
import os, httpx
from statistics import mean
from dotenv import load_dotenv
load_dotenv()

async def get_live_weather(lat, lon):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key: 
        return {"error": "API key not found"}
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        async with httpx.AsyncClient() as client:
            # Add a timeout
            r = await client.get(url, timeout=10.0) 
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error: {e.response.status_code} - {e.response.text}"}
    except httpx.RequestError as e:
        # Catch specific timeout error
        if isinstance(e, httpx.TimeoutException):
             return {"error": "API request timed out."}
        return {"error": f"Request Error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# In api_handler.py
async def get_soil_data(lat, lon):
    # OpenLandMap provides data layers for different properties
    # We will get pH and clay content
    layers = "phh2o_0-5cm_mean,clay_0-5cm_mean"

    # This is a Web Map Service (WMS) request URL
    url = (f"https://layers.openlandmap.org/sol/wms"
           f"?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo"
           f"&LAYERS={layers}&QUERY_LAYERS={layers}"
           f"&BBOX={lon-0.001},{lat-0.001},{lon+0.001},{lat+0.001}"
           f"&HEIGHT=1&WIDTH=1&INFO_FORMAT=application/json&SRS=EPSG:4326"
           f"&X=0&Y=0")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10.0)
            r.raise_for_status()

            data = r.json().get('features', [{}])[0].get('properties', {})

            # The values from this API are direct, no need to divide by 10
            ph_value = data.get('phh2o_0-5cm_mean')
            clay_content = data.get('clay_0-5cm_mean')

            return {
                "soil_ph": round(ph_value, 2) if ph_value is not None else "No data",
                "clay_percentage": round(clay_content, 2) if clay_content is not None else "No data"
            }
    except Exception as e:
        return {"error": str(e)}

# In api_handler.py
async def get_historical_weather(lat, lon):
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&past_days=90&daily=temperature_2m_mean,precipitation_sum&timezone=auto"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10.0)
            r.raise_for_status()
            data = r.json().get('daily', {})

            # --- ADD THIS CHECK ---
            temps = data.get('temperature_2m_mean', [])
            precip = data.get('precipitation_sum', [])

            # Ensure the lists are not empty before calculating
            if not temps or not precip:
                return {"error": "Received empty or invalid data from weather API."}
            # --- END OF CHECK ---

            return {
                "period_days": 90,
                "average_temperature_celsius": round(mean(temps), 2),
                "total_precipitation_mm": round(sum(precip), 2)
            }
    except Exception as e:
        return {"error": str(e)}