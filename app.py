import os
import json
import base64
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta, timezone
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# ------------------- Alarm Page Data -------------------
colors = {"Sun":"orange","Mars":"red","Venus":"green","Jupiter":"purple",
          "Moon":"blue","Mercury":"yellow","Saturn":"indigo"}
planets = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]

def calculate_planetary_hours(latitude, longitude):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable not set")

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

    for i in range(12):  # Day hours
        hours.append({
            "time_str": current_time.strftime("%I:%M %p"),
            "hour": current_time.hour,
            "minute": current_time.minute,
            "planet": planets[i % 7]
        })
        current_time += day_hour

    for i in range(12):  # Night hours
        hours.append({
            "time_str": current_time.strftime("%I:%M %p"),
            "hour": current_time.hour,
            "minute": current_time.minute,
            "planet": planets[(i + 12) % 7]
        })
        current_time += night_hour

    return hours

# ------------------- Routes -------------------

@app.route("/", methods=["GET", "POST"])
def index():
    # Load location.json if exists, else default to Pittsburgh
    try:
        with open("location.json","r") as f:
            location = json.load(f)
    except FileNotFoundError:
        location = {"latitude":40.4406,"longitude":-79.9959}

    if request.method == "POST":
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        if lat and lon:
            location = {"latitude": float(lat), "longitude": float(lon)}
            with open("location.json","w") as f:
                json.dump(location, f)

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

# ------------------- Planner -------------------
@app.route("/planner", methods=["GET", "POST"])
def planner():
    # Sample data for rituals
    rituals = ["Morning Prayer", "Evening Meditation", "Cleansing Ritual"]

    # Current date/time info
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")
    formatted_time = now.strftime("%H:%M")
    day_of_week = now.strftime("%A")
    elemental_quarter = "Air"  # Replace with your logic
    moon_phase = "Waxing Crescent"  # Replace with your logic
    weather = "Clear"  # Replace with API if needed
    planetary_hour = "Mars"  # Replace with your logic

    if request.method == "POST":
        # Here you would save the planner inputs
        physical_condition = request.form.get("physical_condition")
        tarot = request.form.get("tarot")
        meditation = request.form.get("meditation")
        selected_rituals = request.form.getlist("rituals")
        # Add saving logic here if desired

    return render_template(
        "planner.html",
        rituals=rituals,
        formatted_date=formatted_date,
        formatted_time=formatted_time,
        day_of_week=day_of_week,
        elemental_quarter=elemental_quarter,
        moon_phase=moon_phase,
        weather=weather,
        planetary_hour=planetary_hour
    )

# ------------------- Sigil Generator -------------------
@app.route("/sigils", methods=["GET", "POST"])
def sigils():
    sigil_image = None
    if request.method == "POST":
        word = request.form.get("word")
        if word:
            # Create a simple image with the word for demo
            img = Image.new("RGB", (400, 400), color="black")
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            draw.text((50, 180), word, fill="white", font=font)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            sigil_image = base64.b64encode(buffered.getvalue()).decode()

    return render_template("sigils.html", sigil_image=sigil_image)

# ------------------- Run App -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
