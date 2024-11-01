# app/models.py
from app import db, login_manager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

class User(db.Model, UserMixin):
    # Create a table in the db
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