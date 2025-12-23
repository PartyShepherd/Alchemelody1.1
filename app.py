import os
import json
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

colors = {
    "Sun": "orange",
    "Mars": "red",
    "Venus": "green",
    "Jupiter": "purple",
    "Moon": "blue",
    "Mercury": "yellow",
    "Saturn": "indigo",
}

planets = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]


def load_location():
    try:
        with open("location.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"latitude": 40.4406, "longitude": -79.9959}  # Pittsburgh


def calculate_planetary_hours(lat, lon):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY not set")

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={api_key}"
    )
    data = requests.get(url).json()

    tz_offset = data["timezone"]  # seconds
    tz = timezone(timedelta(seconds=tz_offset))

    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"], tz)
    sunset = datetime.fromtimestamp(data["sys"]["sunset"], tz)

    day_len = (sunset - sunrise) / 12
    night_len = (timedelta(hours=24) - (sunset - sunrise)) / 12

    hours = []
    t = sunrise

    for i in range(12):
        hours.append({
            "start": t.isoformat(),
            "planet": planets[i % 7]
        })
        t += day_len

    for i in range(12):
        hours.append({
            "start": t.isoformat(),
            "planet": planets[(i + 12) % 7]
        })
        t += night_len

    return hours


@app.route("/")
def index():
    location = load_location()
    hours = calculate_planetary_hours(location["latitude"], location["longitude"])
    return render_template(
        "index.html",
        hours=hours,
        colors=colors,
        location=location
    )


@app.route("/current_hour")
def current_hour():
    location = load_location()
    hours = calculate_planetary_hours(location["latitude"], location["longitude"])

    now = datetime.now(timezone.utc)
    active = hours[-1]

    for h in hours:
        start = datetime.fromisoformat(h["start"])
        if now >= start:
            active = h

    return jsonify(active)
