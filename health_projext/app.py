from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from models.customer import create_new_user_web
from utils.database import customer_collection

import os


app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "temporary-secret-key"
)


# =====================================
# HOME
# =====================================

@app.route("/")
def home():
    return redirect(url_for("login"))


# =====================================
# LOGIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    if not email:
        flash(
            "Please enter your email.",
            "error"
        )

        return redirect(url_for("login"))

    customer = customer_collection.find_one(
        {"email": email}
    )

    if customer:

        session["customer"] = {
            "Patient_id": customer.get("Patient_id"),
            "Name": customer.get("Name"),
            "email": customer.get("email")
        }

        return redirect(
            url_for("dashboard")
        )

    flash(
        "No user found with this email. Please register.",
        "error"
    )

    return redirect(
        url_for(
            "register_user",
            email=email
        )
    )


# =====================================
# REGISTER
# =====================================

@app.route("/register", methods=["GET", "POST"])
def register_user():

    if request.method == "GET":

        email = request.args.get(
            "email",
            ""
        )

        return render_template(
            "register.html",
            email=email
        )

    name = request.form.get("name", "")
    email = request.form.get("email", "")
    contact_number = request.form.get(
        "contact_number",
        ""
    )
    gender = request.form.get("gender", "")
    age = request.form.get("age", "")
    pincode = request.form.get("pincode", "")

    try:

        patient_id = create_new_user_web(
            name=name,
            email=email,
            contact_number=contact_number,
            gender=gender,
            age=age,
            pincode=pincode
        )

        flash(
            f"Registration successful! "
            f"Patient ID: {patient_id}",
            "success"
        )

        return redirect(
            url_for("login")
        )

    except ValueError as error:

        flash(
            str(error),
            "error"
        )

        return redirect(
            url_for("register_user")
        )

    except Exception as error:

        print(
            "Registration error:",
            error
        )

        flash(
            "Something went wrong during registration.",
            "error"
        )

        return redirect(
            url_for("register_user")
        )


# =====================================
# DASHBOARD
# =====================================

@app.route("/dashboard")
def dashboard():

    if "customer" not in session:
        return redirect(
            url_for("login")
        )

    customer = session["customer"]

    return render_template(
        "dashboard.html",
        customer=customer
    )


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
def logout():

    session.pop(
        "customer",
        None
    )

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =====================================
# START FLASK
# =====================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )