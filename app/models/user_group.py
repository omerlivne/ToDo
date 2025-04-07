# models/user_group.py
from app.extensions import db

class UserGroup(db.Model):
    __tablename__ = "users_groups"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    role = db.Column(db.Integer, nullable=False, default=0)  # 0=member, 1=admin, 2=owner

    # Use string references for back_populates
    user = db.relationship('User', back_populates='user_groups')
    group = db.relationship('Group', back_populates='group_users')

    def __init__(self, user_id: int, group_id: int, role: int = 0) -> None:
        """Initialize a new UserGroup with user id and group id and role."""
        self.user_id = user_id
        self.group_id = group_id
        self.role = role