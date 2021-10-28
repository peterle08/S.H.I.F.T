from flask_login.utils import confirm_login
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, DateField, DecimalField, IntegerField, FileField, FloatField

from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, length
from flask_login import current_user, login_user
from app.models import User
from app.classes import Fetch, Function

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

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name')
    preferred_name = StringField('Preferred Name')
    gender =  SelectField("Gender",  validators=[DataRequired()], choices=[('m', 'Male'), ('f', 'Female'), ('o', 'others')])
    phone = StringField('Phone Number', validators=[DataRequired(), length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[DataRequired(), length(min=5, max=5)])

    def validate_email(self, email):
        if Fetch.profile_by_email(email.data):
            raise ValidationError("Existing Email | Profile")

    def validate_phone(self, phone):
        if (phone.data).isnumeric() == False:
            raise ValidationError("Number only")

class AddUserForm(FlaskForm):
    # need modified
    username = StringField('Username', validators=[DataRequired()], render_kw={'autofocus': True})

    def validate_username(self, username):
        user = Fetch.user_by_username(username.data)
        if user:
            raise ValidationError('Existing username')

class WalkinForm(FlaskForm):
    # need modified
    email = StringField('Username', validators=[DataRequired(), Email()], render_kw={'autofocus': True})
    purpose = StringField('Purpose',)

class EmailForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired(), Email()], render_kw={'autofocus': True})

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), length(min=10)])
    confirm_password =  PasswordField('Password', validators=[DataRequired(), length(min=10), EqualTo('password')])

    def validate_password(self, password):
        if Function.verify_password_requirement(password.data) == False:
            raise ValidationError('The password must contain at least: 1 number, 1 upper case, 1 lower case & 1 special character')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name')
    preferred_name = StringField('Preferred Name')
    gender =  SelectField("Gender",  validators=[DataRequired()], choices=[('m', 'Male'), ('f', 'Female'), ('o', 'others')])
    phone = StringField('Phone Number', validators=[DataRequired(), length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])  # store current or new email address
    current_email = StringField('Email', validators=[DataRequired(), Email()]) # store current email address
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[DataRequired(), length(min=5, max=5)])

    submit = SubmitField('Save')

    def validate_email(self, email):
        if email.data != self.current_email.data:
            if Fetch.profile_by_email(email.data):
                raise ValidationError("Existing Email")

    def validate_phone(self, phone):
        if (phone.data).isnumeric() == False:
            raise ValidationError("Number only")