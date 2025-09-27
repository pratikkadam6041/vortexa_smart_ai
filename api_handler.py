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

async def get_soil_data(lat, lon):
    url = f"https://rest.soilgrids.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o,clay&depth=0-5cm&value=mean"
    try:
        async with httpx.AsyncClient() as client:
            # Add a timeout
            r = await client.get(url, timeout=10.0)
            r.raise_for_status()
            props = r.json().get('properties', {}).get('layers', [{}])[0].get('depths', [{}])[0].get('values', {})
            ph = props.get('phh2o', {}).get('mean', -1)
            clay = props.get('clay', {}).get('mean', -1)
            return {"soil_ph": ph / 10.0 if ph != -1 else "No data",
                    "clay_percentage": clay / 10.0 if clay != -1 else "No data"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error: {e.response.status_code} - {e.response.text}"}
    except httpx.RequestError as e:
        if isinstance(e, httpx.TimeoutException):
             return {"error": "API request timed out."}
        return {"error": f"Request Error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

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