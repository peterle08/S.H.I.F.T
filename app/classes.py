# Created & Developed by ...
# Copyright 2021

from app.models import User, Profile, Setting, Role
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
