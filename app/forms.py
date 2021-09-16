from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, DateField, DecimalField, IntegerField, FileField, FloatField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, DataRequired, ValidationError, Email, EqualTo, length
from flask_login import current_user


