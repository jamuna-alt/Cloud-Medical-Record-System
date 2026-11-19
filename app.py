from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

@app.before_request
def require_login():
    allowed_routes = ["login", "static"]

    if request.endpoint not in allowed_routes:
        if not session.get("logged_in"):
            return redirect("/login")

app.secret_key = "medical_project_secret_key_change_this"

def create_table():
    conn = sqlite3.connect("medical_records.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            disease TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Demo account with hashed password
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if (username == ADMIN_USERNAME and
                check_password_hash(ADMIN_PASSWORD_HASH, password)):

            session["logged_in"] = True
            return redirect("/")

        return "Invalid username or password!"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        disease = request.form["disease"]

        conn = sqlite3.connect("medical_records.db")
        conn.execute(
            "INSERT INTO patients (name, age, gender, disease) VALUES (?, ?, ?, ?)",
            (name, age, gender, disease)
        )
        conn.commit()
        conn.close()

        return redirect("/view_patients")

    return render_template("add_patient.html")


@app.route("/doctors")
def doctors():
    return render_template("doctors.html")

@app.route("/view_doctors")
def view_doctors():
    conn = sqlite3.connect("medical_records.db")

    doctors = conn.execute(
        "SELECT * FROM doctors"
    ).fetchall()

    conn.close()

    return render_template(
        "view_doctors.html",
        doctors=doctors
    )


@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    name = request.form["name"]
    specialization = request.form["specialization"]
    phone = request.form["phone"]

    conn = sqlite3.connect("medical_records.db")

    conn.execute(
        "INSERT INTO doctors (name, specialization, phone) VALUES (?, ?, ?)",
        (name, specialization, phone)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/view_patients")
def view_patients():
    search = request.args.get("search", "")

    conn = sqlite3.connect("medical_records.db")

    patients = conn.execute(
        "SELECT * FROM patients WHERE name LIKE ?",
        ('%' + search + '%',)
    ).fetchall()

    conn.close()

    return render_template(
        "view_patients.html",
        patients=patients,
        search=search
    )


if __name__ == "__main__":
    create_table()
    app.run(debug=True)