from flask import Flask, render_template

app = Flask(__name__)

# ---------------- HOME / ALARM ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- PLANNER ----------------
@app.route("/planner")
def planner():
    return render_template("planner.html")

# ---------------- SIGIL ----------------
@app.route("/sigil")
def sigil():
    return render_template("sigil.html")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
