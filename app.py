from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import os
from flask_mail import Mail, Message
from flask import request, render_template
# ================= APP =================

app = Flask(__name__)
app.secret_key = "raa_super_secret_key"
# Email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'raa.earthquake.2.0@gmail.com'
app.config['MAIL_PASSWORD'] = 'soeg zmof dhse utjs'

mail = Mail(app)
# ================= DATABASE =================

database_url = os.environ.get("DATABASE_URL")

if database_url:
    database_url = database_url.replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= ADMIN =================

ADMIN_EMAILS = [
    "bharadwajrishav8434@gmail.com",
    "nitu9sharma9@gmail.com"
]

# ================= DATABASE MODEL =================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))

# Create database tables
with app.app_context():
    db.create_all()

# ================= HOME =================

@app.route("/")
def home():
    return render_template("index.html")

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

        user = User.query.filter_by(email=email, password=password).first()

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

    user = db.session.get(User, session["user_id"])

    return render_template("account.html", user=user)

# ================= INDIA EARTHQUAKES =================

@app.route("/india")
def india():

    try:

        end = datetime.utcnow()
        start = end - timedelta(days=30)

        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.date()}&endtime={end.date()}&minlatitude=6&maxlatitude=37&minlongitude=68&maxlongitude=97"

        data = requests.get(url).json()

        earthquakes = []

        for item in data["features"]:
            earthquakes.append({
                "place": item["properties"]["place"],
                "mag": item["properties"]["mag"],
                "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
            })

        return render_template("india.html", earthquakes=earthquakes)

    except:
        return render_template("india.html", earthquakes=[])



# ================= WORLD EARTHQUAKES =================
@app.route("/world", methods=["GET", "POST"])
def world():

    countries = [
        "All Countries",
        "Afghanistan","Albania","Algeria","Argentina","Armenia","Australia","Austria",
        "Azerbaijan","Bangladesh","Belgium","Bhutan","Brazil","Canada","Chile","China",
        "Denmark","Egypt","France","Germany","Greece","India","Indonesia","Iran",
        "Italy","Japan","Mexico","Nepal","Netherlands","New Zealand","Pakistan",
        "Philippines","Russia","Saudi Arabia","South Korea","Spain","Sri Lanka",
        "Sweden","Switzerland","Thailand","Turkey","Ukraine","United Kingdom",
        "United States","Vietnam"
    ]

    selected_country = request.form.get("country") if request.method == "POST" else "All Countries"

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=200&orderby=time"

    data = requests.get(url).json()

    earthquakes = []

    for item in data["features"]:

        place = item["properties"]["place"]

        # Skip filtering if "All Countries"
        if selected_country != "All Countries":
            if selected_country.lower() not in place.lower():
                continue

        earthquakes.append({
            "place": place,
            "mag": item["properties"]["mag"],
            "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
        })

    return render_template(
        "world.html",
        earthquakes=earthquakes,
        countries=countries,
        selected_country=selected_country
    )
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
        return "Access Denied ❌"

    return render_template("rishav.html")



# ================= ASIA EARTHQUAKES =================

@app.route("/asia", methods=["GET", "POST"])
def asia():

    countries = {
        "India": {"minlat": 6, "maxlat": 37, "minlon": 68, "maxlon": 97},
        "China": {"minlat": 18, "maxlat": 53, "minlon": 73, "maxlon": 135},
        "Japan": {"minlat": 24, "maxlat": 46, "minlon": 123, "maxlon": 146},
        "Nepal": {"minlat": 26, "maxlat": 31, "minlon": 80, "maxlon": 89},
        "Indonesia": {"minlat": -10, "maxlat": 6, "minlon": 95, "maxlon": 141},
        "Philippines": {"minlat": 5, "maxlat": 20, "minlon": 115, "maxlon": 130},
        "Thailand": {"minlat": 5, "maxlat": 20, "minlon": 97, "maxlon": 106}
    }

    selected_country = request.form.get("country") if request.method == "POST" else "India"
    region = countries[selected_country]

    end = datetime.utcnow()
    start = end - timedelta(days=30)

    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.date()}&endtime={end.date()}&minlatitude={region['minlat']}&maxlatitude={region['maxlat']}&minlongitude={region['minlon']}&maxlongitude={region['maxlon']}"

    data = requests.get(url).json()

    earthquakes = []

    for item in data["features"]:
        place = item["properties"]["place"]

        # Country filter
        if selected_country.lower() not in place.lower():
            continue

        earthquakes.append({
            "place": place,
            "mag": item["properties"]["mag"],
            "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
        })

    return render_template(
        "asia.html",
        earthquakes=earthquakes,
        countries=countries.keys(),
        selected_country=selected_country
    )



@app.route("/map")
def map():
    return render_template("map.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/edit_account", methods=["GET","POST"])
def edit_account():

    if not session.get("user_id"):
        return redirect("/login")

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.get(session["user_id"])

        if email:
            user.email = email

        if password:
            user.password = password

        db.session.commit()

        return redirect("/account")

    return render_template("edit_account.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        msg = Message(
            subject="New Contact Message",
            sender=app.config['MAIL_USERNAME'],
            recipients=["raa.earthquake.2.0@gmail.com"]
        )

        msg.body = f"""
New message from website

Name: {name}
Email: {email}

Message:
{message}
"""

        mail.send(msg)

        return render_template("contact.html", success=True)

    return render_template("contact.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")




@app.route("/ping")
def ping():
    return "ok"


# ================= RUN APP =================


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)