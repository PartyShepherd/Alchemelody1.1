from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Static sounds folder
SOUNDS_FOLDER = os.path.join("static", "sounds")


# Dummy planetary hours calculation
def calculate_planetary_hours():
    # Return 24 hours with dummy planet names
    planets = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
        "Saturn", "Sun", "Moon", "Mars", "Mercury", "Jupiter",
        "Venus", "Saturn", "Sun", "Moon", "Mars", "Mercury",
        "Jupiter", "Venus", "Saturn", "Sun", "Moon", "Mars"
    ]
    hours_list = []
    now = datetime.now()
    for i, planet in enumerate(planets):
        hour_time = (now + timedelta(hours=i)).strftime("%H:%M")
        hours_list.append({"planet": planet, "time": hour_time})
    return hours_list


@app.route("/")
def index():
    hours = calculate_planetary_hours()
    location = {"latitude": 0, "longitude": 0}  # dummy location for template
    return render_template("index.html", hours=hours, location=location)


@app.route("/play_sound/<sound_name>")
def play_sound(sound_name):
    try:
        return send_from_directory(SOUNDS_FOLDER, sound_name)
    except Exception as e:
        return str(e), 404


if __name__ == "__main__":
    app.run(debug=True)
