import os

from pymongo import MongoClient
from dotenv import load_dotenv


# Load .env file
load_dotenv()


# Get MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError(
        "MONGO_URI is missing. Check your .env file."
    )


# Connect to MongoDB
client = MongoClient(MONGO_URI)


# Select database
db = client["Health_status_shower"]


# Select Customer collection
customer_collection = db["Customer"]