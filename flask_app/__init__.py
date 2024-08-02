import os

from dotenv import load_dotenv
from flask import Flask
from flask_image_resizer import Images

from config import Config
from repo import SQLiteDB

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv('SECRET_KEY')

if not app.secret_key:
	raise ValueError("No secret key provided.")

images = Images(app)

with SQLiteDB(app.config["DB_PATH"]) as db:
	db.init_db()

from flask_app.views import read
from flask_app.views import upload
from flask_app.views import errors
