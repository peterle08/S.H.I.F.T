# Created & Developed by ...
# Copyright 2021

from os import stat_result
import string
import random
from app.models import Student, User, Profile, Setting, Role, Employee
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

class Fetch:
    def user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    def user_by_username(username):
        return User.query.filter_by(username=username).first()

    def profile_by_email(email):
        return Profile.query.filter_by(email=email).first()

class Insert:
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