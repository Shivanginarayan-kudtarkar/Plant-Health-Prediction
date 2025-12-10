import pandas as pd
import numpy as np
from flask import Flask, render_template, request, session, redirect, url_for, flash
import pickle
import uuid
import mysql.connector
from werkzeug.security import generate_password_hash
from hashlib import sha256

# -------------------------------------------------
# Flask App Setup
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = "Shivani123"

# -------------------------------------------------
# Load Plant Health Classifier Model
# -------------------------------------------------
with open("plant_health.pkl", "rb") as f:
    model = pickle.load(f)

# -------------------------------------------------
# MySQL Connection Config
# -------------------------------------------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "plant_health_db"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

# -------------------------------------------------
# Prediction Function for Plant Health Classification
# -------------------------------------------------
def predicted_score(
    Soil_Moisture,
    Ambient_Temperature,
    Soil_Temperature,
    Humidity,
    Light_Intensity,
    Soil_pH,
    Nitrogen_Level,
    Phosphorus_Level,
    Potassium_Level,
    Chlorophyll_Content,
    Electrochemical_Signal
):
    temp_array = [
        Soil_Moisture, Ambient_Temperature, Soil_Temperature, Humidity,
        Light_Intensity, Soil_pH, Nitrogen_Level, Phosphorus_Level,
        Potassium_Level, Chlorophyll_Content, Electrochemical_Signal
    ]

    temp_array = np.array([temp_array])
    print("Model Input:", temp_array)

    prediction = model.predict(temp_array)[0]  # returns 0, 1, or 2
    return prediction

# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------- PREDICTION PAGE ----------------------
@app.route("/predict", methods=["GET", "POST"])
def predict():

    # if "user_id" not in session:
    #     flash("Please login to continue.", "error")
    #     return redirect(url_for("login"))

    if request.method == "POST":
        Soil_Moisture = float(request.form["Soil_Moisture"])
        Ambient_Temperature = float(request.form["Ambient_Temperature"])
        Soil_Temperature = float(request.form["Soil_Temperature"])
        Humidity = float(request.form["Humidity"])
        Light_Intensity = float(request.form["Light_Intensity"])
        Soil_pH = float(request.form["Soil_pH"])
        Nitrogen_Level = float(request.form["Nitrogen_Level"])
        Phosphorus_Level = float(request.form["Phosphorus_Level"])
        Potassium_Level = float(request.form["Potassium_Level"])
        Chlorophyll_Content = float(request.form["Chlorophyll_Content"])
        Electrochemical_Signal = float(request.form["Electrochemical_Signal"])

        prediction = predicted_score(
            Soil_Moisture,
            Ambient_Temperature,
            Soil_Temperature,
            Humidity,
            Light_Intensity,
            Soil_pH,
            Nitrogen_Level,
            Phosphorus_Level,
            Potassium_Level,
            Chlorophyll_Content,
            Electrochemical_Signal
        )

        return render_template("result.html", prediction=prediction)

    return render_template("predict.html")


# ---------------------- REGISTRATION ----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        hashed = hash_password(password)

        cursor.execute(
            "INSERT INTO user (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("registration.html")


# ---------------------- LOGIN ----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        # if user and hash_password(password) == user["password"]:
        #     session["user_id"] = user["user_id"]
        #     session["username"] = user["username"]
        #     session["email"] = user["email"]

            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------------------- LOGOUT ----------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

@app.route("/start-predict")
def start_predict():
    if "user_id" in session:
        return redirect(url_for("predict"))
    return redirect(url_for("login"))

@app.route('/about')
def about():
    return render_template('about.html')


# -------------------------------------------------
# Run App
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7002)
