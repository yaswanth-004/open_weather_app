import os
import json
import requests
from datetime import datetime


GEO_URL     = "https://nominatim.openstreetmap.org/search"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL= "https://api.openweathermap.org/data/2.5/forecast"


def get_coordinates(country, city, zip_code=None):
    """
    Uses Nominatim to get lat/lon.
    Returns (lat, lon, display_name) or raises ValueError.
    Handles both list responses and single JSON responses.
    """
    query = f"{city},{country}"
    if zip_code:
        query = f"{zip_code},{city},{country}"

    headers = {
        "User-Agent": "WeatherApp/1.0",
        "Accept":     "application/json"
    }
    params = {"q": query, "format": "json", "limit": 1}

    resp = requests.get(GEO_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    # Nominatim returns a LIST — handle both list and dict
    if isinstance(data, list):
        if not data:
            raise ValueError(f"Location not found: {query}")
        location = data[0]
    elif isinstance(data, dict):
        location = data
    else:
        raise ValueError("Unexpected response from geocoding API")

    lat = float(location["lat"])
    lon = float(location["lon"])
    name = location.get("display_name", query)
    return lat, lon, name


def get_today_weather(lat, lon):
    """
    Fetches current weather from OpenWeatherMap.
    Returns parsed dict with all useful fields.
    """
    api_key = os.getenv("openweatherapi")
    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": api_key,
        "units": "metric"
    }

    session = requests.Session()
    resp = session.get(WEATHER_URL, params=params, timeout=10)
    resp.raise_for_status()

    raw = resp.json()

    # Parse into clean dict for templates
    return {
        "city":        raw.get("name", "Unknown"),
        "country":     raw.get("sys", {}).get("country", ""),
        "temp":        raw["main"]["temp"],
        "feels_like":  raw["main"]["feels_like"],
        "temp_min":    raw["main"]["temp_min"],
        "temp_max":    raw["main"]["temp_max"],
        "humidity":    raw["main"]["humidity"],
        "pressure":    raw["main"]["pressure"],
        "description": raw["weather"][0]["description"].title(),
        "icon":        raw["weather"][0]["icon"],
        "wind_speed":  raw.get("wind", {}).get("speed", 0),
        "wind_deg":    raw.get("wind", {}).get("deg", 0),
        "visibility":  raw.get("visibility", 0),
        "clouds":      raw.get("clouds", {}).get("all", 0),
        "sunrise":     datetime.utcfromtimestamp(
                           raw["sys"]["sunrise"]).strftime("%H:%M UTC"),
        "sunset":      datetime.utcfromtimestamp(
                           raw["sys"]["sunset"]).strftime("%H:%M UTC"),
        "timestamp":   datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "raw_json":    json.dumps(raw, indent=2),
    }


def get_forecast(lat, lon):
    """
    Fetches 5-day / 3-hour forecast from OpenWeatherMap.
    Returns list of daily summaries (one per day, 5 days).
    """
    api_key = os.getenv("openweatherapi")
    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": api_key,
        "units": "metric",
        "cnt":   40   # 5 days × 8 readings per day
    }

    session = requests.Session()
    resp = session.get(FORECAST_URL, params=params, timeout=10)
    resp.raise_for_status()

    raw = resp.json()
    items = raw.get("list", [])

    # Group by date → pick midday reading (12:00)
    days = {}
    for item in items:
        dt_txt = item["dt_txt"]           # "2024-06-14 12:00:00"
        day    = dt_txt.split(" ")[0]
        hour   = dt_txt.split(" ")[1]
        if day not in days:
            days[day] = item             # take first available
        if "12:00:00" in hour:
            days[day] = item             # prefer midday

    result = []
    for day, item in sorted(days.items())[:5]:
        result.append({
            "date":        day,
            "temp":        item["main"]["temp"],
            "temp_min":    item["main"]["temp_min"],
            "temp_max":    item["main"]["temp_max"],
            "humidity":    item["main"]["humidity"],
            "description": item["weather"][0]["description"].title(),
            "icon":        item["weather"][0]["icon"],
            "wind_speed":  item.get("wind", {}).get("speed", 0),
            "pop":         round(item.get("pop", 0) * 100),  # rain probability %
        })

    return result, json.dumps(raw, indent=2)


def analyze_weather(weather_data):
    """
    Post-processing analyzer — generates a human-readable
    summary and advice based on the weather data.
    """
    advice = []
    temp        = weather_data["temp"]
    humidity    = weather_data["humidity"]
    wind_speed  = weather_data["wind_speed"]
    description = weather_data["description"].lower()

    # Temperature advice
    if temp < 5:
        advice.append("🥶 Very cold — wear a heavy coat and gloves.")
    elif temp < 15:
        advice.append("🧥 Cool weather — a jacket is recommended.")
    elif temp < 25:
        advice.append("😊 Pleasant temperature — comfortable outdoors.")
    elif temp < 35:
        advice.append("☀️ Warm day — stay hydrated.")
    else:
        advice.append("🔥 Very hot — avoid prolonged sun exposure.")

    # Humidity advice
    if humidity > 80:
        advice.append("💧 High humidity — it will feel hotter than it is.")
    elif humidity < 30:
        advice.append("🌵 Low humidity — keep a water bottle with you.")

    # Wind advice
    if wind_speed > 10:
        advice.append("💨 Strong winds — secure loose items outdoors.")

    # Condition advice
    if "rain" in description:
        advice.append("☔ Rain expected — carry an umbrella.")
    elif "snow" in description:
        advice.append("❄️ Snow — dress warmly and drive carefully.")
    elif "storm" in description or "thunder" in description:
        advice.append("⛈️ Storm warning — stay indoors if possible.")
    elif "clear" in description:
        advice.append("🌞 Clear sky — great day to go outside.")
    elif "cloud" in description:
        advice.append("☁️ Cloudy — no rain expected but light jacket helps.")

    weather_data["advice"] = advice
    return weather_data