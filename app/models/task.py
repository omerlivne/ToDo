# models/task.py
from app.extensions import db

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    due_date = db.Column(db.DateTime)

    # Foreign key linking to the User who authored the task
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Foreign key linking to the Group the task belongs to
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)

    def __init__(self, name, description, due_date, author_id, group_id):
        self.name = name
        self.description = description
        self.due_date = due_date
        self.author_id = author_id
        self.group_id = group_id