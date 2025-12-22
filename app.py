import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify

app = Flask(__name__)

LOCATION_FILE = "location.json"


# -----------------------------
# Location handling
# -----------------------------
def load_location():
    if not os.path.exists(LOCATION_FILE):
        default_location = {
            "latitude": 40.4406,
            "longitude": -79.9959,
            "name": "Pittsburgh"
        }
        with open(LOCATION_FILE, "w") as f:
            json.dump(default_location, f, indent=2)
        return default_location

    with open(LOCATION_FILE, "r") as f:
        return json.load(f)


# -----------------------------
# Planetary hours calculation
# -----------------------------
def calculate_planetary_hours(lat, lon):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY not set")

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={api_key}"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    # 🔒 HARD VALIDATION (prevents KeyError crashes)
    if (
        not isinstance(data, dict)
        or "sys" not in data
        or "sunrise" not in data["sys"]
        or "sunset" not in data["sys"]
    ):
        raise RuntimeError(f"Invalid OpenWeather response: {data}")

    sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"])
    sunset = datetime.utcfromtimestamp(data["sys"]["sunset"])

    day_length = (sunset - sunrise).total_seconds()
    planetary_hour_length = day_length / 12

    planets = [
        "Saturn",
        "Jupiter",
        "Mars",
        "Sun",
        "Venus",
