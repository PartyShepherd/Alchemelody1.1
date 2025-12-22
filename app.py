import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify

app = Flask(__name__)

LOCATION_FILE = "location.json"

PLANET_ORDER = [
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Saturn",
    "Jupiter",
    "Mars",
]

WEEKDAY_RULERS = {
    0: "Moon",
    1: "Mars",
    2: "Mercury",
    3: "Jupiter",
    4: "Venus",
    5: "Saturn",
    6: "Sun",
}


def load_location():
    if not os.path.exists(LOCATION_FILE):
        return {"latitude": 0, "longitude": 0}
    with open(LOCATION_FILE, "r") as f:
        return json.load(f)


def calculate_planetary_hours():
    now = datetime.now()

    sunrise = now.replace(hour=6, minute=0, second=0)
    sunset = now.replace(hour=18, minute=0, second=0)

    day_length = (sunset - sunrise) / 12
    night_length = (sunrise + timedelta(days=1) - sunset) / 12

    weekday_ruler = WEEKDAY_RULERS[now.weekday()]
    start_index = PLANET_ORDER.index(weekday_ruler)

    hours = []
    current_time = sunrise

    for i in range(12):
        planet = PLANET_ORDER[(start_index + i) % 7]
        hours.append({
            "planet": planet,
            "start": current_time.strftime("%H:%M"),
            "end": (current_time + day_length).strftime("%H:%M"),
            "sound": f"/static/sounds/{planet}.wav"
        })
        current_time += day_length

    current_time = sunset

    for i in range(12):
        planet = PLANET_ORDER[(start_index + 12 + i) % 7]
        hours.append({
            "planet": planet,
            "start": current_time.strftime("%H:%M"),
            "end": (current_time + night_length).strftime("%H:%M"),
            "sound": f"/static/sounds/{planet}.wav"
        })
        current_time += night_length

    return hours


@app.route("/")
def index():
    hours = calculate_planetary_hours()
    return render_template("index.html", hours=hours)


@app.route("/api/hours")
def api_hours():
    return jsonify(calculate_planetary_hours())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
