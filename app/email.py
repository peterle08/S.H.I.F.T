
from flask_mail import Message
from flask import render_template
from app.classes import Fetch
from app import mail
from app.token import generate_email_confirm_token, verify_email_confirm_token

class Email:
    def password_reset(email):
        profile = Fetch.profile_by_email(email)
        user = Fetch.user_by_profile(profile.id) # expired in 5 hours
        if profile:
            msg = Message(  subject='PASSWORD RESET',
                            sender = "support@vnsboard.com",
                            recipients=[email]
                        )
            msg.html = render_template('email/password_reset.html', username=user.username, token=user.get_user_token(18000), extend_body="")
            try:
                mail.send(msg)
            except: 
                pass
    def new_user(username, email):
        profile = Fetch.profile_by_email(email)
        user = user = Fetch.user_by_profile(profile.id) # expired in 5 hours
        extend_body = "Welcome To S.H.I.F.T\n"
        if profile:
            msg = Message(  subject='WELCOME TO S.H.I.F.T',
                            sender = "support@vnsboard.com",
                            recipients=[email]
                        )
            msg.html = render_template('email/password_reset.html', username=username, token=user.get_user_token(256000), extend_body=extend_body)
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
        msg.html = render_template('email/swap_request.html')
        try:
            mail.send(msg)
        except:
            pass