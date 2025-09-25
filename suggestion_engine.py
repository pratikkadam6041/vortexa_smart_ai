# suggestion_engine.py

def suggest_crops(soil_data: dict, historical_weather: dict) -> list[str]:
    """
    Analyzes soil and climate data to suggest suitable crops.
    """
    
    suggested_crops = []

    # Get the key environmental data
    soil_ph = soil_data.get("soil_ph", "No data")
    clay_percentage = soil_data.get("clay_percentage", "No data")
    avg_temp = historical_weather.get("average_temperature_celsius", "No data")
    total_precip = historical_weather.get("total_precipitation_mm", "No data")

    # --- Rule-Based Suggestion Logic ---
    # This is a simple, rule-based system. In a real-world scenario, 
    # you might use a machine learning model or a more detailed database.

    # Rule 1: Temperature and Precipitation
    if isinstance(avg_temp, (int, float)) and isinstance(total_precip, (int, float)):
        # High rainfall and warm climate
        if avg_temp > 25 and total_precip > 200:
            suggested_crops.append("Rice")
            suggested_crops.append("Sugarcane")
        # Moderate temperature and rainfall
        if 15 <= avg_temp <= 25 and 100 <= total_precip <= 200:
            suggested_crops.append("Wheat")
            suggested_crops.append("Maize")
        # Cold climate
        if avg_temp < 15:
            suggested_crops.append("Barley")
            suggested_crops.append("Potatoes")

    # Rule 2: Soil pH
    if isinstance(soil_ph, (int, float)):
        # Acidic soil
        if soil_ph < 6.0:
            suggested_crops.append("Blueberries")
            suggested_crops.append("Oats")
        # Neutral to slightly alkaline soil
        if 6.0 <= soil_ph <= 7.5:
            suggested_crops.append("Soybeans")
            suggested_crops.append("Corn")
            suggested_crops.append("Alfalfa")
        # Highly alkaline soil
        if soil_ph > 7.5:
            suggested_crops.append("Asparagus")
            suggested_crops.append("Cabbage")
            
    # Rule 3: Clay Content (Soil Type)
    if isinstance(clay_percentage, (int, float)):
        # High clay content (heavy soil)
        if clay_percentage > 40:
            # Clay-rich soils retain water well, good for crops that need constant moisture
            suggested_crops.append("Rice")
            suggested_crops.append("Flax")
        # Sandy soil (low clay content)
        if clay_percentage < 10:
            # Sandy soils drain quickly, suitable for root vegetables
            suggested_crops.append("Carrots")
            suggested_crops.append("Peanuts")

    # Remove duplicates
    return list(set(suggested_crops))