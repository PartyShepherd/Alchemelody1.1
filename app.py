import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Planetary colors
colors = {
    "Sun": "orange",
    "Mars": "red",
    "Venus": "green",
    "Jupiter": "purple",
    "Moon": "blue",
    "Mercury": "yellow",
    "Saturn": "indigo"
}

# Chaldean order
planets = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]


def calculate_planetary_hours(latitude, longitude):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable not set")

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
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

    # Day hours
    for i in range(12):
        hours.append((current_time, planets[i % 7]))
        current_time += day_hour

    # Night hours
    for i in range(12):
        hours.append((current_time, planets[(i + 12) % 7]))
        current_time += night_hour

    return hours


@app.route("/", methods=["GET", "POST"])
def index():
    # Load saved location or default
    try:
        with open("location.json", "r") as f:
            location = json.load(f)
    except FileNotFoundError:
        location = {"latitude": 40.4406, "longitude": -79.9959}

    if request.method == "POST":
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        if lat and lon:
            location = {"latitude": float(lat), "longitude": float(lon)}
            with open("location.json", "w") as f:
                json.dump(location, f)

    raw_hours = calculate_planetary_hours(
        location["latitude"], location["longitude"]
    )

    # Convert datetime → display string
    hours = [(h[0].strftime("%I:%M %p"), h[1]) for h in raw_hours]

    return render_template(
        "index.html",
        hours=hours,
        colors=colors,
        location=location
    )


@app.route("/play", methods=["POST"])
def play_sound():
    data = request.get_json()
    planet = data.get("planet")
    if not planet:
        return jsonify({"message": "No planet provided"}), 400

    print(f"Manual play triggered for {planet}")
    return jsonify({"message": f"Playing {planet}"}), 200


@app.route("/current-planet")
def current_planet():
    try:
        with open("location.json", "r") as f:
            location = json.load(f)
    except FileNotFoundError:
        location = {"latitude": 40.4406, "longitude": -79.9959}

    hours = calculate_planetary_hours(
        location["latitude"], location["longitude"]
    )

    now = datetime.utcnow()

    for i in range(len(hours) - 1):
        start = hours[i][0]
        end = hours[i + 1][0]
        if start <= now < end:
            planet = hours[i][1]
            return jsonify({
                "planet": planet,
                "color": colors[planet]
            })

    # Fallback (should never hit, but safe)
    planet = hours[0][1]
    return jsonify({
        "planet": planet,
        "color": colors[planet]
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
