import os
import io
import json
import base64
import requests
import pytz
import numpy as np
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta, timezone
from matplotlib.patches import Circle

app = Flask(__name__)

# ---------------- Settings ----------------
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
RITUALS = ["LIRP", "RR", "LBRP", "LIRH", "MP", "GIRP", "GIRH", "RC"]

colors = {
    "Sun":"orange","Mars":"red","Venus":"green",
    "Jupiter":"purple","Moon":"blue",
    "Mercury":"yellow","Saturn":"indigo"
}
planets = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]

# ---------------- Planner Helpers ----------------
def get_elemental_quarter():
    h = datetime.now(pytz.timezone("US/Eastern")).hour
    if h < 6: return "Earth (12 AM - 6 AM)"
    if h < 12: return "Air (6 AM - 12 PM)"
    if h < 18: return "Fire (12 PM - 6 PM)"
    return "Water (6 PM - 12 AM)"

def get_moon_phase():
    try:
        ref = datetime(2000,1,6,12,24,tzinfo=pytz.utc)
        now = datetime.now(pytz.utc)
        days = (now-ref).total_seconds()/86400
        phase = (days % 29.53058867) / 29.53058867
        if phase < 0.03 or phase > 0.97: return "New Moon"
        if phase < 0.25: return "Waxing Crescent"
        if phase < 0.27: return "First Quarter"
        if phase < 0.5: return "Waxing Gibbous"
        if phase < 0.53: return "Full Moon"
        if phase < 0.75: return "Waning Gibbous"
        if phase < 0.77: return "Last Quarter"
        return "Waning Crescent"
    except:
        return "Unavailable"

def get_weather():
    if not OPENWEATHER_API_KEY:
        return "Weather unavailable"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Pittsburgh,US&appid={OPENWEATHER_API_KEY}&units=metric"
        d = requests.get(url).json()
        f = (d["main"]["temp"] * 9/5) + 32
        return f"{f:.1f}°F, {d['weather'][0]['description'].capitalize()}"
    except:
        return "Weather unavailable"

def get_planetary_hour():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Pittsburgh,US&appid={OPENWEATHER_API_KEY}"
        d = requests.get(url).json()
        tz = timezone(timedelta(seconds=d["timezone"]))
        sunrise = datetime.utcfromtimestamp(d["sys"]["sunrise"]).replace(tzinfo=timezone.utc).astimezone(tz)
        sunset = datetime.utcfromtimestamp(d["sys"]["sunset"]).replace(tzinfo=timezone.utc).astimezone(tz)
        now = datetime.now(tz)
        day_len = (sunset - sunrise) / 12
        night_len = (timedelta(hours=24) - (sunset - sunrise)) / 12
        day_planets = planets
        if sunrise <= now < sunset:
            i = int((now - sunrise) / day_len)
            return day_planets[i % 7]
        i = int((now - sunset) / night_len)
        return day_planets[(i + 12) % 7]
    except:
        return "Unavailable"

# ---------------- Sigil Generator ----------------
letter_mapping = {
    "A":[("A","#FFFF00")],"B":[("B","#FFFF00")],"C":[("G","#0000FF")],
    "D":[("D","#008000")],"E":[("A","#FFFF00")],"F":[("F","#FF0000")],
    "G":[("G","#0000FF")],"H":[("H","#FF0000")],"I":[("I","#9ACD32")],
    "J":[("I","#9ACD32")],"K":[("K","#800080")],"L":[("L","#008000")],
    "M":[("M","#0000FF")],"N":[("N","#20B2AA")],"O":[("O","#4B0082")],
    "P":[("P","#FF0000")],"Q":[("Q","#9400D3")],"R":[("R","#FFA500")],
    "S":[("S","#FF4500")],"T":[("T","#FFFF00")],"U":[("V","#FF4500")],
    "V":[("V","#FF4500")],"W":[("V","#FF4500")],"X":[("X","#800080")],
    "Y":[("I","#9ACD32")],"Z":[("Z","#FFA500")]
}

def draw_rose_sigil(word):
    word = [c for c in word.upper() if c in letter_mapping]
    positions = {c:(np.cos(i*2*np.pi/len(letter_mapping)), np.sin(i*2*np.pi/len(letter_mapping)))
                 for i,c in enumerate(letter_mapping)}
    fig, ax = plt.subplots(figsize=(6,6))
    prev=None
    for c in word:
        x,y=positions[c]
        col=letter_mapping[c][0][1]
        ax.text(x,y,c,color=col,ha="center",va="center",fontsize=14)
        if prev:
            ax.plot([prev[0],x],[prev[1],y],color=col,lw=2)
        prev=(x,y)
    ax.set_aspect("equal")
    ax.axis("off")
    buf=io.BytesIO()
    plt.savefig(buf,format="png")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ---------------- Routes ----------------

@app.route("/", methods=["GET","POST"])
def index():
    try:
        with open("location.json") as f:
            location=json.load(f)
    except:
        location={"latitude":40.4406,"longitude":-79.9959}

    if request.method=="POST":
        location={"latitude":float(request.form["latitude"]),
                  "longitude":float(request.form["longitude"])}
        with open("location.json","w") as f:
            json.dump(location,f)

    return render_template("index.html", hours=[], colors=colors, location=location)

@app.route("/planner", methods=["GET","POST"])
def planner():
    now = datetime.now(pytz.timezone("US/Eastern"))
    return render_template(
        "planner.html",
        formatted_date=now.strftime("%b. %d, %Y"),
        formatted_time=now.strftime("%I:%M %p"),
        day_of_week=now.strftime("%A"),
        elemental_quarter=get_elemental_quarter(),
        moon_phase=get_moon_phase(),
        weather=get_weather(),
        planetary_hour=get_planetary_hour(),
        rituals=RITUALS
    )

@app.route("/sigils", methods=["GET","POST"])
def sigils():
    img=None
    if request.method=="POST":
        word=request.form.get("word","")
        if word:
            img=draw_rose_sigil(word)
    return render_template("sigils.html", sigil_image=img)

@app.route("/play", methods=["POST"])
def play():
    return jsonify({"ok":True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
