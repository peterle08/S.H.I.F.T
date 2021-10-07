from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

import json

from datetime import datetime, timedelta, timezone

# from app.forms import LoginForm
from app.email import Email
from app import app


@app.route('/')
@app.route('/home')
def index():
    return "Home <h1><b>muahahahahahaah</b></h1>"

@app.route('/cal')
def appointment():
    events = [
        {
            'title' : 'Employee 1',
            'start' : '2021-10-05',
            'end' : '2021-10-05'
        },
        {
            'title' : 'Employee 2',
            'start' : '2021-09-24',
            'end' : '2021-09-25'
        },
        {
            'title' : 'Employee 3',
            'start' : '2021-09-25',
            'end' : '2021-09-25'
        },
    ]
    return render_template('calendar/appointment.html', title="Appointment", mycal=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('/user/login.html', title="Log In", year=datetime.now().year)