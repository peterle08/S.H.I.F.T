
from flask_mail import Message
from flask import render_template
from app.classes import Fetch
from app import mail
from app.token import generate_email_confirm_token

class Email:
    def password_reset(email):
        profile = Fetch.profile_by_email(email)
        user = Fetch.user_by_profile(profile.id) # expired in 5 hours
        if user:
            msg = Message(  subject='S.H.I.F.T - PASSWORD RESET',
                            sender = "support@vnsboard.com",
                            recipients=[email]
                        )
            msg.html = render_template('email/password_reset.html', username=user.username, token=user.get_user_token(18000))
            mail.send(msg)

    def new_user(username, password, email):
        msg = Message(  subject='WELCOME TO S.H.I.F.T',
                        sender = "support@vnsboard.com",
                        recipients=[email]
                    )
        msg.html = render_template('email/new_account.html', username=username, password=password)
        mail.send(msg)

    def verify_email(email):
        extend_body = "S.H.I.F.T - VERIFY YOUR EMAIL"
        msg = Message(  subject='Verify Your Kent Email',
                        sender = "support@vnsboard.com",
                        recipients=[email]
                    )
        msg.html = render_template('email/verify_email.html',email=email, token=generate_email_confirm_token(email, 3600), extend_body=extend_body)
        mail.send(msg)
    
    def swap_request_to_supervisor(email):
        msg = Message(  subject='SCHEDULE SWAP REQUEST',
                sender = "support@vnsboard.com",
                recipients=[email]
            )
        msg.html = render_template('email/swap_request.html')
        try:
            mail.send(msg)
        except:
            pass
    
    def swap_request_to_accepter(email):
        msg = Message(  subject='SCHEDULE SWAP REQUEST',
                sender = "support@vnsboard.com",
                recipients=[email]
            )
        msg.html = render_template('email/swap_request.html')
        try:
            mail.send(msg)
        except:
            pass
    
    def swap_request_status(email, status):
        subject = "SWAP REQUEST - " + status
        msg = Message(  subject=subject,
                sender = "support@vnsboard.com",
                recipients=[email]
            )
        msg.html = render_template('email/swap_approval.html')
        try:
            mail.send(msg)
        except:
            pass
    
    def new_schedule_alert(employee_id):
        employee = Fetch.employee_by_id(employee_id)
        email = employee.profile.email
        subject = "SHIFT - NEW SCHEDULE"
        msg = Message(  subject=subject,
                sender = "support@vnsboard.com",
                recipients=[email]
            )
        msg.html = render_template('email/new_schedule.html', name=employee.profile.name)
        try:
            mail.send(msg)
        except:
            pass