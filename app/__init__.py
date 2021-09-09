from flask import Flask
from config import Config


# Create app
app = Flask(__name__)

# configure apps
app.config.from_object(Config)


from app import routes, models
