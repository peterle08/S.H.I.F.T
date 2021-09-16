from flask_mail import Message
from flask import render_template
from app import mail, app
from threading import Thread

class Email:
    def send_password_reset(user):
        pass