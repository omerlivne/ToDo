# forms/auth.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp, EqualTo, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Regexp("^[0-9A-Za-z]{4,12}$",
               message="Username rules: 4-12 chars, letters/numbers only")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Regexp("^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])[0-9A-Za-z]{8,16}$",
               message="Password rules: 8-16 chars, 1 uppercase, 1 lowercase, 1 digit, letters/numbers only")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password")
    ])
    submit = SubmitField("Register")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

