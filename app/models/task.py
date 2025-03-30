# models/task.py
from app.extensions import db

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending")
    due_date = db.Column(db.DateTime)
    author = db.Column(db.String(12), db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)

    def __init__(self, name, description, due_date, author, group_id):
        self.name = name
        self.description = description
        self.due_date = due_date
        self.author = author
        self.group_id = group_id
