from flask import Flask, render_template, request, send_file, jsonify
from datetime import datetime, timedelta, timezone
import pytz
import os
import io
import json
import base64
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

app = Flask(__name__)

# ===============================
# SHARED CONFIG
# ===============================
LOCATION = "Pittsburgh, US"
LOG_FOLDER = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
API_KEY = os.environ.get("API_KEY", "")

# ===============================
# -------- PLANNER LOGIC --------
# ===============================
RITUALS = ["LIRP","RR","LBRP","LIRH","MP","GIRP","GIRH","RC"]

def get_elemental_quarter():
    hour = datetime.now(pytz.timezone("US/Eastern")).hour
    if hour < 6: return "Earth"
    if hour < 12: return "Air"
    if hour < 18: return "Fire"
    return "Water"

def get_moon_phase():
    ref = datetime(2000,1,6,12,24,tzinfo=pytz.utc)
    now = datetime.now(pytz.timezone("US/Eastern")).astimezone(pytz.utc)
    days = (now - ref).total_seconds() / 86400
    phase = (days % 29.53058867) / 29.53058867
    if phase < 0.03 or phase > 0.97: return "New Moon"
    if phase < 0.25: return "Waxing Crescent"
    if phase < 0.27: return "First Quarter"
    if phase < 0.50: return "Waxing Gibbous"
    if phase < 0.53: return "Full Moon"
    if phase < 0.75: return "Waning Gibbous"
    if phase < 0.77: return "Last Quarter"
    return "Waning Crescent"

def get_weather():
    if not OPENWEATHER_API_KEY:
        return "Weather unavailable"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={OPENWEATHER_API_KEY}&units=imperial"
    data = requests.get(url).json()
    if "main" not in data:
        return "Weather unavailable"
    return f"{data['main']['temp']:.1f}°F, {data['weather'][0]['description']}"

# ===============================
# -------- SIGIL LOGIC ----------
# ===============================
# (unchanged, trimmed for clarity — your existing draw_rose_sigil goes here)
# USE YOUR EXACT FUNCTION HERE
# ===============================

# ===============================
# -------- ALARM LOGIC ----------
# ===============================
colors = {
    "Sun":"orange","Mars":"red","Venus":"green",
    "Jupiter":"purple","Moon":"blue","Mercury":"yellow","Saturn":"indigo"
}
planets = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]

def calculate_planetary_hours(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
    data = requests.get(url).json()
    tz = timezone(timedelta(seconds=data["timezone"]))
    sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"]).astimezone(tz)
    sunset = datetime.utcfromtimestamp(data["sys"]["sunset"]).astimezone(tz)

    day_len = (sunset - sunrise) / 12
    night_len = (timedelta(hours=24) - (sunset - sunrise)) / 12

    hours, t = [], sunrise
    for i in range(24):
        hours.append({
            "time_str": t.strftime("%I:%M %p"),
            "hour": t.hour,
            "minute": t.minute,
            "planet": planets[i % 7]
        })
        t += day_len if i < 12 else night_len
    return hours

# ===============================
# -------- ROUTES ---------------
# ===============================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/planner", methods=["GET","POST"])
def planner():
    now = datetime.now(pytz.timezone("US/Eastern"))
    if request.method == "POST":
        log = request.form.to_dict(flat=False)
        filename = f"log_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(LOG_FOLDER, filename)
        with open(path,"w") as f:
            for k,v in log.items():
                f.write(f"{k}: {v}\n")
        return send_file(path, as_attachment=True)
    return render_template(
        "planner.html",
        formatted_date=now.strftime("%b %d, %Y"),
        formatted_time=now.strftime("%I:%M %p"),
        day_of_week=now.strftime("%A"),
        elemental_quarter=get_elemental_quarter(),
        moon_phase=get_moon_phase(),
        weather=get_weather(),
        rituals=RITUALS
    )

@app.route("/sigils", methods=["GET","POST"])
def sigils():
    img = None
    if request.method == "POST":
        img = draw_rose_sigil(request.form["word"])
    return render_template("sigils.html", sigil_image=img)

@app.route("/alarm", methods=["GET","POST"])
def alarm():
    location = {"latitude":40.4406,"longitude":-79.9959}
    if os.path.exists("location.json"):
        location = json.load(open("location.json"))
    if request.method == "POST":
        location["latitude"] = float(request.form["latitude"])
        location["longitude"] = float(request.form["longitude"])
        json.dump(location, open("location.json","w"))
    hours = calculate_planetary_hours(location["latitude"], location["longitude"])
    return render_template("alarm.html", hours=hours, colors=colors, location=location)

@app.route("/play", methods=["POST"])
def play():
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
