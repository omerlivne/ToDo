# forms/tasks.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, ValidationError, Regexp
from datetime import datetime

class TaskForm(FlaskForm):
    name = StringField("Name", validators=[
        DataRequired(),
        Regexp(r"^[A-Za-z0-9 ]{3,50}$",
               message="Name: 3-50 alphanumeric characters and spaces.")
    ])
    description = TextAreaField('Description', validators=[Optional()])
    due_date = DateTimeLocalField('Due Date',
        validators=[Optional()],
        format='%Y-%m-%dT%H:%M',
    )
    submit = SubmitField('Create Task')

    def validate_due_date(self, field):
        if field.data and field.data < datetime.now():
            raise ValidationError("Due date cannot be in the past")

class TaskEditForm(TaskForm):
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Task')
