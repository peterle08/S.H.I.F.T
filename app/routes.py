import re
from flask import render_template, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from datetime import date, datetime, timedelta
from app.classes import Fetch, Function, Insert, Update

from app.forms import LoginForm, ProfileForm, AddUserForm, WalkinForm, EmailForm, PasswordForm
from app.email import Email
from app import app
from app.models import Profile, User, Department, Student, Role, Employee


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
    if current_user.is_authorized("admin") == False: abort(403)
    deparments = Department.query.all()
    return render_template('/department/view.html', title="View Department", deparments=deparments)


#============================== Profile & User ==============================
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
# Login-required: No
# parameter: None
# Description: Request Password Reset
@app.route('/password/reset/request', methods=['GET', 'POST'])
def request_password_reset():
    notice = ""
    form = EmailForm()

    if form.validate_on_submit():
        Email.password_reset(form.email.data)
        notice = "A password reset link was sent to your email"
    return render_template('/password/request_reset.html', title="Request Password Reset", form=form, notice=notice)

#_________________________________
# Login-required: No
# parameter: None
# Description: Request Password Reset
@app.route('/password/reset/<token>',  methods=['GET', 'POST'])
def reset_password(token):
    form = PasswordForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    # validate token 
    user = User.verify_user_token(token)
    if not user: return redirect(url_for('login'))

    if form.validate_on_submit():
        Update.password(user, form.password.data)
        return redirect(url_for('login'))
    return render_template('/password/reset.html', form=form)

#_________________________________
# Login-required: yes
# parameter:
# role:
# Description: View users
@app.route('/users/view',methods=['GET', 'POST'])
@login_required
def view_user():
    if current_user.is_authorized("admin") == False: abort(403)
    users = User.query.all()
    return render_template('/user/view.html', title="View Users", users=users)

#_________________________________
# Login-required: yes
# parameter:
# role:
# Description: validate users
@app.route('/<position>/profile/validate/<email>/<redirect_to>', methods=['GET', 'POST'])
def validate_profile(position, email, redirect_to):
    form = ProfileForm()
    profile = Fetch.profile_by_email(email)

    if request.method == "POST":    # no form validation 
        if profile == None:
            email = form.email.data
            if form.validate_on_submit():
                Insert.profile(form)
                profile = Fetch.profile_by_email(form.email.data)
                if position == "student":
                    return redirect(url_for('add_student', profile_id=profile.id, redirect_to=redirect_to))
                elif position == "employee":
                    return redirect(url_for('add_student', profile_id=profile.id, redirect_to=redirect_to))
        else:
            if position == "student":
                return redirect(url_for('add_student', profile_id=profile.id, redirect_to=redirect_to))
            elif position == "employee":
                return redirect(url_for('add_employee', profile_id=profile.id))
    return render_template('/profile/validate.html', title="Verify Profile", form=form, email=email, profile=profile)

#==============================   Student       ==============================
@app.route('/<department_id>/walkin/start',methods=['GET', 'POST'])
def start_walkin(department_id):
    form = WalkinForm()
    student = None
    profile = None
    department = Department.query.filter_by(id=department_id).first()
    if form.validate_on_submit():
        profile = Fetch.profile_by_email(form.email.data)
        if profile == None or student == None:
            return redirect(url_for('validate_profile', position="student", email=form.email.data, redirect_to="walkin"))
        student = Student.query.filter_by(profile_id=profile.id).first()
        if form.purpose.data:
            Insert.walkin(department_id, student.id, form.purpose.data, datetime.now(), "w", None)
            return redirect(url_for('start_walkin', department_id=department_id))
    return render_template('/walkin/start.html', title="Start Walkin", form=form, student=student, department=department)


#_________________________________
# Login-required: yes
# parameter: profile_id
# role: any
# Description: Add student, Add user, add role
@app.route('/<int:profile_id>/student/add/<redirect_to>',methods=['GET', 'POST'])
def add_student(profile_id, redirect_to):
    form = AddUserForm()
    departments = Department.query.all()
    student = Student.query.filter_by(profile_id=profile_id).first()
    user = Fetch.user_by_profile(profile_id)
    profile = Profile.query.filter_by(id=profile_id).first()
    if request.method == "POST":
        if user == None and form.validate_on_submit():
            password = Function.random_password()
            Insert.user(form.username.data, password, profile_id)
            user = Fetch.user_by_username(form.username.data)
            Email.new_user(form.username.data, password, profile.email, profile.first_name)
        if student == None:
            department_id = request.form.get('department_id')
            Insert.student(request.form.get('student_id'), department_id, profile_id)
        if Role.query.filter_by(user_id=user.id, name="student").first() == None:
            Insert.role(user.id, "student")
        if redirect_to == "walkin":
            return redirect(url_for('start_walkin', department_id=department_id))
    return render_template('/student/add.html', title="Add User", form=form, departments=departments, student=student, user=user)

#============================== Employee  ===================================
# Login-required: yes
# parameter:profile_id
# role: any
# Description: Add employee, Add user, add role
@app.route('/<int:profile_id>/employee/add',methods=['GET', 'POST'])
@login_required
def add_employee(profile_id):
    form = AddUserForm()
    departments = Department.query.all()
    employee = Employee.query.filter_by(profile_id=profile_id).first()
    user = Fetch.user_by_profile(profile_id)
    if request.method == "POST":
        if user == None and form.validate_on_submit():
            password = Function.random_password()
            Insert.user(form.username.data, password, profile_id)
            user = Fetch.user_by_username(form.username.data)
        if employee == None:
            Insert.employee(request.form.get('employee_id'), request.form.get('department_id'), request.form.get('wage'), profile_id)
        if Role.query.filter_by(user_id=user.id, name="employee").first() == None:
            Insert.role(user.id, "employee")
        # redirect to????
    return render_template('/employee/add.html', title="Add User", form=form, departments=departments, employee=employee, user=user)

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

