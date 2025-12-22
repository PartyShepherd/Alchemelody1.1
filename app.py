from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os
import requests

app = Flask(__name__)

# Planet colors
colors = {
    "Sun": "orange",
    "Mars": "red",
    "Venus": "green",
    "Jupiter": "purple",
    "Moon": "blue",
    "Mercury": "yellow",
    "Saturn": "indigo"
}

# Planetary order
planets = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

# Calculate planetary hours
def calculate_planetary_hours(latitude, longitude):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY not set")

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&appid={api_key}"
    )
    data = requests.get(url).json()

    sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"])
    sunset = datetime.utcfromtimestamp(data["sys"]["sunset"])

    day_duration = sunset - sunrise
    night_duration = timedelta(hours=24) - day_duration

    day_hour = day_duration / 12
    night_hour = night_duration / 12

    hours = []
    current_time = sunrise

    for i in range(12):
        hours.append((current_time.strftime("%H:%M"), planets[i % 7]))
        current_time += day_hour

    for i in range(12):
        hours.append((current_time.strftime("%H:%M"), planets[(i + 12) % 7]))
        current_time += night_hour

    return hours


@app.route("/", methods=["GET", "POST"])
def index():
    location_file = "location.json"

    if os.path.exists(location_file):
        with open(location_file, "r") as f:
            location = json.load(f)
    else:
        location = {"latitude": 40.4406, "longitude": -79.9959}

    if request.method == "POST":
        location = {
            "latitude": float(request.form["latitude"]),
            "longitude": float(request.form["longitude"]),
        }
        with open(location_file, "w") as f:
            json.dump(location, f)

    hours = calculate_planetary_hours(
        location["latitude"], location["longitude"]
    )

    return render_template(
        "index.html",
        hours=hours,
        colors=colors,
        location=location,
    )


@app.route("/play", methods=["POST"])
def play_sound():
    data = request.get_json()
    planet = data.get("planet")
    return jsonify({"message": f"Playing sound for {planet}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
