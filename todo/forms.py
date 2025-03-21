# todo\forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeLocalField, SelectField
from wtforms.validators import DataRequired, EqualTo, Regexp, ValidationError, Optional
from todo.models import User
from datetime import datetime

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

class ProfileEditForm(FlaskForm):
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Regexp('^[0-9A-Za-z]{4,12}$',
                                      message="Username must be 4 to 12 characters long and contain only letters and digits")
                           ])
    password = PasswordField('New Password',
                             validators=[
                                 Optional(),
                                 Regexp('^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])[0-9A-Za-z]{8,16}$',
                                        message="Password must be 8 to 16 characters long and contain at least one uppercase letter, one lowercase letter and one digit")
                             ])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password')])
    submit = SubmitField('Update Profile')

    def __init__(self, original_username, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('That username is already taken. Please choose a different one')

class GroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Create Group')

class GroupEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Update Group')

class TaskForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    due_date = DateTimeLocalField('Due Date',
        validators=[Optional()],
        format='%Y-%m-%dT%H:%M',
        render_kw={'min': datetime.now().strftime('%Y-%m-%dT%H:%M')}
    )
    submit = SubmitField('Create Task')

    def validate_due_date(self, field):
        if field.data and field.data < datetime.now():
            raise ValidationError("Due date cannot be in the past")

class TaskEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    due_date = DateTimeLocalField('Due Date',
        validators=[Optional()],
        format='%Y-%m-%dT%H:%M',
        render_kw={'min': datetime.now().strftime('%Y-%m-%dT%H:%M')}
    )
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Task')

    def validate_due_date(self, field):
        if field.data and field.data < datetime.now():
            raise ValidationError("Due date cannot be in the past")

