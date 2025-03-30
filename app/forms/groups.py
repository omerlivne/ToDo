# forms/groups.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Regexp

class GroupForm(FlaskForm):
    """Validates group creation. Ensures name format."""
    name = StringField("Name", validators=[
        DataRequired(),
        Regexp(r"^[A-Za-z0-9 ]{3,50}$", message="Name: 3-50 alphanumeric characters and spaces.")
    ])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Create Group")

class GroupEditForm(GroupForm):
    """Validates group edits. Reuses the same rules as GroupForm."""
    submit = SubmitField("Update Group")