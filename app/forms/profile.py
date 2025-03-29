# forms/profile.py
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp, Optional, EqualTo, ValidationError
from app.models import User

class ProfileEditForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Regexp('^[0-9A-Za-z]{4,12}$',
               message="Username rules: 4-12 chars, letters/numbers only")
    ])
    password = PasswordField("New Password", validators=[
        Optional(),
        Regexp('^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])[0-9A-Za-z]{8,16}$',
              message="Password rules: 8-16 chars, 1 uppercase, 1 lowercase, 1 digit, letters/numbers only")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        Optional(), EqualTo("password")
    ])
    submit = SubmitField("Update Profile")

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError("Username already taken")

