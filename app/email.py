from flask_mail import Message
from flask import render_template
from app import mail, app
from threading import Thread

class Email:
    def new_user(username, password, email, first_name):
        try:
            msg = Message(subject='Welcome To S.H.I.F.T',
                            sender = "support@vnsboard.com",
                            recipients=[email]
                        )
            msg.body = "Hi " + first_name + ",\nYour Account Information:\username: " + username + "\nPassword: " + password
            mail.send(msg)
        except:
            pass