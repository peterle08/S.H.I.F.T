from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config

# Create app
app = Flask(__name__)

# configure apps
app.config.from_object(Config)

# Create Mail
mail = Mail(app)

db= SQLAlchemy(app)   # connect database

# flask_login manager
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import routes, models, errors

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)