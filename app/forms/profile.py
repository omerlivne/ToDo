# forms/profile.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp, Optional, EqualTo, ValidationError
from flask_login import current_user
from app.models import User

class ProfileEditForm(FlaskForm):
    """Validates profile updates. Ensures username format and password rules."""
    username = StringField("Username", validators=[
        DataRequired(),
        Regexp(r"^[0-9A-Za-z]{4,12}$", message="Username: 4-12 alphanumeric characters.")
    ])
    password = PasswordField("Password", validators=[
        Optional(),
        Regexp(r"^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])[0-9A-Za-z]{8,16}$",
               message="Password: 8-16 alphanumeric characters with 1 uppercase, 1 lowercase, and 1 digit.")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        EqualTo("password", message="Passwords must match.")
    ])
    submit = SubmitField("Update Profile")

    def validate_username(self, field) -> None:
        """Ensures new username is unique (if changed)."""
        if field.data != current_user.username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError("Username already taken. Choose another.")

