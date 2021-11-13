# created  by 

from enum import unique
from datetime import datetime, date, timedelta
from time import time
import jwt  # password reset token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import app, db, login_manager

#********************************* load user ******************************
@login_manager.user_loader
def load_user(id):
    if id is not None:
        return User.query.get(id)
    return None

class User(UserMixin, db.Model):
    __tablename__ = "user"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    
    # relationship
    role = db.relationship("Role", back_populates="user")
    setting = db.relationship("Setting", back_populates="user",  uselist=False)
    profile = db.relationship("Profile", back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password,password)

    # verify role
    def is_authorized(self, roles):
        for r in roles:
            if Role.query.filter_by(user_id=self.id, name=r).first():
                return True
        return False

    # create and verify user token
    def get_user_token(self, expires_in):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_user_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format([self.id, self.username, self.status])

class Role(UserMixin, db.Model):
    __tablename__ = "role"
    # Columns
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(25))

    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'name'),)


    # relationship
    user = db.relationship("User", back_populates="role")

    def __repr__(self):
        return '<Role {}>'.format([self.user_id, self.name])

class Setting(UserMixin, db.Model):
    __tablename__ = "setting"
    # Columns
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    mode = db.Column(db.String(25))

    # Relationship
    user = db.relationship("User", back_populates="setting")

    def __repr__(self):
        return '<Setting {}>'.format([self.user_id, self.mode, self.status])

class Profile(UserMixin, db.Model):
    __tablename__ = "profile"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    preferred_name = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(10))
    zip_code = db.Column(db.String(5))
    
    # relationship
    employee = db.relationship("Employee", back_populates="profile", uselist=False)
    student = db.relationship("Student", back_populates="profile", uselist=False)
    user = db.relationship("User", back_populates="profile", uselist=False)

    def __repr__(self):
        return '<Profile {}>'.format([self.id, self.first_name, self.last_name, self.phone, self.email])
    
###########################################
#========== Tutor Support System ==========
class Student(UserMixin, db.Model):
    __tablename__ = "student"

    id = db.Column(db.String(15), primary_key=True)
    department_id = db.Column(db.String(15), db.ForeignKey('department.id'))
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))

    # relationship
    profile = db.relationship("Profile", back_populates="student")
    department = db.relationship("Department", back_populates="student")
    # tutor = db.relationship("Tutor", back_populates="student")
    appointment = db.relationship("Appointment", back_populates="student")
    walkin = db.relationship("Walkin", back_populates="student")

    def __repr__(self):
        return '<Student {}>'.format([self.id, self.department_id, self.profile_id])

class Appointment(UserMixin, db.Model):
    __tablename__ = "appointment"

    date = db.Column(db.Date(), nullable=False)
    start_time = db.Column(db.Time(), index=True, nullable=False)
    end_time = db.Column(db.Time(), index=True)
    status = db.Column(db.String(10), nullable=False)
    # constraints
    student_id = db.Column(db.String(15),  db.ForeignKey('student.id'))
    employee_id = db.Column(db.String(15), db.ForeignKey('employee.id'))
    __table_args__ = (db.PrimaryKeyConstraint('student_id', 'date', 'start_time'),)

    # relationship
    student = db.relationship("Student", back_populates="appointment")
    employee = db.relationship("Employee", back_populates="appointment")

    def get_student_profile(self):
        profile_id = Student.query.get(self.student_id).profile_id
        return Profile.query.get(profile_id)

    def get_employee_profile(self):
        profile_id = Employee.query.get(self.employee_id).profile_id
        return Profile.query.get(profile_id)

    def __repr__(self):
        return '<Appointment {}>'.format([self.student_id, self.date, self.start_time])

class Walkin(UserMixin, db.Model):
    __tablename__ = "walkin"

    purpose = db.Column(db.String(100), nullable=False)
    time_stamp = db.Column(db.DateTime(), index=True, nullable=False)
    status = db.Column(db.String(10), nullable=False)

    #constraints
    student_id = db.Column(db.String(15),  db.ForeignKey('student.id'), nullable=True)
    employee_id = db.Column(db.String(15), db.ForeignKey('employee.id'))
    department_id = db.Column(db.String(15), db.ForeignKey('department.id'))
    __table_args__ = (db.PrimaryKeyConstraint('time_stamp', 'department_id'),)
    
    # relationship
    student = db.relationship("Student", back_populates="walkin")
    employee = db.relationship("Employee", back_populates="walkin")
    department = db.relationship("Department", back_populates="walkin")

    def __repr__(self):
        return '<Walkin {}>'.format([self.student_id, self.date, self.start_time])

class Course(UserMixin, db.Model):
    __tablename__ = "course"
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # relationship
    tutor = db.relationship("Tutor", back_populates="course")
    def __repr__(self):
        return '<Course {}>'.format([self.id, self.name])

###########################################
#========== Employee System ==========
class Tutor(UserMixin, db.Model):
    __tablename__ = "tutor"

    employee_id = db.Column(db.String(15), db.ForeignKey('employee.id'))
    course_id = db.Column(db.String(15), db.ForeignKey('course.id')) 

    __table_args__ = (db.PrimaryKeyConstraint('employee_id', 'course_id',),)

    # relationships
    employee = db.relationship("Employee", back_populates="tutor")
    course = db.relationship("Course", back_populates="tutor")

    def __repr__(self):
        return '<Tutor {}>'.format([self.employee_id, self.course_id])

class Department(UserMixin, db.Model):
    __tablename__ = "department"
    
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100))
    location = db.Column(db.String(100))

    # relationships
    walkin = db.relationship("Walkin", back_populates="department")
    employee = db.relationship("Employee", back_populates="department")
    student = db.relationship("Student", back_populates="department")

    def __repr__(self):
        return '<Department {}>'.format([self.id, self.name, self.building])

class Employee(UserMixin, db.Model):
    __tablename__ = "employee"

    id = db.Column(db.String(15), primary_key=True)
    wage = db.Column(db.Numeric(10,2))
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id')) 
    department_id = db.Column(db.String(15), db.ForeignKey('department.id'))
    
    #Relationships
    profile = db.relationship("Profile", back_populates="employee", uselist=False)
    appointment = db.relationship("Appointment", back_populates="employee")
    walkin = db.relationship("Walkin", back_populates="employee")
    department = db.relationship("Department", back_populates="employee")
    supervisor = db.relationship("Supervisor", back_populates="employee")
    supervise = db.relationship("Supervise", back_populates="employee")
    tutor = db.relationship("Tutor", back_populates="employee")
    limit = db.relationship("Limit", back_populates="employee")
    shift = db.relationship("Shift", back_populates="employee")
    swap = db.relationship("Swap", back_populates="employee")

    def __repr__(self):
        return '<Employee {}>'.format([self.id, self.profile_id, self.department_id])

class Supervise(UserMixin, db.Model):
    __tablename__ = "supervise"

    supervisor_id = db.Column(db.String(15), db.ForeignKey('supervisor.id'))
    employee_id = db.Column(db.String(15), db.ForeignKey('employee.id'))

    __table_args__ = (db.PrimaryKeyConstraint('supervisor_id', 'employee_id'),)

    # relationship
    employee = db.relationship("Employee", back_populates="supervise")
    supervisor = db.relationship("Supervisor", back_populates="supervise")

    def __repr__(self):
        return '<Supervise {}>'.format([self.supervisor_id, self.employee_id])

class Supervisor(UserMixin, db.Model):
    __tablename__ = "supervisor"

    id = db.Column(db.String(15), db.ForeignKey('employee.id'), primary_key=True)
    # relationship
    employee = db.relationship("Employee", back_populates="supervisor")
    supervise = db.relationship("Supervise", back_populates="supervisor")

    def __repr__(self):
        return '<Supervisor {}>'.format([self.id])

class Limit(UserMixin, db.Model):
    __tablename__ = "limit"

    employee_id = db.Column(db.String(15), db.ForeignKey('employee.id'), primary_key=True)
    weekly_hours = db.Column(db.Numeric(10,2))
    # relationship
    employee = db.relationship("Employee", back_populates="limit")

    def __repr__(self):
        return '<Limit {}>'.format([self.employee_id])

###########################################
#========== Employee System ==========
class Shift(UserMixin, db.Model):
    __tablename__ = "shift"

    employee_id = db.Column(db.String(15), db.ForeignKey('employee.id'))
    date = db.Column(db.Date(), nullable=False)
    start_time = db.Column(db.Time(), index=True, nullable=False)
    end_time = db.Column(db.Time())
    status = db.Column(db.String(10), )
    # constraints
    __table_args__ = (db.PrimaryKeyConstraint('employee_id', 'date', 'start_time'),)

    # relationship
    employee = db.relationship("Employee", back_populates="shift")

    def __repr__(self):
        return '<Shift {}>'.format([self.employee_id, self.date, self.start_time, self.end_time, self.status])

class Swap(UserMixin, db.Model):
    __tablename__ = "swap"

    requester_id = db.Column(db.String(15), db.ForeignKey('employee.id'))
    accepter_id = db.Column(db.String(15))
    from_date = db.Column(db.Date(), index=True, nullable=False)
    from_time = db.Column(db.Time(), nullable=False)
    to_date = db.Column(db.Date(), nullable=False)
    to_time = db.Column(db.Time(), nullable=False)
    status = db.Column(db.String(10))
    # constraints
    __table_args__ = (db.PrimaryKeyConstraint('requester_id', 'accepter_id', 'from_date', 'from_time', 'to_date', 'to_time'),)

    # relationship
    employee = db.relationship("Employee", back_populates="swap")

    def __repr__(self):
        return '<Swap {}>'.format([self.requester_id, self.accepter_id, self.from_date, self.from_time, self.to_date, self.to_time])