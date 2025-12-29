import os
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta, timezone
import requests

app = Flask(__name__)

# ------------------- Planetary Data -------------------
colors = {
    "Sun":"orange","Mars":"red","Venus":"green","Jupiter":"purple",
    "Moon":"blue","Mercury":"yellow","Saturn":"indigo"
}

planets = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]

# ------------------- Planetary Hours -------------------
def calculate_planetary_hours(latitude, longitude):
    api_key = os.environ.get("API_KEY")

    # Fallback if API_KEY is missing (prevents 500)
    if not api_key:
        now = datetime.now()
        return [{
            "time_str": now.strftime("%I:%M %p"),
            "hour": now.hour,
            "minute": now.minute,
            "planet": planets[i % 7]
        } for i in range(24)]

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    data = requests.get(url).json()

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

    for i in range(12):
        hours.append({
            "time_str": current_time.strftime("%I:%M %p"),
            "hour": current_time.hour,
            "minute": current_time.minute,
            "planet": planets[i % 7]
        })
        current_time += day_hour

    for i in range(12):
        hours.append({
            "time_str": current_time.strftime("%I:%M %p"),
            "hour": current_time.hour,
            "minute": current_time.minute,
            "planet": planets[(i + 12) % 7]
        })
        current_time += night_hour

    return hours

# ------------------- Alarm Page -------------------
@app.route("/", methods=["GET","POST"])
def index():
    try:
        with open("location.json","r") as f:
            location = json.load(f)
    except:
        location = {"latitude":40.4406,"longitude":-79.9959}

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
    return jsonify({"message": f"Playing {data.get('planet','Unknown')}"})

# ------------------- Planner -------------------
@app.route("/planner", methods=["GET","POST"])
def planner():
    rituals = ["Morning Prayer", "Evening Meditation", "Cleansing Ritual"]

    now = datetime.now()
    return render_template(
        "planner.html",
        rituals=rituals,
        formatted_date=now.strftime("%Y-%m-%d"),
        formatted_time=now.strftime("%H:%M"),
        day_of_week=now.strftime("%A"),
        elemental_quarter="Air",
        moon_phase="Waxing Crescent",
        weather="Clear",
        planetary_hour="Mars"
    )

# ------------------- Sigils -------------------
@app.route("/sigils", methods=["GET","POST"])
def sigils():
    # Image generation intentionally disabled for stability
    return render_template("sigils.html", sigil_image=None)

# ------------------- Run -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
