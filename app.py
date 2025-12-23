import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta, timezone
import json
import requests

app = Flask(__name__)

# Planetary hour colors and order
colors = {"Sun":"orange","Mars":"red","Venus":"green","Jupiter":"purple","Moon":"blue","Mercury":"yellow","Saturn":"indigo"}
planets = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]

def calculate_planetary_hours(latitude, longitude):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable not set")

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    data = requests.get(url).json()

    # Get timezone offset in seconds
    tz_offset = data.get("timezone", 0)
    tz = timezone(timedelta(seconds=tz_offset))

    sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"]).replace(tzinfo=timezone.utc).astimezone(tz)
    sunset = datetime.utcfromtimestamp(data["sys"]["sunset"]).replace(tzinfo=timezone.utc).astimezone(tz)

    day_duration = sunset - sunrise
    day_hour = day_duration / 12
    night_duration = timedelta(hours=24) - day_duration
    night_hour = night_duration / 12

    hours = []
    current_time = sunrise

    # Daytime hours
    for i in range(12):
        hours.append({
            "time_str": current_time.strftime("%I:%M %p"),
            "hour": current_time.hour,
            "minute": current_time.minute,
            "planet": planets[i % 7]
        })
        current_time += day_hour

    # Nighttime hours
    for i in range(12):
        hours.append({
            "time_str": current_time.strftime("%I:%M %p"),
            "hour": current_time.hour,
            "minute": current_time.minute,
            "planet": planets[(i + 12) % 7]
        })
        current_time += night_hour

    return hours

@app.route("/", methods=["GET","POST"])
def index():
    # Load location.json if exists, else default
    try:
        with open("location.json","r") as f:
            location = json.load(f)
    except FileNotFoundError:
        location = {"latitude":40.4406,"longitude":-79.9959}  # Pittsburgh default

    if request.method == "POST":
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        if lat and lon:
            location = {"latitude":float(lat),"longitude":float(lon)}
            with open("location.json","w") as f:
                json.dump(location,f)

    hours = calculate_planetary_hours(location["latitude"], location["longitude"])
    return render_template("index.html", hours=hours, colors=colors, location=location)

@app.route("/play", methods=["POST"])
def play_sound():
    data = request.get_json()
    planet = data.get("planet")
    if not planet:
        return jsonify({"message":"No planet provided"}), 400
    print(f"Playing sound for {planet}")
    return jsonify({"message":f"Playing sound for {planet}"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
