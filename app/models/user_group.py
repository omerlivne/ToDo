# models/user_group.py
from app.extensions import db

class UserGroup(db.Model):

    __tablename__ = "users_groups"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    admin = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, group_id, admin=False):
        self.user_id = user_id
        self.group_id = group_id
        self.admin = admin