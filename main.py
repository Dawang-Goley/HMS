import os
import random
import uuid
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, session, url_for

# ------------------ APP CONFIG ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "hospital_secret_key"

# ------------------ EMAIL CONFIG ------------------
# USE GMAIL APP PASSWORD

EMAIL_ADDRESS = "yourgmail@gmail.com"
EMAIL_PASSWORD = "your_16_digit_app_password"

# ------------------ DUMMY USERS ------------------

users = {
    "admin": {"password": "admin123", "role": "admin"},
    "doctor1": {"password": "doc123", "role": "doctor"},
    "patient1": {"password": "pat123", "role": "patient"}
}

appointments = []

# ------------------ HOME ------------------

@app.route("/")
def home():
    return render_template("home.html")

# =================================================
# ================ PATIENT MODULE =================
# =================================================

@app.route("/patient/signup", methods=["GET", "POST"])
def patient_signup():
    if request.method == "POST":
        email = request.form["email"]
        otp = str(random.randint(100000, 999999))

        session["otp"] = otp
        session["email"] = email
        session["role"] = "patient"

        send_otp_email(email, otp)
        return redirect(url_for("patient_verify_otp"))

    return render_template("patient_signup.html")

@app.route("/patient/verify-otp", methods=["GET", "POST"])
def patient_verify_otp():
    msg = ""
    if request.method == "POST":
        if request.form["otp"] == session.get("otp"):
            session.pop("otp", None)
            return redirect(url_for("patient_login"))
        else:
            msg = "Invalid OTP"

    return render_template("patient_verify_otp.html", msg=msg)

@app.route("/patient/login", methods=["GET", "POST"])
def patient_login():
    msg = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # demo logic (replace with DB later)
        if email == "patient@gmail.com" and password == "1234":
            return redirect("/patient")
        else:
            msg = "Invalid login details"

    return render_template("patient_login.html", msg=msg)

@app.route("/patient/register", methods=["GET", "POST"])
def patient_register():
    if request.method == "POST":
        # Later: save to database / OTP verification
        return redirect("/patient/login")

    return render_template("patient_register.html")

@app.route("/patient/dashboard", methods=["GET", "POST"])
def patient_dashboard():
    if session.get("role") != "patient":
        return redirect(url_for("patient_login"))

    msg = ""
    if request.method == "POST":
        appointments.append({
            "patient": session["user"],
            "doctor": request.form["doctor"]
        })
        msg = "Appointment booked successfully"

    doctors = [u for u in users if users[u]["role"] == "doctor"]
    patient_appointments = [a for a in appointments if a["patient"] == session["user"]]

    return render_template(
        "patient_dashboard.html",
        doctors=doctors,
        appointments=patient_appointments,
        msg=msg
    )

# =================================================
# ================ DOCTOR MODULE ==================
# =================================================

@app.route("/doctor/login", methods=["GET", "POST"])
def doctor_login():
    error = ""

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # TEMP doctor credentials
        if email == "doctor@gmail.com" and password == "doc123":
            session["user"] = email          # REQUIRED
            session["role"] = "doctor"       # REQUIRED
            return redirect(url_for("doctor_dashboard"))

        error = "Invalid email or password"

    return render_template("doctor_login.html", error=error)





@app.route("/doctor/dashboard")
def doctor_dashboard():
    if "user" not in session or session.get("role") != "doctor":
        return redirect(url_for("doctor_login"))

    doctor_name = session["user"]
    doctor_appointments = [
        a for a in appointments if a["doctor"] == doctor_name
    ]

    return render_template(
        "doctor_dashboard.html",
        appointments=doctor_appointments
    )



# =================================================
# ================= ADMIN MODULE ==================
# =================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin@gmail.com" and password == "admin123":
            session["user"] = "admin"
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))

        msg = "Invalid credentials"

    return render_template("admin_login.html", msg=msg)


@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    return render_template("admin_dashboard.html", users=users, appointments=appointments)

# ------------------ LOGOUT ------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ------------------ EMAIL FUNCTION ------------------

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg.set_content(f"Your OTP for HMS signup is: {otp}")
    msg["Subject"] = "HMS Email Verification"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)
