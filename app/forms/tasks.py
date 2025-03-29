# forms/tasks.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

class TaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    due_date = DateTimeLocalField("Due Date",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        render_kw={"min": datetime.now().strftime("%Y-%m-%dT%H:%M")}
    )
    submit = SubmitField("Create Task")

class TaskEditForm(TaskForm):
    status = SelectField("Status", choices=[
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed")
    ], validators=[DataRequired()])
    submit = SubmitField("Update Task")
