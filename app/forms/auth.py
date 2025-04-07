# forms/auth.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    """Validates registration inputs and username availability."""

    username = StringField("Username", validators=[
        DataRequired(),
        Regexp(r"^[0-9A-Za-z]{4,12}$",
               message="Username: 4-12 alphanumeric characters.")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Regexp(r"^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])[0-9A-Za-z]{8,16}$",
               message="Password: 8-16 alphanumeric characters with 1 uppercase, 1 lowercase, and 1 digit.")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo("password", message="Passwords must match.")
    ])
    submit = SubmitField("Register")

    def validate_username(self, field: StringField) -> None:
        """Check username uniqueness before database commit."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username unavailable. Choose another.")

class LoginForm(FlaskForm):
    """Validates login credential formatting."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
