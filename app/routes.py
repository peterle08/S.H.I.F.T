import re
from flask import render_template, redirect, url_for, request, json, abort
from flask_login import current_user, logout_user, login_required
from sqlalchemy.sql.elements import Null
from werkzeug.urls import url_parse

from datetime import date, datetime, timedelta

from app.classes import Fetch, Function, Insert, Update

from app.forms import LoginForm, ProfileForm, AddUserForm, WalkinForm, EmailForm, PasswordForm, EditProfileForm,\
                        AddShiftForm, AddAppointmentForm
from app.email import Email
from app import app
from app.models import Appointment, Course, Profile, Tutor, User, Department, Student, Role, Employee

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
    if current_user.is_authorized(['admin']) == False: abort(403)
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
    if current_user.is_authorized(['admin']) == False: abort(403)
    users = User.query.all()
    return render_template('/user/view.html', title="View Users", users=users)

#_________________________________
# Login-required: yes
# parameter:
# role:
# Description: View Personal Profile, Update profile on form validation
@app.route('/profile/view',methods=['GET', 'POST'])
@login_required
def view_profile():
    form = EditProfileForm()
    profile = Fetch.profile_by_profileid(current_user.profile_id)
    if form.validate_on_submit():
        Update.profile(profile, form)
    return render_template('/profile/view.html', title="Profile Page", form=form, user=current_user, profile=profile)

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
#_________________________________
# Login-required: yes (student do not required to login)
# parameter:
# role:
# Description: if existing student -> checkin, else: redirect to validate profile
@app.route('/<department_id>/walkin/start',methods=['GET', 'POST'])
@login_required
def start_walkin(department_id):
    form = WalkinForm()
    student = None
    profile = None
    department = Department.query.filter_by(id=department_id).first()
    if form.validate_on_submit():
        profile = Fetch.profile_by_email(form.email.data)
        if profile == None:
            return redirect(url_for('validate_profile', position="student", email=form.email.data, redirect_to="walkin"))
        else:
            student = Student.query.filter_by(profile_id=profile.id).first()
            if student == None:
                return redirect(url_for('validate_profile', position="student", email=form.email.data, redirect_to="walkin"))
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
        elif redirect_to == "signup":
            pass # redirect  login??????
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
# role: admin, supervisor
# Description: View employee list
@app.route('/employees/view',methods=['GET', 'POST'])
@login_required
def view_employees():
    form = AddShiftForm()
    if current_user.is_authorized(['admin', 'supervisor']) == False: abort(403)
    employees = Employee.query.all()  
    if form.validate_on_submit():
        Insert.schedule(form)
        return redirect(url_for('view_employees'))
    return render_template('/employee/view.html', title="View Employees", employees=employees, form=form)


#============================== Calendar  ===================================
# Login-required: yes
# parameter:
# Description: view shift - monthly
@app.route('/tutor/availability/<student_id>', methods=['GET', 'POST'])
@login_required
def tutor_availability(student_id):
    if not current_user.is_authorized(['student', 'supervisor']): abort(403)
    if current_user.is_authorized(['student']):
        student_id = current_user.profile.student.id

    form = AddAppointmentForm()
    selected_options = {'department_id': None, 'course_id': None}
    departments = Department.query.all()
    courses = Course.query.all()
    shift_list = []
    if request.method == "POST":
        # get department & course
        selected_options['department_id'] = request.form.get('department_id')
        selected_options['course_id'] = request.form.get('course_id')
        # get tutor availability
        shift_list = Fetch.tutor_availability(selected_options['department_id'], selected_options['course_id'])
        if form.employee_id.data and form.validate_on_submit():
            Insert.appointment(form)
            return redirect(url_for('appointments'))
    # shifts & events
    shifts =  []
    events = []
    index = 0
    for shift in shift_list:
        if (shift.Profile.preferred_name):
            employee_name = shift.Profile.preferred_name
        else: 
            employee_name = shift.Profile.first_name
        events.append(
            {
                'id' : str(index),
                'title' : employee_name,
                'start' : str(datetime.combine(shift.Shift.date, shift.Shift.start_time)),
                'end' :  str(datetime.combine(shift.Shift.date, shift.Shift.end_time)),
                'classNames': [ 'btn', 'btn-info' ],
            }
        )
        shifts.append(
            {
                "employeeId": shift.Employee.id,
                "employeeName":  employee_name,
                "employeeEmail": shift.Profile.email,
                "date": str(shift.Shift.date),
                "start": str(shift.Shift.start_time),
                "end": str(shift.Shift.end_time),
                "status": shift.Shift.status
            }
        )
        index += 1 # increase event_id
    return render_template('appointment/availability.html', title="Tutor Availability", form=form, events=events, shifts=shifts,
                        selected_options=selected_options, departments=departments, courses=courses, student_id=student_id)

# Login-required: yes
# parameter:
# Description: View & Edit appointment(s)
@app.route('/appointments')
@login_required
def appointments():
    if current_user.is_authorized(['supervisor']):
        appointments = Appointment.query.all()
    elif current_user.is_authorized(['student']):
        appointments = Appointment.query.filter_by(student_id=current_user.profile.student.id).all()
    appointments_dict = [] # map
    events = []
    index = 0
    for appointment in appointments:
        events.append(
            {
                'id' : str(index),
                'title' : appointment.get_student_profile().first_name,
                'start' : str(datetime.combine(appointment.date, appointment.start_time)),
                'end' :  str(datetime.combine(appointment.date, appointment.end_time)),
            }
        )
        appointments_dict.append(
            {
                "studentId": appointment.student_id,
                "studentName":  appointment.get_student_profile().first_name,
                "employeeId": appointment.employee_id,
                "employeeName": appointment.get_employee_profile().first_name,
                "date": str(appointment.date),
                "start": str(appointment.start_time),
                "end": str(appointment.end_time)
            }
        )
        index += 1
    return render_template('appointment/view.html', title="Appointments - Student Support", mycal=events, appointments_list=appointments_dict)

#_________________________________
# Login-required: yes
# parameter:
# Description: view shift - monthly
@app.route('/shift/all')
@login_required
def shift_all():
    if current_user.is_authorized(['employee']) == False: abort(403)
    employee = Fetch.employee_by_profile(current_user.profile_id)
    shift_list = Fetch.shift_by_department(employee.department_id)
    shifts =  []
    events = []
    index = 0
    for shift in shift_list:
        if (shift.Profile.preferred_name):
            employee_name = shift.Profile.preferred_name
        else: 
            employee_name = shift.Profile.first_name
        events.append(
            {
                'id' : str(index),
                'title' : employee_name, #+ " at " + str(shift.Shift.start_time),
                'start' : str(datetime.combine(shift.Shift.date, shift.Shift.start_time)),
                'end' :  str(datetime.combine(shift.Shift.date, shift.Shift.end_time)),
                'classNames': [ 'btn', 'btn-info' ],
            }
        )
        # save shift to array of map 
        shifts.append(
            {
                "employeeId": shift.Employee.id,
                "employeeName":  employee_name,
                "date": shift.Shift.date,
                "start": str(shift.Shift.start_time),
                "end": str(shift.Shift.end_time),
                "status": shift.Shift.status
            }
        )
        index += 1 # increase event_id
    return render_template('shift/all.html', title="Shift - View All", events=events, shifts=shifts)

#_________________________________
# Login-required: yes
# parameter:
# Description: view shift - weekly
@app.route('/shift/personal')
@login_required
def shift_personal():
    # to add time to date:  str(datetime.combine(shift.Shift.date, shift.Shift.start_time)),
    shifts =  []
    events = []
    return render_template('shift/personal.html', title="My Shift", events=events, shifts=shifts)
