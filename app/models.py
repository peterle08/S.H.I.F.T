# created  by 
# create database here
from sqlalchemy.orm import relationship
from datetime import datetime, date, time, timedelta
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
    __tablename__ = "User"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    profile_id = db.Column(db.String(20), nullable=False)
    
    def set_password(self, password):
        return ""
    
    def verify_password(self, password):
        return ""


    # Relationship
    # employee = db.relationship("Employee", back_populates="user")