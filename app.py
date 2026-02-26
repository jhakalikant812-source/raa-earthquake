
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import os

# ================= APP =================

app = Flask(__name__)
app.secret_key = "raa_super_secret_key"

# ⭐ IMPORTANT FOR RENDER (uses DATABASE_URL if exists)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///users.db"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
@app.before_first_request
def create_tables():
    db.create_all()
# ================= ADMIN =================

ADMIN_EMAILS = [
    "bharadwajrishav8434@gmail.com",
    "nitu9sharma9@gmail.com"
]

# ================= DATABASE MODELS =================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500))
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ================= CREATE TABLES (FOR RENDER) =================



# ================= HOME =================

@app.route("/")
def home():
    alerts = Alert.query.order_by(Alert.date.desc()).all()

    for alert in alerts:
        alert.ist_time = alert.date + timedelta(hours=5, minutes=30)

    return render_template("index.html", alerts=alerts)

# ================= ESP8266 ALERT ROUTE =================

@app.route("/send_alert", methods=["POST"])
def send_alert():
    try:
        message = request.form.get("message")

        if not message:
            return "No Message", 400

        print("🚨 ALERT RECEIVED:", message)

        new_alert = Alert(message=message)
        db.session.add(new_alert)
        db.session.commit()

        return "OK", 200

    except Exception as e:
        print("ERROR:", e)
        return "SERVER ERROR", 500

# ================= SIGNUP =================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "Email already exists"

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["user_email"] = user.email

        return redirect("/")

    return render_template("signup.html")

# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:
            session["user_id"] = user.id
            session["user_email"] = user.email
            return redirect("/")

        return "Invalid login"

    return render_template("login.html")

# ================= LOGOUT =================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= ACCOUNT =================

@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    return render_template("account.html", user=user)

# ================= INDIA =================

@app.route("/india")
def india():
    end = datetime.utcnow()
    start = end - timedelta(days=30)

    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.date()}&endtime={end.date()}&minlatitude=6&maxlatitude=37&minlongitude=68&maxlongitude=97"

    data = requests.get(url).json()

    earthquakes = []

    for item in data["features"]:
        earthquakes.append({
            "place": item["properties"]["place"],
            "mag": item["properties"]["mag"],
            "time": datetime.fromtimestamp(
                item["properties"]["time"] / 1000
            )
        })

    return render_template("india.html", earthquakes=earthquakes)

# ================= WORLD =================

@app.route("/world")
def world():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=100&orderby=time"

    data = requests.get(url).json()

    earthquakes = []

    for item in data["features"]:
        earthquakes.append({
            "place": item["properties"]["place"],
            "mag": item["properties"]["mag"],
            "time": datetime.fromtimestamp(
                item["properties"]["time"] / 1000
            )
        })

    return render_template("world.html", earthquakes=earthquakes)

# ================= GUIDE =================

@app.route("/guide")
def guide():
    return render_template("guide.html")

# ================= ADMIN PANEL =================

@app.route("/rishav")
def rishav():
    if "user_email" not in session:
        return redirect("/login")

    if session["user_email"] not in ADMIN_EMAILS:
        return "Access Denied"

    return render_template("rishav.html")

# ================= RUN LOCAL SERVER =================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )
# =======
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
ADMIN_EMAILS = [
    "bharadwajrishav8434@gmail.com",
    "nitu9sharma9@gmail.com"
]


app = Flask(__name__)
app.secret_key = "raa_super_secret_key"
ADMIN_EMAILS = [
    "bharadwajrishav8434@gmail.com",
    "nitu9sharma9@gmail.com"
]

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ---------------- DATABASE ----------------

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

ADMIN_EMAILS = [
    "bharadwajrishav8434@gmail.com",
    "nitu9sharma9@gmail.com"
]

# ---------------- HOME ----------------

from datetime import timedelta

@app.route("/")
def home():
    alerts = Alert.query.order_by(Alert.date.desc()).all()

    # Convert UTC to IST
    for alert in alerts:
        alert.ist_time = alert.date + timedelta(hours=5, minutes=30)

    return render_template("index.html", alerts=alerts)

# alert

@app.route("/send_alert", methods=["POST"])
def send_alert():
    message = request.form.get("message")

    if message:
        new_alert = Alert(message=message)
        db.session.add(new_alert)
        db.session.commit()
        print("Alert saved to database")

    return "OK", 200
# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered."

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id   # login automatically

        return redirect("/")

    return render_template("signup.html")
# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session["user_id"] = user.id
            session["user_email"] = user.email
            print("Logged in:", session["user_email"])   # DEBUG
            return redirect("/")
        else:
            return "Invalid email or password"

    return render_template("login.html")

# ---------------- INDIA EARTHQUAKE ----------------

@app.route("/india")
def india():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date.date()}&endtime={end_date.date()}&minlatitude=6&maxlatitude=37&minlongitude=68&maxlongitude=97"

    response = requests.get(url)
    data = response.json()

    earthquakes = []

    for item in data["features"]:
        earthquakes.append({
            "place": item["properties"]["place"],
            "mag": item["properties"]["mag"],
            "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
        })

    return render_template("india.html", earthquakes=earthquakes)

# ---------------- WORLD EARTHQUAKE ----------------

@app.route("/world")
def world():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=100&orderby=time"
    data = requests.get(url).json()
    earthquakes = []

    for item in data["features"]:
        earthquakes.append({
            "place": item["properties"]["place"],
            "mag": item["properties"]["mag"],
            "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
        })

    return render_template("world.html", earthquakes=earthquakes)

# ---------------- ADMIN ALERT ----------------

@app.route("/admin", methods=["GET","POST"])
def admin():
    if "user" not in session or session["user"] not in ADMIN_EMAILS:
        return redirect("/login")

    if request.method == "POST":
        message = """BE ALERT THERE IS AN EARTHQUAKE NEAR YOU SO BE SAFE 
ONCE AGAIN THERE IS AN EARTHQUAKE BE SAFE"""

        users = User.query.all()

        for user in users:
            send_email(user.email, message)

        return "Alert Sent Successfully!"

    return render_template("admin.html")

# ---------------- EMAIL FUNCTION ----------------

def send_email(to_email, message):
    sender = "bharadwajrishav8434@gmail.com"
    password = "8434"

    msg = MIMEText(message)
    msg["Subject"] = "RAA EARTHQUAKE ALERT"
    msg["From"] = sender
    msg["To"] = to_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender, password)
    server.sendmail(sender, to_email, msg.as_string())
    server.quit()



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

ADMIN_EMAILS = [
    "bharadwajrishav8434@gmail.com",
    "nitu9sharma9@gmail.com"
]


@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    return render_template("account.html", user=user)


@app.route("/guide")
def guide():
    return render_template("guide.html")

# rishav

@app.route("/rishav")
def rishav():
    if "user_email" not in session:
        return redirect("/login")

    # Only admin emails allowed
    if session.get("user_email") not in [
        "bharadwajrishav8434@gmail.com",
        "nitu9sharma9@gmail.com"
    ]:
        return "Access Denied ❌"

    return render_template("rishav.html")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


