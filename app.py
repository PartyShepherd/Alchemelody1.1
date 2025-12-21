from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import requests
import os

app = Flask(__name__)

# Define planetary hour colors
colors = {
    "Sun": "orange",
    "Mars": "red",
    "Venus": "green",
    "Jupiter": "purple",
    "Moon": "blue",
    "Mercury": "yellow",
    "Saturn": "indigo"
}

planets = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

# Helper to calculate planetary hours
def calculate_planetary_hours(latitude, longitude):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable not set")

    # Get sunrise and sunset times from OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"])
    sunset = datetime.utcfromtimestamp(data["sys"]["sunset"])
    day_duration = sunset - sunrise

    day_hour = day_duration / 12
    night_duration = timedelta(hours=24) - day_duration
    night_hour = night_duration / 12

    hours = []
    current_time = sunrise

    # Calculate daytime planetary hours
    for i in range(12):
        hours.append((current_time.strftime("%I:%M %p"), planets[i % 7]))
        current_time += day_hour

    # Calculate nighttime planetary hours
    for i in range(12):
        hours.append((current_time.strftime("%I:%M %p"), planets[(i + 12) % 7]))
        current_time += night_hour

    return hours

@app.route("/", methods=["GET", "POST"])
def index():
    # Load saved location or use default
    try:
        with open("location.json", "r") as f:
            location = json.load(f)
    except FileNotFoundError:
        location = {"latitude": 40.4406, "longitude": -79.9959}  # Pittsburgh default

    # Handle location updates
    if request.method == "POST":
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        if latitude and longitude:
            location = {"latitude": float(latitude), "longitude": float(longitude)}
            with open("location.json", "w") as f:
                json.dump(location, f)

    # Calculate planetary hours
    hours = calculate_planetary_hours(location["latitude"], location["longitude"])
    return render_template("index.html", hours=hours, colors=colors, location=location)

@app.route("/play", methods=["POST"])
def play_sound():
    data = request.get_json()
    planet = data.get("planet")
    if not planet:
        return jsonify({"message": "No planet provided"}), 400

    # Debug: server-side playback
    print(f"Playing sound for {planet}")
    return jsonify({"message": f"Playing sound for {planet}"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
