# Created & Developed by ...
# Copyright 2021

from app.models import User, Profile, Setting, Role
from app import db

class Function:
    def get_started():
        user = Fetch.user_by_id(1)
        user.set_password("#BestShift2021")
        db.session.commit()
        # if user == None:
        #     user = User(username="admin", status="pending", profile_id=1)
        #     user.set_password(user.password)
        #     db.session.add(user)
        #     db.session.add_all([
        #         Profile(first_name="admin", last_name="admin", phone="0123456789", email="youremail@example.com"),
        #         Setting(user_id=1, mode="light"),
        #         Role(user_id=1, name="admin")
        #     ])
        #     db.session.commit()

class Fetch:
    def user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()
    def user_by_username(username):
        return User.query.filter_by(username=username).first()