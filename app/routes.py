import re
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from datetime import datetime, timedelta
from app.classes import Fetch, Function, Insert

from app.forms import LoginForm, ProfileForm, AddUserForm
from app.email import Email
from app import app
from app.models import User, Department


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
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('/dashboard/main.html', title="Dashboard", year=datetime.now().year)

#============================== Department =================================
# Login-required: yes
# parameter:
# role:
# Description: View Department
@app.route('/departments/view')
def view_department():
    if current_user.is_authorized("admin") == False: return 404
    deparments = Department.query.all()
    return render_template('/department/view.html', title="View Department", deparments=deparments)


#============================== Profile & User ==============================

# Login-required: yes
# parameter:
# role:
# Description: Add Employee
@app.route('/profile/validate', methods=['GET', 'POST'])
@login_required
def validate_profile():
    if current_user.is_authorized("admin") == False: return 404
    form = ProfileForm()
    profile = None
    email = None
    if request.method == "POST":    # no form validation 
        profile = Fetch.profile_by_email(form.email.data)
        if profile == None:
            email = form.email.data
            if form.validate_on_submit():
                Insert.profile(form)
                profile = Fetch.profile_by_email(form.email.data)
                return redirect(url_for('add_user', profile_id=profile.id))
        else:
            return redirect(url_for('add_user', profile_id=profile.id))

    return render_template('/profile/validate.html', title="Verify Profile", form=form, email=email)

#_________________________________
# Login-required: yes
# parameter:
# role:
# Description: Add Employee
@app.route('/<profile_id>/user/add',methods=['GET', 'POST'])
@login_required
def add_user(profile_id):
    if current_user.is_authorized("admin") == False: return 404
    form = AddUserForm()
    
    return render_template('/user/add.html', title="Add User", form=form)


#_________________________________
# Login-required: yes
# parameter:
# role:
# Description: Add Employee
@app.route('/users/view',methods=['GET', 'POST'])
@login_required
def view_user():
    if current_user.is_authorized("admin") == False: return 404
    users = User.query.all()
    return render_template('/user/view.html', title="View Users", users=users)

#============================== Student  ===================================

#_________________________________
# Login-required: yes
# parameter:
# Description: view Appointment
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

