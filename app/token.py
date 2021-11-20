
import jwt
from time import time
from app import app


def generate_email_confirm_token(email, expires_in):
    return jwt.encode({'reset_password': email, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

def verify_email_confirm_token(token):
    try:
        email = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
    except:
        return
    return email