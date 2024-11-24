# todo\models.py
from todo import db, login_manager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime


bcrypt = Bcrypt()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    username = db.Column(db.String(), primary_key=True)
    password_hash = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        # Use Bcrypt to hash the password before storing in the database
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        # Use Bcrypt to check the password against the stored hash
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(), nullable=False, default="Pending")
    creation_date = db.Column(db.DateTime, default=datetime.now().strftime("%m/%d/%Y %H:%M"))
    due_date = db.Column(db.DateTime, nullable=True)
    creator_username = db.Column(db.String(), db.ForeignKey('users.username'), nullable=False)

    def __init__(self, name, description, due_date, creator_username):
        self.name = name
        self.description = description
        self.due_date = due_date
        self.creator_username = creator_username