
from flask import Flask
from config import Config
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object(Config)

mongo_client = MongoClient(app.config['MONGODB_URI'])
db = mongo_client.get_default_database()

from app import routes