# Created & Developed by ...
# Copyright 2021

from operator import and_
from os import stat_result
import string
import random
from datetime import timedelta, date, datetime
from time import time
from sqlalchemy.sql.elements import Null

from wtforms.fields.core import TimeField

from app.models import Appointment, Department, Student, User, Profile, Setting, Role, Employee, Walkin, Shift
from app import db

class Function:
    def get_started():
        user = Fetch.user_by_id(1)
        if user == None:
            user = User(username="admin", status="pending", profile_id=1)
            user.set_password("#BestShift2021")
            db.session.add(user)
            db.session.add_all([
                Profile(first_name="admin", last_name="admin", phone="0123456789", email="youremail@example.com"),
                Setting(user_id=1, mode="light"),
                Role(user_id=1, name="admin")
            ])
            db.session.commit()
    
    def validate_username(username):
        if Fetch.user_by_username(username):
            return True
        return False

    def random_password():
        return "mypass:" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 4))

    def verify_password_requirement(password):
        if password.isalnum(): return False
        map = {}    # dictionary that store valid case(s)
        for e in password:
            if e.isdigit() : map["number"] = 1
            else:
                map["alpha"] = 1
                if e.islower(): map["lower"] = 1
                else: map["upper"] = 1
        
        if len(map) < 4: return False
        return True

class Update:
    def password(user, password):   # update password
        user.set_password(password)
        db.session.commit()

    def profile(profile, form):     # update profile 
        profile.first_name = form.first_name.data
        profile.last_name = form.last_name.data
        profile.middle_name = form.middle_name.data
        profile.preferred_name = form.preferred_name.data
        profile.phone = form.phone.data
        profile.email = form.email.data
        profile.address = form.address.data
        profile.city = form.city.data
        profile.state = form.state.data
        profile.zip_code = form.zip_code.data
        db.session.commit()

class Fetch:
    def user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    def user_by_username(username):
        return User.query.filter_by(username=username).first()

    def profile_by_email(email):
        return Profile.query.filter_by(email=email).first()

    def profile_by_profileid(profileid):
        return Profile.query.filter_by(id=profileid).first()

    def user_by_profile(profile_id):
        return User.query.filter_by(profile_id=profile_id).first()

    def appointments_all():
        return db.session.query(Appointment)\
                        .join(Student, Appointment.student_id==Student.id)\
                        .join(Employee, Appointment.employee_id==Employee.id)\
                        .all()

    def shift_by_department(department_id):
        return db.session.query(Shift, Employee, Profile)\
                            .join(Employee, Shift.employee_id==Employee.id)\
                            .join(Profile, Profile.id==Employee.profile_id)\
                            .filter(Employee.department_id==department_id)\
                            .order_by(Shift.date, Shift.start_time)\
                            .all()

    def employee_by_profile(profile_id):
        return Employee.query.filter_by(profile_id=profile_id).first()

class Insert:
    def schedule(form):
        s = set()
        if(form.monday_start.data is None and form.monday_end.data is None):
            s.add(0)
        if(form.tuesday_start.data is None  and form.tuesday_end.data is None):
            s.add(1)
        if(form.wednesday_start.data is None and form.wednesday_end.data is None):
            s.add(2)
        if(form.thursday_start.data is None and form.thursday_end.data is None):
            s.add(3)
        if(form.friday_start.data is None and form.friday_end.data is None):
            s.add(4)

        startDate = form.start_date.data
        endDate = form.end_date.data
        index = startDate

        while index <= endDate:
            if(index.weekday() != 5 and index.weekday() != 6):
                shiftstart = form.monday_start.data
                shiftend = form.monday_end.data
                if(index.weekday() == 0):
                    shiftstart = form.monday_start.data
                    shiftend = form.monday_end.data
                elif(index.weekday() == 1):
                    shiftstart = form.tuesday_start.data
                    shiftend = form.tuesday_end.data
                elif(index.weekday() == 2):
                    shiftstart = form.wednesday_start.data
                    shiftend = form.wednesday_end.data
                elif(index.weekday() == 3):
                    shiftstart = form.thursday_start.data
                    shiftend = form.thursday_end.data
                elif(index.weekday() == 4):
                    shiftstart = form.friday_start.data
                    shiftend = form.friday_end.data
                i = set()
                i.add(index.weekday())
                if(s.issuperset(i) == False):
                    print(form.employee_id.data, index, shiftstart, shiftend)
                    shft = Shift(employee_id = form.employee_id.data, date=index, start_time = shiftstart, end_time = shiftend)
                    db.session.add(shft)
                    db.session.commit()
            index = index + timedelta(days=1) 
        


    def profile(form):
        stmt = Profile(first_name=form.first_name.data, last_name=form.last_name.data, middle_name=form.middle_name.data,
                        preferred_name=form.preferred_name.data, gender=form.gender.data, phone=form.phone.data, email=form.email.data,
                        address=form.address.data, city=form.city.data, state=form.state.data, zip_code=form.zip_code.data )
        db.session.add(stmt)
        db.session.commit()
    
    def user(username, password, profile_id):
        user = User(username=username, password=password, profile_id=profile_id, status="pending")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    
    def student(id, department_id, profile_id):
        db.session.add(Student(id=id, department_id=department_id, profile_id=profile_id))
        db.session.commit()

    def role(user_id, role):
        db.session.add(Role(user_id=user_id, name=role))
        db.session.commit()
    
    def employee(id, department_id, wage, profile_id):
        db.session.add(Employee(id=id, department_id=department_id, profile_id=profile_id, wage=wage))
        db.session.commit()
    
    def walkin(department_id, student_id, purpose, time_stamp, status, employee_id):
        db.session.add(Walkin(department_id=department_id, student_id=student_id, purpose=purpose,
                                time_stamp=time_stamp, status=status, employee_id=employee_id
                        ))
        db.session.commit()
    
    