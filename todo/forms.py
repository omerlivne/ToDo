# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Regexp, ValidationError
from todo.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Regexp('^[0-9A-Za-z]{4,12}$',
                                      message="Username must be 4 to 12 characters long and contain only letters and digits")
                           ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 Regexp('^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])[0-9A-Za-z]{8,16}$',
                                        message="Password must be 8 to 16 characters long and contain at least one uppercase letter, one lowercase letter and one digit")
                             ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('That username is already taken. Please choose a different one')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')