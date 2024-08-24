from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Attempt to get the MONGODB_URI environment variable
mongodb_uri = os.environ.get('MONGODB_URI')

if mongodb_uri is None:
    raise ValueError("MONGODB_URI environment variable is not set. Please set it and try again.")

# If the URI doesn't include a database name, add one
if '/' not in mongodb_uri.split('/')[-1]:
    mongodb_uri += '/your_database_name'  # Replace 'your_database_name' with your actual database name

# Set up the MongoDB client with the modified URI
app.config["MONGO_URI"] = mongodb_uri
mongo = PyMongo(app)

# Now you can get the database
db = mongo.db

from app import routes