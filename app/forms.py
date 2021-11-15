from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, DateField, DecimalField, IntegerField, FileField, FloatField
from wtforms.fields.html5 import DateField, TimeField

from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, length, Optional
from flask_login import current_user, login_user
from app.models import User, Role
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


class AddShiftForm(FlaskForm):
    start_date = DateField('Start Date', format='%m/%d/%y', validators=[DataRequired()])
    end_date = DateField('End Date', format='%m/%d/%y', validators=[DataRequired()])
    employee_id = StringField('Employee ID', validators=[DataRequired()])

    monday_start = TimeField('Start Time',validators=[Optional()])
    monday_end = TimeField('End Time',validators=[Optional()])
    tuesday_start = TimeField('Start Time',validators=[Optional()])
    tuesday_end = TimeField('End Time',validators=[Optional()])
    wednesday_start = TimeField('Start Time',validators=[Optional()])
    wednesday_end = TimeField('End Time',validators=[Optional()])
    thursday_start = TimeField('Start Time',validators=[Optional()])
    thursday_end = TimeField('End Time',validators=[Optional()])
    friday_start = TimeField('Start Time',validators=[Optional()])
    friday_end = TimeField('End Time',validators=[Optional()])

    submit = SubmitField('Save')

class AddAppointmentForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    student_id = StringField('Student ID',)
    employee_id = StringField('Employee ID',)

    def validate_student_id(self, student_id):
        if not Function.is_valid_appointment(student_id.data, self.employee_id.data, self.start_time.data, self.end_time.data):
            raise ValidationError("The tutor is unavailable or Time Conflict")

    def validate_end_time(self, end_time):
        if end_time.data <= self.start_time.data:
            raise ValidationError("Invalid Time Range")

class AddRoleForm(FlaskForm):
    user_id = StringField('user_id',  validators=[DataRequired()])
    role_name = SelectField('user_id',  validators=[DataRequired()], choices=[('', 'Select Role'), ('tutor', 'Tutor'), ('supervisor', 'Supervisor')])
    def validate_user_id(self, user_id):
        if Role.query.filter_by(user_id=user_id.data, name=self.role_name.data).first():
            raise ValidationError("Existing role")
    
    
    
    

