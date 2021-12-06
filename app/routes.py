from app.token import verify_email_confirm_token

from flask import render_template, redirect, url_for, request, json, abort
from flask_login import current_user, logout_user, login_required

from werkzeug.urls import url_parse

from datetime import date, datetime

from app.classes import Fetch, Function, Insert, Update, Delete

from app.forms import AddRoleForm, GetWalkinLinkForm, LoginForm, NewUserForm, ProfileForm, AddUserForm, RequestShiftSwapForm, WalkinForm, EmailForm, PasswordForm, EditProfileForm,\
                        AddShiftForm, AddAppointmentForm
from app.email import Email
from app import app
from app.models import Appointment, Course, Profile, Supervisor, Swap, User, Department, Student, Role, Employee, Walkin

#_________________________________
# Login-required: yes
# parameter:
# Description: dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authorized(['supervisor']) == True:
        employee = Fetch.employee_by_profile(current_user.profile.id)
        total_appointments_for_departemnt = Fetch.appointmentby_department(employee.department_id)
        totalappt = len(total_appointments_for_departemnt)
        total_walkins_by_department = Fetch.walkin_by_departmentid(employee.department_id)
        totalwalks= len(total_walkins_by_department)
        return render_template('/dashboard/main.html', title="Dashboard", year=datetime.now().year, totalappt = totalappt, totalwalks=totalwalks)
    else:
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
@app.route('/profile/validate/<email>/', methods=['GET', 'POST'])
def validate_profile(email):
    form = ProfileForm()
    profile = Fetch.profile_by_email(email)

    if request.method == "POST":    # no form validation 
        if profile == None:
            email = form.email.data
            if form.validate_on_submit():
                Insert.profile(form)
                profile = Fetch.profile_by_email(form.email.data)
                if current_user.is_authenticated:
                    return redirect(url_for('add_employee', profile_id=profile.id))
                return redirect(url_for('add_student', profile_id=profile.id))
        else:
            if current_user.is_authenticated:
                return redirect(url_for('add_employee', profile_id=profile.id))
            return redirect(url_for('add_student', profile_id=profile.id))
    return render_template('/profile/validate.html', title="Verify Profile", form=form, email=email, profile=profile)

#==============================   Student       ==============================
# Login-required: npo
# parameter:
# role:
# Description: student sign-up
@app.route('/student/verify/email',methods=['GET', 'POST'])
def student_verify_email():
    form = EmailForm()
    alert = ""
    if form.validate_on_submit():
        if form.email.data[-8:] != "kent.edu":
            alert = "Invalid Kent Email"
        else:
            Email.verify_email(form.email.data)
            alert = "We have sent the confirmation to " + form.email.data + "!\nPlease verify your email to continue to the Next Step!"
    return render_template('/student/signup.html', title="Student SignUp", form=form, alert=alert)

@app.route('/student/signup/<email>/<token>',methods=['GET', 'POST'])
def student_signup(email, token):
    if not verify_email_confirm_token(token): abort(404)

    form = NewUserForm()
    profile_form = ProfileForm()

    student = None
    user = None
    departments = Department.query.all()
    profile = Fetch.profile_by_email(email)
    if request.method == "POST":
        if profile == None:
            if profile_form.validate_on_submit():
                Insert.profile(profile_form)
                profile = Fetch.profile_by_email(profile_form.email.data)
        else:
            if user == None:
                if form.validate_on_submit():
                    Insert.user(form.username.data, form.password.data, profile.id)
                    Email.new_user(form.username.data, form.password.data, profile.email)
                    user = Fetch.user_by_username(form.username.data)
            else:
                user = User.query.filter_by(profile_id=profile.id).first()
            if student == None and user:
                department_id = request.form.get('department_id')
                Insert.student(request.form.get('student_id'), department_id, profile.id)
                if Role.query.filter_by(user_id=user.id, name="student").first() == None:
                    Insert.role(user.id, "student")
                return redirect(url_for('login'))
    if profile:
        student = Student.query.filter_by(profile_id=profile.id).first()
        user = User.query.filter_by(profile_id=profile.id).first()
    return render_template('/student/new.html', title="Student Signup", email=email, form=form, profile_form=profile_form, profile=profile,
                                     departments=departments, student=student, user=user)
#_________________________________
# Login-required: yes (student do not required to login)
# parameter:
# role:
# Description: if existing student -> checkin, else: redirect to validate profile
@app.route('/walkin/start/<department_id>',methods=['GET', 'POST'])
def start_walkin(department_id):
    ENCODED_DEPARTMENT = department_id
    department_id = Function.hex_to_string(department_id)[:-51]
    form = WalkinForm()
    student = None
    profile = None
    department = Department.query.filter_by(id=department_id).first()
    if form.validate_on_submit():
        profile = Fetch.profile_by_email(form.email.data)
        if profile == None:
            return redirect(url_for('validate_profile', email=form.email.data))
        else:
            student = Student.query.filter_by(profile_id=profile.id).first()
            if student == None:
                return redirect(url_for('validate_profile', email=form.email.data))
            if form.purpose.data:
                Insert.walkin(department_id, student.id, form.purpose.data, datetime.now(), "w", None)
                return redirect(url_for('start_walkin', department_id=ENCODED_DEPARTMENT))
    return render_template('/walkin/start.html', title="Start Walkin", form=form, student=student, department=department)

#_________________________________
# Login-required: yes
# parameter: profile_id
# role: any
# Description: Add student, Add user, add role
@app.route('/<int:profile_id>/student/add',methods=['GET', 'POST'])
def add_student(profile_id):
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
            Email.new_user(form.username.data, password, profile.email)
        if student == None:
            department_id = request.form.get('department_id')
            Insert.student(request.form.get('student_id'), department_id, profile_id)
        if Role.query.filter_by(user_id=user.id, name="student").first() == None:
            Insert.role(user.id, "student")

        return redirect(url_for('start_walkin', department_id=Function.string_to_hex((department_id + "this1saFreakingStudpidwayt0decode$$Gotokillyourself"))))

    return render_template('/student/add.html', title="Add User", form=form, departments=departments, student=student, user=user)

#============================== Employee  ===================================
# Login-required: yes
# parameter:profile_id
# role: any
# Description: Add employee, Add user, add role
@app.route('/<profile_id>/employee/add',methods=['GET', 'POST'])
@login_required
def add_employee(profile_id):
    if not current_user.is_authorized(['admin', 'supervisor']): abort(403)
    form = AddUserForm()
    employee = Employee.query.filter_by(profile_id=profile_id).first()
    user = Fetch.user_by_profile(profile_id)
    courses = Course.query.all()
    supervisors = Supervisor.query.all()

    if current_user.is_authorized(['admin']):
        departments = Department.query.all()
    else:
        departments = Department.query.filter_by(id=current_user.profile.employee.department_id).all()
    if request.method == "POST":
        employee_id = request.form.get('employee_id')
        if user == None and form.validate_on_submit():
            password = Function.random_password()
            Insert.user(form.username.data, password, profile_id)
            user = Fetch.user_by_username(form.username.data)
            Email.new_user(user.username, password, user.profile.email)
        if employee == None:
            Insert.employee(employee_id, request.form.get('department_id'), request.form.get('wage'), profile_id)
        if Role.query.filter_by(user_id=user.id, name="employee").first() == None:
            Insert.role(user.id, "employee")
            supervisor_id = request.form.get('supervisor_id')
            if supervisor_id:
                Insert.supervise(supervisor_id, employee_id)
        roles = request.form.getlist('role')
        for role in roles:
            if Role.query.filter_by(user_id=user.id, name=role).first() == None:
                Insert.role(user.id, role)
                if role == "supervisor":
                    Insert.supervisor(employee_id)
        tutor_courses = request.form.getlist('course_id')
        for course in tutor_courses:
            Insert.tutor(employee_id, course)
        return redirect(url_for('view_employees'))
    return render_template('/employee/add.html', title="Add User", form=form, departments=departments, employee=employee, 
                                        supervisors=supervisors, user=user, courses=courses)


#_________________________________
# Login-required: yes
# parameter:
# role: admin, supervisor
# Description: View employee list
@app.route('/employees/view',methods=['GET', 'POST'])
@login_required
def view_employees():
    if current_user.is_authorized(['admin', 'supervisor']) == False: abort(403)
    form = AddShiftForm()
    role_form = AddRoleForm()
    profile_form = EditProfileForm()
    if current_user.is_authorized(['supervisor']):
        employees = Fetch.employee_by_supervisor(current_user.profile.employee.id)
    else:
        employees = Employee.query.all()
    if request.method == "POST":
        if request.form.get("action") == "shift":
            if form.validate_on_submit():
                Insert.schedule(form)
                Email.new_schedule_alert(form.employee_id.data)
                employees = Employee.query.all()
                return redirect(url_for('view_employees'))
        else:
            if role_form.validate_on_submit():
                if Role.query.filter_by(user_id=role_form.user_id.data, name=role_form.user_id.data).first() == None:
                    course_id = request.form.get("course_id")
                    employee_id = request.form.get("tutor_id")
                    Insert.role(role_form.user_id.data, role_form.role_name.data)
                    if role_form.role_name.data == "tutor":
                        Insert.tutor(employee_id, course_id)
                    elif role_form.role_name.data == "supervisor":
                        Insert.supervisor(employee_id)
    courses = Course.query.all()
    return render_template('/employee/view.html', title="View Employees", employees=employees, form=form, role_form=role_form, profile_form=profile_form, courses=courses)

# Login-required: yes
# parameter:
# Description: view students
@app.route('/students/view')
def view_students():
    if current_user.is_authorized(['admin', 'supervisor']) == False: abort(403)
    students = Student.query.all()
    students_profs = []
    for student in students:
        students_profs.append( Fetch.user_by_profile(student.profile_id))
    return render_template('/student/view.html', title="View Students", students_profs=students_profs)



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
@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    if not current_user.is_authorized(['supervisor', 'student']): abort(403)
    if request.method == "POST":
        Delete.appointment(request.form.get('date'), request.form.get('start_time'), request.form.get('student_id'))

    if current_user.is_authorized(['supervisor']):
        appointments = Fetch.appointmentby_department(current_user.profile.employee.department_id)
    elif current_user.is_authorized(['student']):
        appointments = Appointment.query.filter_by(student_id=current_user.profile.student.id).all()
    elif current_user.is_authorized(['admin']):
        appointments = Appointment.query.all()
    # appointments & fc events
    appointments_dict = []
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
    if current_user.is_authorized(['supervisor']) == False: abort(403)
    employee = Fetch.employee_by_profile(current_user.profile_id)
    supervise = Fetch.supervise_by_employee(employee.id)
    shift_list = Fetch.shift_by_supervisor(supervise.supervisor_id)
    shifts =  []
    events = []
    if request.method == "POST":
        Delete.shift(request.form.get('employee_id'), request.form.get('date'), request.form.get('start_time'))
        shift_list = Fetch.shift_by_supervisor(employee.supervise.supervisor_id)
    
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
                "date": str(shift.Shift.date),
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
    if current_user.is_authorized(['employee']) == False: abort(403)
    shift_list = Fetch.shift_for_personal(current_user.profile.employee.id)
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
    return render_template('shift/personal.html', title="My Shift", events=events, shifts=shifts)

#_________________________________
# Login-required: yes
# parameter:
# Description: request a shift swap
@app.route('/shift/swap/request', methods=['GET', 'POST'])
@login_required
def request_shift_swap():
    if not current_user.is_authorized(['emplpoyee', "supervisor"]): abort(403)
    form = RequestShiftSwapForm()
    shift_list = []
    if not current_user.is_authorized(['supervisor']):
        supervisor_id = current_user.profile.employee.supervise.supervisor_id
    else:
        supervisor_id = current_user.profile.employee.id
    if request.method == "POST":
        post_for  = request.form.get('action')
        if post_for == "search":
            # filter shift
            role =  request.form.get('role')
            if role == "tutor":
                shift_list = Fetch.shift_for_swap(supervisor_id, role)
            elif role == "assistant":
                shift_list = Fetch.shift_for_swap(supervisor_id, role)
            elif role == "all":
                shift_list = Fetch.shift_by_supervisor(supervisor_id)
            # shift_list = Fetch.shift_by_department("0006") # remove this line for testing purpose
        else:
            if form.validate_on_submit():
                supervisor = Employee.query.filter_by(id=supervisor_id).first()
                Insert.swap_request(form)
                Email.swap_request_to_supervisor(supervisor.profile.email)
                if form.accepter_id.data:
                    accepter = Employee.query.filter_by(id=form.accepter_id.data).first()
                    Email.swap_request_to_accepter(accepter.profile.email)

    # save schedule
    shifts =  []
    events = []
    index = 0
    for shift in shift_list:
        if (shift.Profile.preferred_name):
            employee_name = shift.Profile.preferred_name
        else: 
            employee_name = shift.Profile.first_name + shift.Profile.last_name
        events.append(
            {
                'id' : str(index),
                'title' : employee_name,
                'start' : str(datetime.combine(shift.Shift.date, shift.Shift.start_time)),
                'end' :  str(datetime.combine(shift.Shift.date, shift.Shift.end_time)),
            }
        )
        # save shift to array of map 
        shifts.append(
            {
                "employeeId": shift.Employee.id,
                "employeeName":  employee_name,
                "date": str(shift.Shift.date),
                "start": str(shift.Shift.start_time),
                "end": str(shift.Shift.end_time),
                "status": shift.Shift.status,
                "email": shift.Profile.email,
                "phone": shift.Profile.phone,
            }
        )
        index += 1 # increase event_id

    return render_template('shift/swap_request.html', title="Request Shift Swap", form=form, events=events, shifts=shifts)

#_________________________________
# Login-required: yes
# parameter:
# Description: request a shift swap
@app.route('/shift/swap/view', methods=['GET', 'POST'])
@login_required
def view_swap_request():
    if not current_user.is_authorized(['employee']): abort(403)
    if current_user.is_authorized(['supervisor']):
        swaps = Fetch.swap_request_by_supervisor(current_user.profile.employee.id)
    else:
        swaps = Swap.query.filter_by(requester_id=current_user.profile.employee.id, status="pending").all()
    # swaps = Swap.query.all() # for testing
    if request.method == "POST":
        for_action = request.form.get('action')
        index = int(request.form.get('index'))
        if for_action == "accept":
            Update.swap_status(swaps[index], "accepted")
            Email.swap_request_status("Accepted by the Employee and is Waiting for Supervisor's Approval")
        elif for_action == "approve":
            # swap shift
            Function.swap_shift(swaps[index])
            # update swap request
            Update.swap_status(swaps[index], "approved")
            # email new update on swap request 
            Email.swap_request_status( swaps[index].employee.profile.email, "Approved by Supervisor")
            email = Employee.query.filter_by(id=swaps[index].accepter_id).first().profile.email
            Email.swap_request_status(email, "Approved by Supervisor")
        elif for_action == "deny":
            Update.swap_status(swaps[index], "approved")
            Email.swap_request_status("Denied")
    if current_user.is_authorized(['supervisor']):
        swaps = Fetch.swap_request_by_supervisor(current_user.profile.employee.id)
    else:
        swaps = Swap.query.filter_by(requester_id=current_user.profile.employee.id, status="pending").all()
    my_swaps = Swap.query.filter_by(accepter_id=current_user.profile.employee.id).all()
    return render_template('shift/swap_request_view.html', title="Request Shift Swap", swaps=swaps, my_swaps=my_swaps)
#============================== Walkin  ===================================
# Login-required: yes
# Role: assistant & supervisor
# parameter:
# Description: view walkin/dropin
@app.route('/walkin', methods=['GET', 'POST'])
@login_required
def view_walkin():
    if current_user.is_authorized(['assistant', 'supervisor']) == False: abort(403)
    picked_date = date.today()
    # drop-in by department_id
    department_id = current_user.profile.employee.department_id
    walkin = Walkin.query.filter_by(department_id=department_id, status="w").order_by(Walkin.time_stamp).all()
    if request.method == "POST":
        action = request.form.get('action')
        if action == "search":
            picked_date = request.form.get("date")
            walkin = Fetch.walkin_search(department_id, picked_date)
        else:
            index = int(request.form.get('index')) - 1
            Update.walkin_status(walkin[index], "d")
            walkin = Walkin.query.filter_by(department_id=department_id, status="w").order_by(Walkin.time_stamp).all()
    return render_template('walkin/view.html', title="Walkin", walkin=walkin, picked_date=picked_date)

# Login-required: yes
# Role: assistant & supervisor
# parameter:
# Description: view walkin/dropin
@app.route('/go/walkin', methods=['GET', 'POST'])
def get_walkin_link():
    form = GetWalkinLinkForm()
    departments = Department.query.all()
    if form.validate_on_submit():
        encoded_department = Function.string_to_hex((request.form.get('department_id')) + "this1saFreakingStudpidwayt0decode$$Gotokillyourself")
        return redirect(url_for('start_walkin', department_id=encoded_department))

    return render_template('walkin/get_link.html', title="Walkin", form=form, departments=departments)