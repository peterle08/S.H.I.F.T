from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, DateField, DecimalField, IntegerField, FileField, FloatField

from wtforms.validators import InputRequired, DataRequired, ValidationError, Email, EqualTo, length
from flask_login import current_user, login_user
from app.models import Role
from app.classes import Fetch

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def validate_username(self, username):
        user = Fetch.user_by_username(username.data)
        if user and user.check_password(self.password.data):
            if user.status != "inactive":
                login_user(user, remember=self.remember_me.data)
            else:
                ValidationError('Sorry, Your account has been terminated! Please contact the Admin to get more information')
        else:
            raise ValidationError('Invalid username or password! Please try again!')
