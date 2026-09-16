from datetime import datetime
import re

from utils.database import customer_collection


def generate_patient_id():
    """Generate a new Patient ID such as PAT001."""

    customers = customer_collection.find(
        {"Patient_id": {"$regex": r"^PAT\d+$"}}
    )

    highest_number = 0

    for customer in customers:
        patient_id = customer.get("Patient_id", "")

        try:
            number = int(patient_id.replace("PAT", ""))

            if number > highest_number:
                highest_number = number

        except ValueError:
            continue

    return f"PAT{highest_number + 1:03d}"


def validate_customer(
    name,
    email,
    contact_number,
    gender,
    age,
    pincode
):
    """Validate registration information."""

    name = name.strip()
    email = email.strip().lower()
    contact_number = contact_number.strip()
    gender = gender.strip()
    pincode = pincode.strip()

    if not name:
        raise ValueError("Name cannot be empty.")

    if not re.match(
        r"^[\w\.-]+@[\w\.-]+\.\w+$",
        email
    ):
        raise ValueError("Invalid email format.")

    if not re.match(
        r"^\d{10}$",
        contact_number
    ):
        raise ValueError(
            "Contact number must contain exactly 10 digits."
        )

    if not gender:
        raise ValueError("Please select gender.")

    try:
        age = int(age)
    except (ValueError, TypeError):
        raise ValueError("Age must be a number.")

    if not (0 <= age <= 120):
        raise ValueError(
            "Age must be between 0 and 120."
        )

    if not re.match(
        r"^\d{6}$",
        pincode
    ):
        raise ValueError(
            "Pincode must contain exactly 6 digits."
        )

    return {
        "name": name,
        "email": email,
        "contact_number": contact_number,
        "gender": gender,
        "age": age,
        "pincode": pincode
    }


def create_new_user_web(
    name,
    email,
    contact_number,
    gender,
    age,
    pincode
):
    """Create a new customer or update an existing one."""

    data = validate_customer(
        name,
        email,
        contact_number,
        gender,
        age,
        pincode
    )

    name = data["name"]
    email = data["email"]
    contact_number = data["contact_number"]
    gender = data["gender"]
    age = data["age"]
    pincode = data["pincode"]

    # Check if customer already exists
    existing = customer_collection.find_one(
        {"email": email}
    )

    # Existing customer
    if existing:

        patient_id = existing["Patient_id"]

        customer_collection.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "Name": name,
                    "contact_number": contact_number,
                    "Gender": gender,
                    "Age": age,
                    "pincode": pincode,
                    "update_date": datetime.now()
                }
            }
        )

        return patient_id

    # New customer
    patient_id = generate_patient_id()

    user_data = {
        "Patient_id": patient_id,
        "Name": name,
        "email": email,
        "contact_number": contact_number,
        "Gender": gender,
        "Age": age,
        "pincode": pincode,
        "current_date": datetime.now(),
        "update_date": None
    }

    customer_collection.insert_one(user_data)

    return patient_id