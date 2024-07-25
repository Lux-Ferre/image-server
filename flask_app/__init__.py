from dotenv import load_dotenv
from flask import Flask

from config import Config

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

from flask_app import views
