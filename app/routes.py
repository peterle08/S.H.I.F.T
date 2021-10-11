from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

import json

from datetime import datetime, timedelta
from app.classes import Function

from app.forms import LoginForm
from app.email import Email
from app import app


#_________________________________
# Login-required: No
# parameter: None
# Description: login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard', user_id=current_user.id))
    Function.get_started()
    form = LoginForm()
    if form.validate_on_submit():
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard', user_id=current_user.id)
        return redirect(next_page)
    return render_template('/user/login.html', title="Log In", year=datetime.now().year, form=form)
#_________________________________
# Login-required: No
# parameter: None
# Description: logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#_________________________________
# Login-required: yes
# parameter:
# Description: dashboard
@app.route('/<user_id>/dashboard')
def dashboard(user_id):
    return render_template('/dashboard/main.html', title="Dashboard", year=datetime.now().year)

@app.route('/<user_id>/appointment')
def appointment(user_id):
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