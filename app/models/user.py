# models/user.py
from flask_login import UserMixin
from app.extensions import db, bcrypt
from .group import Group
from app.models.user_group import UserGroup

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def groups(self):
        return db.session.query(Group).join(UserGroup).filter(UserGroup.user_id == self.username).all()
