from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from datetime import datetime, timedelta, timezone
import time

# from app.forms import LoginForm
from app.email import Email
from app import app

@app.route('/')
@app.route('/home')
def index():
    return "home - muahahahahahaah"

@app.route('/login', methods=['GET', 'POST'])
def login():

    return render_template('/user/login.html', year=datetime.now().year)